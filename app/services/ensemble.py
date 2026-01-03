import pandas as pd
import numpy as np
from typing import Dict, Tuple

def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """RSI: mide sobreventa (< 30) / sobrecompra (> 70)"""
    # Convertir a valores numéricos explícitamente
    data_clean = pd.to_numeric(data, errors='coerce')
    delta = data_clean.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)  # Valor neutral para NaN

def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series]:
    """MACD: momentum e histograma"""
    ema_fast = data.ewm(span=fast).mean()
    ema_slow = data.ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    return macd_line, signal_line

def calculate_bollinger_bands(data: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Bollinger Bands: volatilidad y límites"""
    sma = data.rolling(window=period).mean()
    std = data.rolling(window=period).std()
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return upper, sma, lower

def ensemble_signal(row: Dict) -> Dict:
    """
    Vota entre 4 indicadores y devuelve:
    - recommendation: BUY / SELL / HOLD (consenso)
    - confidence: 0..1 (% de indicadores de acuerdo)
    - reason: explicación legible
    """
    votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
    reasons = []

    # Helper para obtener valores seguros
    def get_val(key):
        val = row.get(key)
        if val is None:
            return None
        if isinstance(val, (int, float)):
            return val
        if hasattr(val, 'item'):
            return val.item()
        return val

    sma20 = get_val("sma20")
    sma50 = get_val("sma50")
    rsi = get_val("rsi")
    macd = get_val("macd")
    macd_signal = get_val("macd_signal")
    bb_upper = get_val("bb_upper")
    bb_lower = get_val("bb_lower")
    close = get_val("close")

    # 1. SMA Crossover (SMA20 vs SMA50)
    if sma20 is not None and sma50 is not None:
        if sma20 > sma50:
            votes["BUY"] += 1
            reasons.append("SMA20 > SMA50")
        elif sma20 < sma50:
            votes["SELL"] += 1
            reasons.append("SMA20 < SMA50")
        else:
            votes["HOLD"] += 1
            reasons.append("SMA neutral")
    else:
        votes["HOLD"] += 1
        reasons.append("SMA: insufficient data")

    # 2. RSI (sobreventa/sobrecompra)
    if rsi is not None:
        if rsi < 30:
            votes["BUY"] += 1
            reasons.append(f"RSI oversold ({rsi:.1f})")
        elif rsi > 70:
            votes["SELL"] += 1
            reasons.append(f"RSI overbought ({rsi:.1f})")
        else:
            votes["HOLD"] += 1
            reasons.append(f"RSI neutral ({rsi:.1f})")
    else:
        votes["HOLD"] += 1
        reasons.append("RSI: insufficient data")

    # 3. MACD (momentum)
    if macd is not None and macd_signal is not None:
        if macd > macd_signal:
            votes["BUY"] += 1
            reasons.append("MACD bullish cross")
        elif macd < macd_signal:
            votes["SELL"] += 1
            reasons.append("MACD bearish cross")
        else:
            votes["HOLD"] += 1
            reasons.append("MACD neutral")
    else:
        votes["HOLD"] += 1
        reasons.append("MACD: insufficient data")

    # 4. Bollinger Bands (precio en extremos)
    if bb_upper is not None and bb_lower is not None and close is not None:
        if close < bb_lower:
            votes["BUY"] += 1
            reasons.append("Price < BB lower (oversold)")
        elif close > bb_upper:
            votes["SELL"] += 1
            reasons.append("Price > BB upper (overbought)")
        else:
            votes["HOLD"] += 1
            reasons.append("Price within BB bands")
    else:
        votes["HOLD"] += 1
        reasons.append("BB: insufficient data")

    # Consenso
    total_votes = sum(votes.values())
    max_vote = max(votes.values())
    confidence = max_vote / total_votes if total_votes > 0 else 0.5
    
    recommendation = max(votes.keys(), key=lambda k: votes[k])
    
    return {
        "recommendation": recommendation,
        "confidence": round(float(confidence), 2),
        "reason": " | ".join(reasons),
        "votes": votes
    }