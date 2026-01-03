from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import pandas as pd

from app.data_providers.market_data import get_daily_data
from app.services.signals import compute_signals
from app.services.formatter import format_signal, generate_html_dashboard
from app.data_providers.ibex35_symbols import (
    IBEX_35_SYMBOLS, get_all_symbols, get_symbols_by_sector, 
    get_company_info, SECTORS
)
from app.scoring.danelfin_score import calculate_danelfin_score
from app.ea.expert_advisors import (
    RSI_EA, MACD_EA, MA_Crossover_EA, Bollinger_EA, Ensemble_EA, 
    EAConfig, SignalType
)

app = FastAPI(
    title="IBEX 35 Trading API",
    description="API tipo Danelfin con Expert Advisors para IBEX 35 - Optimizado para Android",
    version="2.0.0"
)

# CORS para permitir acceso desde apps móviles
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "ok",
        "api": "IBEX 35 Trading API",
        "version": "2.0.0",
        "features": [
            "Scoring tipo Danelfin (0-10)",
            "Expert Advisors (RSI, MACD, MA Crossover, Bollinger, Ensemble)",
            "Backtesting de estrategias",
            "35 empresas del IBEX 35",
            "Optimizado para Android"
        ]
    }


# ==================== ENDPOINTS MÓVIL OPTIMIZADOS ====================

@app.get("/api/v1/ibex35/ranking")
def get_ibex35_ranking(
    limit: int = Query(35, ge=1, le=35),
    sector: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None, ge=0, le=10)
):
    """
    📱 MÓVIL: Ranking completo del IBEX 35 con scores Danelfin.
    Retorna lista ordenada por score de mayor a menor.
    
    Parámetros:
    - limit: Número de empresas (default 35)
    - sector: Filtrar por sector (Financiero, Energía, etc.)
    - min_score: Score mínimo (0-10)
    """
    symbols = get_all_symbols()
    if sector:
        symbols = get_symbols_by_sector(sector)
    
    results = []
    for symbol in symbols:
        try:
            # Obtener datos
            data_raw = get_daily_data(symbol)
            if not data_raw or len(data_raw) < 50:
                continue
            
            df = pd.DataFrame(data_raw)
            df["fecha"] = pd.to_datetime(df["fecha"])
            df = df.sort_values("fecha", ascending=True).reset_index(drop=True)
            
            # Calcular indicadores (rápido)
            df["sma_20"] = df["close"].rolling(window=20).mean()
            df["sma_50"] = df["close"].rolling(window=50).mean()
            
            from app.services.ensemble import calculate_rsi, calculate_macd, calculate_bollinger_bands
            df["rsi"] = calculate_rsi(df["close"])
            macd_vals = calculate_macd(df["close"])
            df["macd"] = macd_vals[0]
            df["macd_signal"] = macd_vals[1]
            bb_vals = calculate_bollinger_bands(df["close"])
            df["bb_upper"] = bb_vals[0]
            df["bb_middle"] = bb_vals[1]
            df["bb_lower"] = bb_vals[2]
            
            # Calcular score Danelfin
            score_data = calculate_danelfin_score(df)
            
            company_info = get_company_info(symbol)
            latest = df.iloc[-1]
            
            results.append({
                "symbol": symbol,
                "name": company_info["name"],
                "sector": company_info["sector"],
                "score": score_data["total_score"],
                "rating": score_data["rating"],
                "confidence": score_data["confidence"],
                "price": round(float(latest["close"]), 2),
                "change_pct": round((float(latest["close"]) / float(df.iloc[-2]["close"]) - 1) * 100, 2) if len(df) > 1 else 0,
                "technical_score": score_data["technical_score"],
                "momentum_score": score_data["momentum_score"],
                "sentiment_score": score_data["sentiment_score"],
            })
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            continue
    
    # Ordenar por score
    results.sort(key=lambda x: x["score"], reverse=True)
    
    # Filtrar por score mínimo
    if min_score is not None:
        results = [r for r in results if r["score"] >= min_score]
    
    return {
        "total": len(results),
        "sector_filter": sector,
        "min_score_filter": min_score,
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ranking": results[:limit]
    }


