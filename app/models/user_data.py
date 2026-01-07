"""
Modelos de datos para favoritos y alertas de precios.
Usa SQLite para persistencia simple.
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Ruta de la base de datos
DB_PATH = Path(__file__).parent.parent.parent / "data" / "user_data.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def init_db():
    """Inicializa la base de datos con las tablas necesarias"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla de favoritos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL DEFAULT 'default',
            symbol TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, symbol)
        )
    """)
    
    # Tabla de alertas de precio
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL DEFAULT 'default',
            symbol TEXT NOT NULL,
            condition TEXT NOT NULL,  -- 'above' o 'below'
            target_price REAL NOT NULL,
            current_price REAL,
            notification_type TEXT NOT NULL,  -- 'popup', 'email', 'both'
            email TEXT,
            is_active BOOLEAN DEFAULT 1,
            triggered BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            triggered_at TIMESTAMP
        )
    """)
    
    # Tabla de historial de búsquedas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL DEFAULT 'default',
            symbol TEXT NOT NULL,
            searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Índices para mejor performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_favorites_user ON favorites(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_user ON price_alerts(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_active ON price_alerts(is_active, triggered)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_user ON search_history(user_id)")
    
    conn.commit()
    conn.close()


# ==================== FAVORITOS ====================

def add_favorite(symbol: str, user_id: str = "default") -> Dict:
    """Añade un símbolo a favoritos (máximo 10)"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar límite de 10 favoritos
        cursor.execute(
            "SELECT COUNT(*) FROM favorites WHERE user_id = ?",
            (user_id,)
        )
        count = cursor.fetchone()[0]
        
        if count >= 10:
            # Eliminar el más antiguo para hacer espacio
            cursor.execute(
                "DELETE FROM favorites WHERE id IN (SELECT id FROM favorites WHERE user_id = ? ORDER BY added_at ASC LIMIT 1)",
                (user_id,)
            )
        
        cursor.execute(
            "INSERT INTO favorites (user_id, symbol) VALUES (?, ?)",
            (user_id, symbol.upper())
        )
        conn.commit()
        return {"status": "added", "symbol": symbol.upper(), "id": cursor.lastrowid}
    except sqlite3.IntegrityError:
        return {"status": "already_exists", "symbol": symbol.upper()}
    finally:
        conn.close()


def remove_favorite(symbol: str, user_id: str = "default") -> Dict:
    """Elimina un símbolo de favoritos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "DELETE FROM favorites WHERE user_id = ? AND symbol = ?",
        (user_id, symbol.upper())
    )
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    if deleted > 0:
        return {"status": "removed", "symbol": symbol.upper()}
    else:
        return {"status": "not_found", "symbol": symbol.upper()}


def get_favorites(user_id: str = "default") -> List[Dict]:
    """Obtiene todos los favoritos de un usuario"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, symbol, added_at FROM favorites WHERE user_id = ? ORDER BY added_at DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {"id": row[0], "symbol": row[1], "added_at": row[2]}
        for row in rows
    ]


def is_favorite(symbol: str, user_id: str = "default") -> bool:
    """Verifica si un símbolo está en favoritos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT COUNT(*) FROM favorites WHERE user_id = ? AND symbol = ?",
        (user_id, symbol.upper())
    )
    count = cursor.fetchone()[0]
    conn.close()
    
    return count > 0


# ==================== ALERTAS ====================

def create_alert(
    symbol: str,
    condition: str,  # 'above' o 'below'
    target_price: float,
    notification_type: str = "popup",  # 'popup', 'email', 'both'
    email: Optional[str] = None,
    user_id: str = "default"
) -> Dict:
    """Crea una nueva alerta de precio"""
    init_db()
    
    if condition not in ['above', 'below']:
        raise ValueError("condition debe ser 'above' o 'below'")
    
    if notification_type not in ['popup', 'email', 'both']:
        raise ValueError("notification_type debe ser 'popup', 'email' o 'both'")
    
    if notification_type in ['email', 'both'] and not email:
        raise ValueError("email es requerido para notificaciones por email")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO price_alerts 
        (user_id, symbol, condition, target_price, notification_type, email)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, symbol.upper(), condition, target_price, notification_type, email))
    
    alert_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "id": alert_id,
        "symbol": symbol.upper(),
        "condition": condition,
        "target_price": target_price,
        "notification_type": notification_type,
        "status": "created"
    }


