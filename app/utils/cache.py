"""
Sistema de caché simple en memoria para optimizar performance.
"""
from functools import wraps
from datetime import datetime, timedelta
import time

# Caché global en memoria
_cache = {}
_cache_timestamps = {}

def cache_with_ttl(ttl_seconds=300):
    """
    Decorator para cachear resultados de funciones con TTL (Time To Live).
    
    Args:
        ttl_seconds: Tiempo de vida del caché en segundos (default 5 minutos)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Crear clave única basada en función y argumentos
            cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
            
            current_time = time.time()
            
            # Verificar si existe en caché y no ha expirado
            if cache_key in _cache and cache_key in _cache_timestamps:
                cached_time = _cache_timestamps[cache_key]
                if current_time - cached_time < ttl_seconds:
                    # print(f"✅ Cache HIT: {func.__name__}")
                    return _cache[cache_key]
            
            # Si no está en caché o expiró, ejecutar función
            # print(f"❌ Cache MISS: {func.__name__}")
            result = func(*args, **kwargs)
            
            # Guardar en caché
            _cache[cache_key] = result
            _cache_timestamps[cache_key] = current_time
            
            return result
        
        return wrapper
    return decorator


def clear_cache():
    """Limpia todo el caché"""
    global _cache, _cache_timestamps
    _cache.clear()
    _cache_timestamps.clear()
    return {"status": "cache_cleared", "timestamp": datetime.now().isoformat()}


def get_cache_stats():
    """Obtiene estadísticas del caché"""
    current_time = time.time()
    valid_entries = sum(
        1 for key, timestamp in _cache_timestamps.items()
        if current_time - timestamp < 300  # Asumiendo TTL de 5 min
    )
    
    return {
        "total_entries": len(_cache),
        "valid_entries": valid_entries,
        "expired_entries": len(_cache) - valid_entries,
        "timestamp": datetime.now().isoformat()
    }
