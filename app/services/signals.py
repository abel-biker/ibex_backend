from typing import List, Dict, Optional
import pandas as pd
import numpy as np
import warnings
from app.data_providers.market_data import get_daily_data
from app.services.ensemble import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands, ensemble_signal
)

# Suprimir FutureWarnings de pandas
warnings.filterwarnings('ignore', category=FutureWarning)

def _safe_float(x: Optional[object], default: Optional[float] = None) -> Optional[float]:
    try:
        if x is None:
            return default
        if pd.isna(x):
            return default
        if hasattr(x, "item"):
            val = x.item()
            if pd.isna(val):
                return default
            return float(val)
        if isinstance(x, (int, float)):
            if pd.isna(x):
                return default
            return float(x)
        return float(x)
    except Exception:
        return default

def _safe_int(x: Optional[object], default: Optional[int] = None) -> Optional[int]:
    try:
        if x is None:
            return default
        if pd.isna(x):
            return default
        if hasattr(x, "item"):
            val = x.item()
            if pd.isna(val):
                return default
            return int(float(val))
        if isinstance(x, (int, float)):
            if pd.isna(x):
                return default
            return int(float(x))
        return int(float(x))
    except Exception:
        return default

def _safe_round(x: Optional[float], decimals: int = 2) -> Optional[float]:
    """Redondea de forma segura, devuelve None si x es None"""
    if x is None:
        return None
    try:
        return round(float(x), decimals)
    except (TypeError, ValueError):
        return None

def compute_signals(symbol: str, limit: int = 30, order: str = "desc", interval: str = "1d", period: str = "1y") -> List[Dict]:
    precios = get_daily_data(symbol, interval=interval, period=period)
    if not precios:
        return []

    df = pd.DataFrame(precios)
    df["fecha"] = pd.to_datetime(df["fecha"])

    # Calcular en orden cronológico
    df = df.sort_values("fecha", ascending=True).reset_index(drop=True)
    
    # Indicadores
    df["pct_change"] = df["close"].pct_change(periods=1).fillna(0) * 100
    
    # Convertir a numpy arrays para evitar Series y FutureWarnings
    df["sma20"] = pd.Series(df["close"].rolling(window=20).mean().values, index=df.index)
    df["sma50"] = pd.Series(df["close"].rolling(window=50).mean().values, index=df.index)
    
    rsi_vals = calculate_rsi(df["close"], period=14)
    df["rsi"] = pd.Series(rsi_vals.values if hasattr(rsi_vals, 'values') else rsi_vals, index=df.index)
    
    macd_result = calculate_macd(df["close"])
    df["macd"] = pd.Series(macd_result[0].values if hasattr(macd_result[0], 'values') else macd_result[0], index=df.index)
    df["macd_signal"] = pd.Series(macd_result[1].values if hasattr(macd_result[1], 'values') else macd_result[1], index=df.index)
    
    bb_result = calculate_bollinger_bands(df["close"])
    df["bb_upper"] = pd.Series(bb_result[0].values if hasattr(bb_result[0], 'values') else bb_result[0], index=df.index)
    df["bb_middle"] = pd.Series(bb_result[1].values if hasattr(bb_result[1], 'values') else bb_result[1], index=df.index)
    df["bb_lower"] = pd.Series(bb_result[2].values if hasattr(bb_result[2], 'values') else bb_result[2], index=df.index)

    # Orden de salida
    if order == "asc":
        out_df = df.sort_values("fecha", ascending=True).reset_index(drop=True)
    else:
        out_df = df.sort_values("fecha", ascending=False).reset_index(drop=True)

    if limit:
        out_df = out_df.head(limit)

    out = []
    # Convertir DataFrame a lista de diccionarios de una vez
    records = out_df.to_dict('records')
    
    for record in records:
        # Convertir timestamp a string
        if isinstance(record.get("fecha"), pd.Timestamp):
            # Preservar hora para intervalos intradiarios
            if interval in ["1m", "5m", "15m", "30m", "1h", "90m"]:
                fecha_str = record["fecha"].strftime("%Y-%m-%d %H:%M:%S")
            else:
                fecha_str = record["fecha"].strftime("%Y-%m-%d")
        else:
            fecha_str = str(record.get("fecha", ""))
        
        # Limpiar valores NaN y convertir tipos numpy
        clean_record = {}
        for key, val in record.items():
            # Evitar problemas con Series
            if isinstance(val, (pd.Series, np.ndarray)):
                clean_record[key] = None
            elif val is None:
                clean_record[key] = None
            elif isinstance(val, pd.Timestamp):
                clean_record[key] = val
            elif isinstance(val, (np.integer, np.floating)):
                clean_record[key] = float(val) if isinstance(val, np.floating) else int(val)
            else:
                # Chequear NaN solo para tipos escalares
                try:
                    if pd.isna(val):
                        clean_record[key] = None
                    else:
                        clean_record[key] = val
                except (TypeError, ValueError):
                    clean_record[key] = val
        
        signal_data = ensemble_signal(clean_record)

        out.append({
            "fecha": fecha_str,
            "open": _safe_float(clean_record.get("open")),
            "high": _safe_float(clean_record.get("high")),
            "low": _safe_float(clean_record.get("low")),
            "close": _safe_float(clean_record.get("close")),
            "volume": _safe_int(clean_record.get("volume"), 0) or 0,
            "pct_change": _safe_round(_safe_float(clean_record.get("pct_change")), 4),
            # Indicadores (None cuando no hay valor)
            "sma20": _safe_round(_safe_float(clean_record.get("sma20")), 2),
            "sma50": _safe_round(_safe_float(clean_record.get("sma50")), 2),
            "rsi": _safe_round(_safe_float(clean_record.get("rsi")), 2),
            "macd": _safe_round(_safe_float(clean_record.get("macd")), 6),
            "macd_signal": _safe_round(_safe_float(clean_record.get("macd_signal")), 6),
            "bb_upper": _safe_round(_safe_float(clean_record.get("bb_upper")), 2),
            "bb_lower": _safe_round(_safe_float(clean_record.get("bb_lower")), 2),
            # Señal final
            "recommendation": signal_data.get("recommendation"),
            "confidence": float(signal_data.get("confidence") or 0.0),
            "reason": signal_data.get("reason"),
            "votes": signal_data.get("votes")
        })
    
    return out