@app.get("/api/v1/stock/{symbol}/score")
def get_stock_score(symbol: str):
    """
    📱 MÓVIL: Score Danelfin detallado de una acción individual.
    Incluye sub-scores, señales y recomendaciones.
    """
    if symbol not in IBEX_35_SYMBOLS:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not in IBEX 35")
    
    try:
        # Obtener datos
        data_raw = get_daily_data(symbol)
        if not data_raw:
            raise HTTPException(status_code=404, detail="No data available")
        
        df = pd.DataFrame(data_raw)
        df["fecha"] = pd.to_datetime(df["fecha"])
        df = df.sort_values("fecha", ascending=True).reset_index(drop=True)
        
        # Calcular indicadores
        df["sma_20"] = df["close"].rolling(window=20).mean()
        df["sma_50"] = df["close"].rolling(window=50).mean()
        
        from app.services.ensemble import calculate_rsi, calculate_macd, calculate_bollinger_bands
        df["rsi"] = calculate_rsi(df["close"])
        macd_vals = calculate_macd(df["close"])
        df["macd"] = macd_vals[0]
        df["macd_signal"] = macd_vals[1]
        bb_vals = calculate_bollinger_bands(df["close"])
        df["bb_upper"] = bb_vals[0]
        df["bb_middle"] = bb_vals[1]
        df["bb_lower"] = bb_vals[2]
        
        # Score Danelfin
        score_data = calculate_danelfin_score(df)
        
        company_info = get_company_info(symbol)
        latest = df.iloc[-1]
        
        return {
            "symbol": symbol,
            "name": company_info["name"],
            "sector": company_info["sector"],
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "price": round(float(latest["close"]), 2),
            "score": score_data["total_score"],
            "rating": score_data["rating"],
            "confidence": score_data["confidence"],
            "sub_scores": {
                "technical": score_data["technical_score"],
                "momentum": score_data["momentum_score"],
                "sentiment": score_data["sentiment_score"]
            },
            "signals": score_data["signals"],
            "indicators": {
                "rsi": round(float(latest["rsi"]), 2) if pd.notna(latest["rsi"]) else None,
                "macd": round(float(latest["macd"]), 4) if pd.notna(latest["macd"]) else None,
                "macd_signal": round(float(latest["macd_signal"]), 4) if pd.notna(latest["macd_signal"]) else None,
                "sma_20": round(float(latest["sma_20"]), 2) if pd.notna(latest["sma_20"]) else None,
                "sma_50": round(float(latest["sma_50"]), 2) if pd.notna(latest["sma_50"]) else None,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stock/{symbol}/signals")
def get_ea_signals(
    symbol: str,
    strategy: str = Query("ensemble", pattern="^(rsi|macd|ma_crossover|bollinger|ensemble)$")
):
    """
    📱 MÓVIL: Señales de trading de Expert Advisors.
    
    Estrategias disponibles:
    - rsi: Basado en RSI (sobreventa/sobrecompra)
    - macd: Cruces de MACD
    - ma_crossover: Golden/Death Cross
    - bollinger: Bandas de Bollinger
    - ensemble: Combinación de todas (recomendado)
    """
    if symbol not in IBEX_35_SYMBOLS:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not in IBEX 35")
    
    try:
        # Obtener datos
        data_raw = get_daily_data(symbol)
        if not data_raw:
            raise HTTPException(status_code=404, detail="No data available")
        
        df = pd.DataFrame(data_raw)
        df["fecha"] = pd.to_datetime(df["fecha"])
        df = df.sort_values("fecha", ascending=True).reset_index(drop=True)
        df["date"] = df["fecha"].dt.strftime("%Y-%m-%d")
        
        # Calcular indicadores
        df["sma_20"] = df["close"].rolling(window=20).mean()
        df["sma_50"] = df["close"].rolling(window=50).mean()
        
        from app.services.ensemble import calculate_rsi, calculate_macd, calculate_bollinger_bands
        df["rsi"] = calculate_rsi(df["close"])
        macd_vals = calculate_macd(df["close"])
        df["macd"] = macd_vals[0]
        df["macd_signal"] = macd_vals[1]
        bb_vals = calculate_bollinger_bands(df["close"])
        df["bb_upper"] = bb_vals[0]
        df["bb_middle"] = bb_vals[1]
        df["bb_lower"] = bb_vals[2]
        
        # Crear EA según estrategia
        config = EAConfig(
            name=f"{strategy.upper()} Strategy",
            description=f"Expert Advisor {strategy} para {symbol}"
        )
        
        if strategy == "rsi":
            ea = RSI_EA(config)
        elif strategy == "macd":
            ea = MACD_EA(config)
        elif strategy == "ma_crossover":
            ea = MA_Crossover_EA(config)
        elif strategy == "bollinger":
            ea = Bollinger_EA(config)
        else:  # ensemble
            ea = Ensemble_EA(config)
        
        # Generar señal
        signal = ea.analyze(df)
        
        company_info = get_company_info(symbol)
        
        return {
            "symbol": symbol,
            "name": company_info["name"],
            "strategy": strategy,
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "signal": signal["signal"].value,
            "confidence": round(signal["confidence"], 2),
            "reason": signal["reason"],
            "current_price": signal["price"],
            "stop_loss": round(signal["stop_loss"], 2) if signal["stop_loss"] else None,
            "take_profit": round(signal["take_profit"], 2) if signal["take_profit"] else None,
            "risk_reward": round((signal["take_profit"] - signal["price"]) / (signal["price"] - signal["stop_loss"]), 2) 
                          if signal["stop_loss"] and signal["take_profit"] else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stock/{symbol}/backtest")
def run_backtest(
    symbol: str,
    strategy: str = Query("ensemble", pattern="^(rsi|macd|ma_crossover|bollinger|ensemble)$"),
    initial_capital: float = Query(10000, ge=1000)
):
    """
    📱 MÓVIL: Backtest de estrategia EA.
    Retorna métricas de performance histórica.
    """
    if symbol not in IBEX_35_SYMBOLS:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not in IBEX 35")
    
    try:
        # Obtener datos históricos (máximo disponible)
        data_raw = get_daily_data(symbol)
        if not data_raw:
            raise HTTPException(status_code=404, detail="No data available")
        
        df = pd.DataFrame(data_raw)
        df["fecha"] = pd.to_datetime(df["fecha"])
        df = df.sort_values("fecha", ascending=True).reset_index(drop=True)
        df["date"] = df["fecha"].dt.strftime("%Y-%m-%d")
        
        # Calcular indicadores
        df["sma_20"] = df["close"].rolling(window=20).mean()
        df["sma_50"] = df["close"].rolling(window=50).mean()
        
        from app.services.ensemble import calculate_rsi, calculate_macd, calculate_bollinger_bands
        df["rsi"] = calculate_rsi(df["close"])
        macd_vals = calculate_macd(df["close"])
        df["macd"] = macd_vals[0]
        df["macd_signal"] = macd_vals[1]
        bb_vals = calculate_bollinger_bands(df["close"])
        df["bb_upper"] = bb_vals[0]
        df["bb_middle"] = bb_vals[1]
        df["bb_lower"] = bb_vals[2]
        
        # Crear EA
        config = EAConfig(
            name=f"{strategy.upper()} Strategy",
            description=f"Backtest {strategy} para {symbol}",
            min_score=0.0  # Sin filtro de score para backtest
        )
        
        if strategy == "rsi":
            ea = RSI_EA(config)
        elif strategy == "macd":
            ea = MACD_EA(config)
        elif strategy == "ma_crossover":
            ea = MA_Crossover_EA(config)
        elif strategy == "bollinger":
            ea = Bollinger_EA(config)
        else:  # ensemble
            ea = Ensemble_EA(config)
        
        # Ejecutar backtest
        results = ea.backtest(df, initial_capital=initial_capital)
        
        company_info = get_company_info(symbol)
        
        return {
            "symbol": symbol,
            "name": company_info["name"],
            "strategy": strategy,
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "initial_capital": initial_capital,
            "final_equity": round(results["equity_curve"][-1]["equity"], 2) if results["equity_curve"] else initial_capital,
            "metrics": {
                "total_trades": results["total_trades"],
                "winning_trades": results["winning_trades"],
                "losing_trades": results["losing_trades"],
                "win_rate": round(results["win_rate"], 2),
                "total_return": round(results["total_return"], 2),
                "total_return_pct": round(results["total_return_pct"], 2),
                "max_drawdown": round(results["max_drawdown"], 2),
                "sharpe_ratio": round(results["sharpe_ratio"], 2),
                "avg_win": round(results["avg_win"], 2),
                "avg_loss": round(results["avg_loss"], 2),
                "profit_factor": round(results["profit_factor"], 2)
            },
            "recent_trades": results["trades"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/sectors")
def get_sectors():
    """📱 MÓVIL: Lista de sectores del IBEX 35"""
    sector_data = {}
    for sector in SECTORS:
        symbols = get_symbols_by_sector(sector)
        sector_data[sector] = {
            "count": len(symbols),
            "symbols": [{"symbol": s, "name": IBEX_35_SYMBOLS[s]["name"]} for s in symbols]
        }
    
    return {
        "total_sectors": len(SECTORS),
        "sectors": sector_data
    }


@app.get("/api/v1/watchlist")
def get_watchlist(min_score: float = Query(7.0, ge=0, le=10)):
    """
    📱 MÓVIL: Watchlist de oportunidades.
    Retorna acciones con score alto (por defecto >= 7.0).
    """
    return get_ibex35_ranking(limit=35, min_score=min_score)


# ==================== ENDPOINTS LEGACY (COMPATIBILIDAD) ====================

@app.get("/debug/{symbol}")
def debug(symbol: str):
    """Debug endpoint para ver qué retorna compute_signals"""
    try:
        signals = compute_signals(symbol, limit=5, order="desc")
        return {
            "status": "ok",
            "count": len(signals),
            "sample": signals[0] if signals else None
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "type": type(e).__name__
        }

@app.get("/daily/{symbol}")
def daily(symbol: str):
    """
    Devuelve datos diarios OHLCV usando:
    - Yahoo Finance como proveedor principal
    - Twelve Data como respaldo
    """
    try:
        data = get_daily_data(symbol)
        if not data:
            raise HTTPException(status_code=404, detail="No data for symbol")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/daily_signals/{symbol}")
def daily_signals(
    symbol: str,
    limit: int = Query(30, ge=1, le=365),
    order: str = Query("desc", pattern="^(asc|desc)$")
):
    """
    Devuelve OHLCV con indicadores técnicos y recomendaciones (ensemble).
    Parámetros: limit (default 30), order (asc|desc, default desc)
    """
    try:
        signals = compute_signals(symbol, limit=limit, order=order)
        if not signals:
            raise HTTPException(status_code=404, detail="No data for symbol")
        formatted = [format_signal(s) for s in signals]
        return formatted
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/{symbol}", response_class=HTMLResponse)
def dashboard(symbol: str, limit: int = Query(30, ge=1, le=365)):
    """
    Dashboard HTML interactivo con gráficos de precios, medias móviles y RSI.
    """
    try:
        # Obtener datos más recientes primero (desc) y luego revertir para gráficos
        signals = compute_signals(symbol, limit=limit, order="desc")
        if not signals:
            msg = (
                f"No hay datos recientes para {symbol}. "
                "Verifica sufijo (.MC para IBEX) o usa tickers completos como BTC-USD."
            )
            return HTMLResponse(content=f"<h2>{msg}</h2>", status_code=404)
        
        # Convertir todos los valores a tipos Python nativos explícitamente
        clean_signals = []
        for s in signals:
            clean = {}
            for k, v in s.items():
                if v is None:
                    clean[k] = None
                elif isinstance(v, (int, float, str, bool)):
                    clean[k] = v
                elif isinstance(v, dict):
                    clean[k] = v
                elif hasattr(v, 'item'):
                    clean[k] = v.item()
                else:
                    clean[k] = str(v)
            clean_signals.append(clean)
        
        # Invertir para que los gráficos muestren cronológicamente (antiguo a reciente)
        clean_signals_for_chart = list(reversed(clean_signals))
        
        html = generate_html_dashboard(symbol, clean_signals_for_chart)
        return html
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))