def get_alerts(user_id: str = "default", active_only: bool = True) -> List[Dict]:
    """Obtiene todas las alertas de un usuario"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if active_only:
        cursor.execute(
            "SELECT * FROM price_alerts WHERE user_id = ? AND is_active = 1 ORDER BY created_at DESC",
            (user_id,)
        )
    else:
        cursor.execute(
            "SELECT * FROM price_alerts WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def delete_alert(alert_id: int, user_id: str = "default") -> Dict:
    """Elimina una alerta"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "DELETE FROM price_alerts WHERE id = ? AND user_id = ?",
        (alert_id, user_id)
    )
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    if deleted > 0:
        return {"status": "deleted", "alert_id": alert_id}
    else:
        return {"status": "not_found", "alert_id": alert_id}


def update_alert_status(alert_id: int, is_active: bool) -> Dict:
    """Activa o desactiva una alerta"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE price_alerts SET is_active = ? WHERE id = ?",
        (1 if is_active else 0, alert_id)
    )
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    
    if updated > 0:
        return {"status": "updated", "alert_id": alert_id, "is_active": is_active}
    else:
        return {"status": "not_found", "alert_id": alert_id}


def trigger_alert(alert_id: int, current_price: float) -> Dict:
    """Marca una alerta como activada"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE price_alerts 
        SET triggered = 1, triggered_at = CURRENT_TIMESTAMP, current_price = ?
        WHERE id = ?
    """, (current_price, alert_id))
    
    conn.commit()
    conn.close()
    
    return {"status": "triggered", "alert_id": alert_id, "price": current_price}


def check_alerts_for_symbol(symbol: str, current_price: float) -> List[Dict]:
    """
    Verifica si alguna alerta debe activarse para un símbolo dado.
    Retorna lista de alertas que deben notificarse.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtener alertas activas para este símbolo
    cursor.execute("""
        SELECT * FROM price_alerts 
        WHERE symbol = ? AND is_active = 1 AND triggered = 0
    """, (symbol.upper(),))
    
    alerts = cursor.fetchall()
    triggered_alerts = []
    
    for alert in alerts:
        alert_dict = dict(alert)
        condition = alert_dict['condition']
        target_price = alert_dict['target_price']
        
        should_trigger = False
        
        if condition == 'above' and current_price >= target_price:
            should_trigger = True
        elif condition == 'below' and current_price <= target_price:
            should_trigger = True
        
        if should_trigger:
            # Marcar como activada
            trigger_alert(alert_dict['id'], current_price)
            alert_dict['current_price'] = current_price
            triggered_alerts.append(alert_dict)
    
    conn.close()
    return triggered_alerts


# ==================== HISTORIAL DE BÚSQUEDAS ====================

def add_to_history(symbol: str, user_id: str = "default") -> Dict:
    """Añade un símbolo al historial de búsquedas (últimos 10)"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Añadir al historial
        cursor.execute(
            "INSERT INTO search_history (user_id, symbol) VALUES (?, ?)",
            (user_id, symbol.upper())
        )
        
        # Mantener solo los últimos 10 registros por usuario
        cursor.execute("""
            DELETE FROM search_history 
            WHERE id NOT IN (
                SELECT id FROM search_history 
                WHERE user_id = ? 
                ORDER BY searched_at DESC 
                LIMIT 10
            ) AND user_id = ?
        """, (user_id, user_id))
        
        conn.commit()
        return {"status": "added", "symbol": symbol.upper()}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()


def get_search_history(user_id: str = "default") -> List[Dict]:
    """Obtiene el historial de búsquedas (últimos 10, sin duplicados consecutivos)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT symbol, MAX(searched_at) as last_search
        FROM search_history 
        WHERE user_id = ? 
        GROUP BY symbol
        ORDER BY last_search DESC 
        LIMIT 10
    """, (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {"symbol": row[0], "last_searched": row[1]}
        for row in rows
    ]


def clear_search_history(user_id: str = "default") -> Dict:
    """Limpia todo el historial de búsquedas de un usuario"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "DELETE FROM search_history WHERE user_id = ?",
        (user_id,)
    )
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    return {"status": "cleared", "deleted_count": deleted}


def get_all_active_alerts() -> List[Dict]:
    """
    Obtiene todas las alertas activas (no disparadas) de todos los usuarios.
    Útil para verificación periódica por el scheduler.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM price_alerts 
        WHERE is_active = 1 AND triggered = 0
        ORDER BY symbol
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# Inicializar DB al importar
init_db()
