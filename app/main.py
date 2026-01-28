from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from typing import List, Optional
import pandas as pd
from functools import lru_cache
from datetime import datetime, timedelta
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.data_providers.market_data import get_daily_data
from app.services.signals import compute_signals
from app.services.formatter import format_signal, generate_html_dashboard
from app.data_providers.ibex35_symbols import (
    IBEX_35_SYMBOLS, get_all_symbols, get_symbols_by_sector, 
    get_company_info, SECTORS
)
from app.scoring.danelfin_score import calculate_danelfin_score
from app.scoring.hybrid_scorer import get_hybrid_scorer, HybridScorer
from app.ea.expert_advisors import (
    RSI_EA, MACD_EA, MA_Crossover_EA, Bollinger_EA, Ensemble_EA, 
    EAConfig, SignalType
)
from app.utils.cache import cache_with_ttl, clear_cache, get_cache_stats
from app.models.user_data import (
    add_favorite, remove_favorite, get_favorites, is_favorite,
    create_alert, get_alerts, delete_alert, update_alert_status,
    check_alerts_for_symbol, get_all_active_alerts,
    add_to_history, get_search_history, clear_search_history
)
from app.services.notifications import send_price_alert_email, test_email_config

app = FastAPI(
    title="IBEX 35 Trading API",
    description="API tipo Danelfin con Expert Advisors para IBEX 35 - Optimizado para Android",
    version="2.3.0"
)

# ==================== SISTEMA HÍBRIDO AI ====================
# Inicializar HybridScorer con ML models (lazy loading)
hybrid_scorer = None  # Se inicializa bajo demanda

def get_scorer(use_hybrid: bool = True) -> HybridScorer:
    """
    Retorna scorer híbrido o tradicional.
    El scorer híbrido se inicializa solo cuando se necesita (lazy loading).
    """
    global hybrid_scorer
    if use_hybrid and hybrid_scorer is None:
        hybrid_scorer = get_hybrid_scorer(
            ml_model_path=None,  # Usar modelo básico por ahora
            enable_sentiment=False  # Deshabilitado por defecto (requiere noticias)
        )
    return hybrid_scorer

# CORS para permitir acceso desde apps móviles
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compresión gzip para respuestas grandes
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ==================== SCHEDULER PARA ALERTAS ====================

def check_all_alerts():
    """
    Job periódico que verifica todas las alertas activas.
    Se ejecuta cada 5 minutos automáticamente.
    """
    print("🔔 Verificando alertas de precios...")
    try:
        alerts = get_all_active_alerts()
        if not alerts:
            print("   No hay alertas activas")
            return
        
        # Agrupar por símbolo para minimizar llamadas a Yahoo
        symbols_to_check = set(alert['symbol'] for alert in alerts)
        print(f"   Verificando {len(symbols_to_check)} símbolos con {len(alerts)} alertas...")
        
        for symbol in symbols_to_check:
            try:
                # Obtener precio actual
                data = get_daily_data(symbol, interval="1d", period="1d")
                if not data or len(data) == 0:
                    continue
                
                current_price = data[-1]['close']
                
                # Verificar alertas para este símbolo
                triggered = check_alerts_for_symbol(symbol, current_price)
                
                if triggered:
                    print(f"   ⚠️ {len(triggered)} alerta(s) disparadas para {symbol} @ €{current_price:.2f}")
                    
                    # Enviar notificaciones
                    for alert in triggered:
                        if alert['notification_type'] in ['email', 'both']:
                            try:
                                send_price_alert_email(
                                    to_email=alert['email'],
                                    symbol=symbol,
                                    condition=alert['condition'],
                                    target_price=alert['target_price'],
                                    current_price=current_price
                                )
                                print(f"   ✉️ Email enviado a {alert['email']}")
                            except Exception as e:
                                print(f"   ⚠️ Email no configurado (esto es normal sin .env)")
                                print(f"   📧 DEMO: Se enviaría email a {alert['email']}")
                                print(f"      Símbolo: {symbol}")
                                print(f"      Condición: {'por encima de' if alert['condition'] == 'above' else 'por debajo de'} €{alert['target_price']:.2f}")
                                print(f"      Precio actual: €{current_price:.2f}")
                                
            except Exception as e:
                print(f"   ❌ Error verificando {symbol}: {e}")
        
        print("🔔 Verificación completada")
    except Exception as e:
        print(f"❌ Error en check_all_alerts: {e}")


# Iniciar scheduler en background
# NOTA: Deshabilitado temporalmente para Railway (causaba bloqueos)
# TODO: Migrar a Railway Cron Jobs o servicio externo
# scheduler = BackgroundScheduler()
# scheduler.add_job(
#     func=check_all_alerts,
#     trigger=IntervalTrigger(minutes=5),
#     id='check_alerts_job',
#     name='Verificar alertas de precio cada 5 minutos',
#     replace_existing=True
# )

@app.on_event("startup")
async def startup_event():
    # scheduler.start()
    print("⚠️ Scheduler de alertas DESHABILITADO (configurar Railway Cron Jobs)")

@app.on_event("shutdown")
async def shutdown_event():
    # scheduler.shutdown()
    print("🛑 Servidor detenido")


@app.get("/", response_class=HTMLResponse)
def root():
    """Página de inicio con documentación y lista de símbolos válidos"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>IBEX 35 Trading API</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
            .section {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .endpoint {{ background: #f8f9fa; padding: 10px; margin: 10px 0; border-left: 4px solid #667eea; border-radius: 4px; }}
            .symbol {{ display: inline-block; background: #e3f2fd; padding: 5px 10px; margin: 5px; border-radius: 4px; font-family: monospace; }}
            a {{ color: #667eea; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .status {{ color: #4caf50; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📈 IBEX 35 Trading API</h1>
            <p>Sistema de análisis tipo Danelfin con Expert Advisors</p>
            <p class="status">✅ Estado: ONLINE</p>
        </div>
        
        <div class="section">
            <h2>🚀 Endpoints Principales</h2>
            <div class="endpoint">
                <strong>GET /api/v1/ibex35/ranking</strong> - Ranking completo IBEX 35<br>
                <a href="/api/v1/ibex35/ranking?limit=10">Ver ejemplo</a>
            </div>
            <div class="endpoint">
                <strong>GET /api/v1/stock/{{symbol}}/score</strong> - Score Danelfin de una acción<br>
                <a href="/api/v1/stock/SAN.MC/score">Ver ejemplo: Santander</a>
            </div>
            <div class="endpoint">
                <strong>GET /api/v1/stock/{{symbol}}/signals</strong> - Señales de trading<br>
                <a href="/api/v1/stock/BBVA.MC/signals?strategy=ensemble">Ver ejemplo: BBVA</a>
            </div>
            <div class="endpoint">
                <strong>GET /dashboard/{{symbol}}</strong> - Dashboard visual interactivo<br>
                <a href="/dashboard/SAN.MC?limit=30">Ver dashboard: Santander</a>
            </div>
            <div class="endpoint">
                <strong>POST /api/v1/favorites/{{symbol}}</strong> - Añadir a favoritos (máx 10)<br>
                <strong>GET /api/v1/favorites</strong> - Ver favoritos<br>
                <a href="/api/v1/favorites">Ver mis favoritos</a>
            </div>
            <div class="endpoint">
                <strong>GET /api/v1/history</strong> - Historial de búsquedas (últimos 10)<br>
                <a href="/api/v1/history">Ver mi historial</a>
            </div>
            <div class="endpoint">
                <strong>GET /health</strong> - Estado del servicio<br>
                <a href="/health">Verificar estado</a>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Símbolos Válidos del IBEX 35</h2>
            <p>Usa estos símbolos en los endpoints (incluye sufijo .MC):</p>
            <div>
                {''.join([f'<span class="symbol"><a href="/dashboard/{s}">{s}</a></span>' for s in sorted(IBEX_35_SYMBOLS.keys())])}
            </div>
        </div>
        
        <div class="section">
            <h2>📚 Documentación Completa</h2>
            <p><a href="/docs">Swagger UI - Documentación interactiva</a></p>
            <p><a href="/redoc">ReDoc - Documentación alternativa</a></p>
        </div>
        
        <div class="section">
            <h2>⚡ Características</h2>
            <ul>
                <li>✅ Scoring tipo Danelfin (0-10)</li>
                <li>✅ 5 Expert Advisors (RSI, MACD, MA Crossover, Bollinger, Ensemble)</li>
                <li>✅ Backtesting de estrategias</li>
                <li>✅ 35 empresas del IBEX 35</li>
                <li>✅ Optimizado para apps móviles Android</li>
            </ul>
        </div>
    </body>
    </html>
    """
    return html

@app.get("/health")
def health_check():
    """Endpoint de salud para monitoreo"""
    cache_stats = get_cache_stats()
    
    # Verificar estado del sistema híbrido
    try:
        scorer = get_scorer(use_hybrid=True)
        hybrid_status = {
            "ml_trained": scorer.ml_predictor.is_trained,
            "prophet_available": scorer.prophet.is_available,
            "sentiment_enabled": scorer.enable_sentiment
        }
    except:
        hybrid_status = {"error": "Hybrid system not initialized"}
    
    return {
        "status": "healthy",
        "api": "IBEX 35 Trading API",
        "version": "2.3.0",
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_symbols": len(IBEX_35_SYMBOLS),
        "cache": cache_stats,
        "ai_system": hybrid_status
    }

@app.post("/api/v1/admin/cache/clear")
def clear_api_cache():
    """Limpia el caché (útil para desarrollo/debugging)"""
    return clear_cache()

@app.get("/api/v1/admin/cache/stats")
def get_cache_statistics():
    """Obtiene estadísticas del caché"""
    return get_cache_stats()


# ==================== HELPERS CON CACHÉ ====================

@cache_with_ttl(ttl_seconds=300)  # 5 minutos
def get_stock_data_cached(symbol: str, interval: str = "1d", period: str = "5y"):
    """Obtiene y cachea datos de mercado (5 min TTL) con soporte para timeframes"""
    data_raw = get_daily_data(symbol, interval=interval, period=period)
    if not data_raw or len(data_raw) < 50:
        return None
    
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
    
    return df


# ==================== ENDPOINTS MÓVIL OPTIMIZADOS ====================

@app.get("/api/v1/ibex35/ranking")
def get_ibex35_ranking(
    limit: int = Query(35, ge=1, le=35),
    sector: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None, ge=0, le=10),
    use_ai: bool = Query(True, description="Usar sistema híbrido AI (XGBoost+Prophet)")
):
    """
    📱 MÓVIL: Ranking completo del IBEX 35 con scores Danelfin o Híbrido AI.
    Retorna lista ordenada por score de mayor a menor.
    
    Parámetros:
    - limit: Número de empresas (default 35)
    - sector: Filtrar por sector (Financiero, Energía, etc.)
    - min_score: Score mínimo (0-10)
    - use_ai: Si True, usa sistema híbrido (XGBoost+Prophet). Si False, solo Danelfin tradicional.
    
    ⚡ Este endpoint usa caché de 5 minutos para mejor performance.
    🤖 NUEVO v2.3: Sistema híbrido con ML predictivo para mejores señales.
    """
    symbols = get_all_symbols()
    if sector:
        symbols = get_symbols_by_sector(sector)
    
    # Obtener scorer apropiado
    scorer = get_scorer(use_hybrid=use_ai) if use_ai else None
    
    results = []
    for symbol in symbols:
        try:
            # Usar datos cacheados
            df = get_stock_data_cached(symbol)
            if df is None:
                continue
            
            # Calcular score (híbrido o tradicional)
            if use_ai and scorer:
                score_data = scorer.calculate_hybrid_score(df)
            else:
                score_data = calculate_danelfin_score(df)
            
            company_info = get_company_info(symbol)
            latest = df.iloc[-1]
            
            result_item = {
                "symbol": symbol,
                "name": company_info["name"],
                "sector": company_info["sector"],
                "score": score_data["total_score"],
                "rating": score_data["rating"],
                "confidence": score_data["confidence"],
                "price": round(float(latest["close"]), 2),
                "change_pct": round((float(latest["close"]) / float(df.iloc[-2]["close"]) - 1) * 100, 2) if len(df) > 1 else 0,
            }
            
            # Agregar información adicional según el tipo de score
            if use_ai and 'components' in score_data:
                result_item.update({
                    "signal": score_data.get("signal", "HOLD"),
                    "methodology": "Hybrid AI",
                    "technical_score": score_data["components"]["technical"]["score"],
                    "ml_score": score_data["components"]["ml_prediction"]["score"],
                    "ml_signal": score_data["components"]["ml_prediction"]["signal"],
                    "prophet_score": score_data["components"]["prophet"]["score"],
                })
            else:
                result_item.update({
                    "technical_score": score_data.get("technical_score", 0),
                    "momentum_score": score_data.get("momentum_score", 0),
                    "sentiment_score": score_data.get("sentiment_score", 0),
                    "methodology": "Danelfin Classic"
                })
            
            results.append(result_item)
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
        "ranking": results[:limit],
        "methodology": "Hybrid AI (XGBoost+Prophet+Danelfin)" if use_ai else "Danelfin Classic",
        "cache_info": "Data cached for 5 minutes"
    }


@app.get("/api/v1/stock/{symbol}/score")
def get_stock_score(
    symbol: str,
    use_ai: bool = Query(True, description="Usar sistema híbrido AI")
):
    """
    📱 MÓVIL: Score detallado de una acción individual.
    
    Parámetros:
    - use_ai: Si True, usa sistema híbrido AI (XGBoost+Prophet+Danelfin). Si False, solo Danelfin.
    
    ⚡ Usa caché de 5 minutos.
    🤖 NUEVO v2.3: Sistema híbrido con predicción ML para señales más precisas.
    """
    # if symbol not in IBEX_35_SYMBOLS:  # Deshabilitado: permitir cualquier símbolo
        # raise HTTPException(status_code=404, detail=f"Symbol {symbol} not in IBEX 35")
    
    try:
        # Añadir al historial de búsquedas
        add_to_history(symbol)
        
        # Usar datos cacheados
        df = get_stock_data_cached(symbol)
        if df is None:
            raise HTTPException(status_code=404, detail="No data available")
        
        # Obtener scorer apropiado
        scorer = get_scorer(use_hybrid=use_ai) if use_ai else None
        
        # Calcular score
        if use_ai and scorer:
            score_data = scorer.calculate_hybrid_score(df)
            
            # Formato de respuesta para sistema híbrido
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
                "signal": score_data.get("signal", "HOLD"),
                "confidence": score_data["confidence"],
                "reason": score_data.get("reason", ""),
                "methodology": score_data.get("methodology", "Hybrid AI"),
                "components": {
                    "technical": {
                        "score": score_data["components"]["technical"]["score"],
                        "weight": score_data["components"]["technical"]["weight"]
                    },
                    "ml_prediction": {
                        "score": score_data["components"]["ml_prediction"]["score"],
                        "signal": score_data["components"]["ml_prediction"]["signal"],
                        "probability": score_data["components"]["ml_prediction"]["probability"],
                        "weight": score_data["components"]["ml_prediction"]["weight"]
                    },
                    "prophet": {
                        "score": score_data["components"]["prophet"]["score"],
                        "predicted_change_pct": score_data["components"]["prophet"]["predicted_change_pct"],
                        "weight": score_data["components"]["prophet"]["weight"]
                    },
                    "sentiment": {
                        "score": score_data["components"]["sentiment"]["score"],
                        "sentiment": score_data["components"]["sentiment"]["sentiment"],
                        "weight": score_data["components"]["sentiment"]["weight"]
                    }
                },
                "indicators": {
                    "rsi": round(float(latest["rsi"]), 2) if pd.notna(latest["rsi"]) else None,
                    "macd": round(float(latest["macd"]), 4) if pd.notna(latest["macd"]) else None,
                    "macd_signal": round(float(latest["macd_signal"]), 4) if pd.notna(latest["macd_signal"]) else None,
                    "sma_20": round(float(latest["sma_20"]), 2) if pd.notna(latest["sma_20"]) else None,
                    "sma_50": round(float(latest["sma_50"]), 2) if pd.notna(latest["sma_50"]) else None,
                }
            }
        else:
            # Modo tradicional Danelfin
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
                "methodology": "Danelfin Classic",
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
    # if symbol not in IBEX_35_SYMBOLS:  # Deshabilitado: permitir cualquier s�mbolo
        # raise HTTPException(status_code=404, detail=f"Symbol {symbol} not in IBEX 35")
    
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
    # if symbol not in IBEX_35_SYMBOLS:  # Deshabilitado: permitir cualquier s�mbolo
        # raise HTTPException(status_code=404, detail=f"Symbol {symbol} not in IBEX 35")
    
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
    # if symbol not in IBEX_35_SYMBOLS:  # Deshabilitado: permitir cualquier símbolo
    #     raise HTTPException(
    #         status_code=404, 
    #         detail=f"Símbolo '{symbol}' no encontrado en IBEX 35. Usa símbolos como SAN.MC, BBVA.MC, etc. Ver / para lista completa."
    #     )
    
    try:
        data = get_daily_data(symbol)
        if not data:
            raise HTTPException(status_code=404, detail=f"No hay datos disponibles para {symbol}")
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo datos: {str(e)}")

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
    # if symbol not in IBEX_35_SYMBOLS:  # Deshabilitado: permitir cualquier símbolo
    #     raise HTTPException(
    #         status_code=404,
    #         detail=f"Símbolo '{symbol}' no encontrado en IBEX 35. Usa símbolos como SAN.MC, BBVA.MC, etc. Ver / para lista completa."
    #     )
    
    try:
        signals = compute_signals(symbol, limit=limit, order=order)
        if not signals:
            raise HTTPException(status_code=404, detail=f"No hay datos disponibles para {symbol}")
        formatted = [format_signal(s) for s in signals]
        return formatted
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando señales: {str(e)}")

@app.get("/dashboard/{symbol}", response_class=HTMLResponse)
def dashboard(
    symbol: str, 
    limit: int = Query(30, ge=1, le=365),
    timeframe: str = Query("1d", pattern="^(1h|1d|5d)$")
):
    """
    Dashboard HTML interactivo con gráficos de precios, medias móviles y RSI.
    Timeframes: 
    - 1h: Últimos 60 minutos con datos cada 5 minutos
    - 1d: Últimas 24 horas con datos cada hora
    - 5d: Últimos 5 días con datos diarios
    """
    # Validar símbolo
    # if symbol not in IBEX_35_SYMBOLS:  # Deshabilitado: permitir cualquier símbolo
    #     available_symbols = ', '.join(sorted(list(IBEX_35_SYMBOLS.keys())[:10]))
    #     error_html = f"""
    #     <!DOCTYPE html>
    #     <html>
    #     <head>
    #         <title>Error - Símbolo Inválido</title>
    #         <meta charset="utf-8">
    #         <style>
    #             body {{ font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }}
    #             .error {{ background: #ffebee; border-left: 4px solid #f44336; padding: 20px; border-radius: 4px; }}
    #             .symbols {{ background: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 4px; }}
    #             a {{ color: #1976d2; text-decoration: none; }}
    #             a:hover {{ text-decoration: underline; }}
    #         </style>
    #     </head>
    #     <body>
    #         <div class="error">
    #             <h2>❌ Símbolo '{symbol}' no encontrado</h2>
    #             <p>Este símbolo no pertenece al IBEX 35.</p>
    #         </div>
    #         <div class="symbols">
    #             <h3>📊 Símbolos válidos:</h3>
    #             <p>Ejemplos: {available_symbols}, ...</p>
    #             <p><a href="/">Ver lista completa de símbolos →</a></p>
    #         </div>
    #         <p><a href="/dashboard/SAN.MC">Ver ejemplo: Dashboard de Santander</a></p>
    #     </body>
    #     </html>
    #     """
    #     return HTMLResponse(content=error_html, status_code=404)
    
    try:
        # Añadir al historial de búsquedas
        add_to_history(symbol)
        
        # Mapear timeframe a interval/period para Yahoo
        interval_map = {
            "1h": ("5m", "1d"),     # Última hora: datos cada 5 minutos del último día
            "1d": ("1h", "5d"),     # Último día: datos cada hora de los últimos 5 días
            "5d": ("1d", "3mo")     # Últimos 5 días mostrados: datos diarios de 3 meses (suficiente para SMA50)
        }
        interval, period = interval_map.get(timeframe, ("1d", "3mo"))
        
        print(f"🔍 DEBUG main.py - timeframe: {timeframe}, interval: {interval}, period: {period}")
        
        # Obtener datos con el timeframe seleccionado
        signals = compute_signals(symbol, limit=limit, order="desc", interval=interval, period=period)
        if not signals:
            company_info = get_company_info(symbol)
            company_name = company_info.get('name', symbol) if company_info else symbol
            msg = (
                f"No hay datos recientes para {company_name} ({symbol}). "
                "Puede que el proveedor de datos esté temporalmente no disponible o el símbolo no sea válido."
            )
            return HTMLResponse(content=f"<h2>{msg}</h2><p><a href='/'>Volver al inicio</a></p>", status_code=404)
        
        # Obtener score Danelfin actualizado para el último punto
        danelfin_confidence = None
        try:
            df = get_stock_data_cached(symbol, interval=interval, period=period)
            if df is not None:
                from app.scoring.danelfin_score import calculate_danelfin_score
                danelfin = calculate_danelfin_score(df)
                danelfin_confidence = danelfin['confidence']
                # Actualizar el primer signal (más reciente) con el score de Danelfin
                # signals[0] es el más reciente porque order="desc"
                signals[0]['confidence'] = danelfin_confidence
                print(f"✅ Confianza Danelfin para {symbol}: {danelfin_confidence}")
        except Exception as e:
            print(f"❌ Error obteniendo score Danelfin: {e}")
            import traceback
            traceback.print_exc()
        
        # Actualizar confianza ANTES de serializar (signals[0] es el más reciente)
        if danelfin_confidence and len(signals) > 0:
            signals[0]['confidence'] = danelfin_confidence
            print(f"✅ Confianza inyectada ANTES de serialización: {signals[0]['confidence']}")
        
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
        
        # Verificar que la confianza sobrevivió la serialización
        if len(clean_signals_for_chart) > 0:
            print(f"✅ Confianza DESPUÉS de serialización: {clean_signals_for_chart[-1].get('confidence')}")
        
        html = generate_html_dashboard(symbol, clean_signals_for_chart, timeframe=timeframe)
        return html
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generando dashboard: {str(e)}")


# ==================== ENDPOINTS NUEVOS: TIMEFRAMES ====================

@app.get("/api/v1/stock/{symbol}/data")
def get_stock_data_timeframe(
    symbol: str,
    timeframe: str = Query("1d", pattern="^(1h|1d|5d)$")
):
    """
    📱 Obtiene datos de mercado con diferentes intervalos de tiempo.
    
    Timeframes disponibles:
    - 1h: Datos horarios (últimos 7 días)
    - 1d: Datos diarios (últimos 6 meses por defecto)
    - 5d: Datos diarios (últimos 5 días)
    """
    # if symbol not in IBEX_35_SYMBOLS:  # Deshabilitado: permitir cualquier símbolo
    #     raise HTTPException(status_code=404, detail=f"Símbolo '{symbol}' no encontrado")
    
    try:
        # Mapear timeframes
        interval_map = {
            "1h": ("1h", "7d"),
            "1d": ("1d", "6mo"),
            "5d": ("1d", "5d")
        }
        
        interval, period = interval_map[timeframe]
        data_raw = get_daily_data(symbol, interval=interval, period=period)
        
        if not data_raw:
            raise HTTPException(status_code=404, detail="No hay datos disponibles")
        
        company_info = get_company_info(symbol)
        
        return {
            "symbol": symbol,
            "name": company_info["name"],
            "sector": company_info["sector"],
            "timeframe": timeframe,
            "data_points": len(data_raw),
            "data": data_raw
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo datos: {str(e)}")


# ==================== ENDPOINTS NUEVOS: FAVORITOS ====================

@app.post("/api/v1/favorites/{symbol}")
def add_to_favorites(
    symbol: str,
    user_id: str = Query("default", description="ID del usuario (default: 'default')")
):
    """
    ⭐ Añade un símbolo a favoritos.
    """
    # if symbol not in IBEX_35_SYMBOLS:  # Deshabilitado: permitir cualquier símbolo
    #     raise HTTPException(status_code=404, detail=f"Símbolo '{symbol}' no encontrado")
    
    result = add_favorite(symbol, user_id)
    company_info = get_company_info(symbol)
    
    return {
        **result,
        "name": company_info["name"],
        "sector": company_info["sector"]
    }


@app.delete("/api/v1/favorites/{symbol}")
def remove_from_favorites(
    symbol: str,
    user_id: str = Query("default")
):
    """
    🗑️ Elimina un símbolo de favoritos.
    """
    result = remove_favorite(symbol, user_id)
    return result


@app.get("/api/v1/favorites")
def list_favorites(user_id: str = Query("default")):
    """
    📋 Lista todos los símbolos favoritos con información completa.
    """
    favorites = get_favorites(user_id)
    
    # Enriquecer con información de las empresas
    enriched = []
    for fav in favorites:
        symbol = fav["symbol"]
        if symbol in IBEX_35_SYMBOLS:
            company_info = get_company_info(symbol)
            enriched.append({
                **fav,
                "name": company_info["name"],
                "sector": company_info["sector"]
            })
        else:
            enriched.append(fav)
    
    return {
        "total": len(enriched),
        "favorites": enriched
    }


# ==================== ENDPOINTS NUEVOS: HISTORIAL ====================

@app.get("/api/v1/history")
def get_history(user_id: str = Query("default")):
    """
    📜 Obtiene el historial de búsquedas (últimos 10 símbolos únicos consultados).
    """
    history = get_search_history(user_id)
    
    # Enriquecer con información de las empresas
    enriched = []
    for item in history:
        symbol = item["symbol"]
        if symbol in IBEX_35_SYMBOLS:
            company_info = get_company_info(symbol)
            enriched.append({
                **item,
                "name": company_info["name"],
                "sector": company_info["sector"]
            })
        else:
            enriched.append(item)
    
    return {
        "total": len(enriched),
        "history": enriched
    }


@app.delete("/api/v1/history")
def clear_history(user_id: str = Query("default")):
    """
    🗑️ Limpia todo el historial de búsquedas del usuario.
    """
    result = clear_search_history(user_id)
    return result


# ==================== ENDPOINTS NUEVOS: ALERTAS ====================

@app.post("/api/v1/alerts")
def create_price_alert(
    symbol: str = Query(..., description="Símbolo de la acción"),
    condition: str = Query(..., pattern="^(above|below)$", description="'above' o 'below'"),
    target_price: float = Query(..., gt=0, description="Precio objetivo"),
    notification_type: str = Query("popup", pattern="^(popup|email|both)$"),
    email: Optional[str] = Query(None, description="Email para notificaciones (requerido si notification_type=email/both)"),
    user_id: str = Query("default")
):
    """
    🔔 Crea una alerta de precio.
    
    La alerta se activará cuando:
    - condition='above': el precio alcance o supere target_price
    - condition='below': el precio baje de target_price
    
    Tipos de notificación:
    - popup: Solo notificación en la plataforma
    - email: Solo email
    - both: Ambos
    """
    # if symbol not in IBEX_35_SYMBOLS:  # Deshabilitado: permitir cualquier símbolo
    #     raise HTTPException(status_code=404, detail=f"Símbolo '{symbol}' no encontrado")
    
    try:
        result = create_alert(
            symbol=symbol,
            condition=condition,
            target_price=target_price,
            notification_type=notification_type,
            email=email,
            user_id=user_id
        )
        
        company_info = get_company_info(symbol)
        
        return {
            **result,
            "name": company_info["name"]
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/alerts")
def list_alerts(
    user_id: str = Query("default"),
    active_only: bool = Query(True, description="Solo alertas activas")
):
    """
    📋 Lista todas las alertas de un usuario.
    """
    alerts = get_alerts(user_id, active_only)
    
    # Enriquecer con nombres de empresas
    enriched = []
    for alert in alerts:
        symbol = alert["symbol"]
        if symbol in IBEX_35_SYMBOLS:
            company_info = get_company_info(symbol)
            alert["company_name"] = company_info["name"]
        enriched.append(alert)
    
    return {
        "total": len(enriched),
        "alerts": enriched
    }


@app.delete("/api/v1/alerts/{alert_id}")
def delete_price_alert(
    alert_id: int,
    user_id: str = Query("default")
):
    """
    🗑️ Elimina una alerta.
    """
    result = delete_alert(alert_id, user_id)
    return result


@app.patch("/api/v1/alerts/{alert_id}")
def toggle_alert(
    alert_id: int,
    is_active: bool = Query(..., description="true para activar, false para desactivar")
):
    """
    ⏸️ Activa o desactiva una alerta sin eliminarla.
    """
    result = update_alert_status(alert_id, is_active)
    return result


@app.post("/api/v1/alerts/check/{symbol}")
def manual_check_alerts(symbol: str):
    """
    🔍 Verifica manualmente alertas para un símbolo (útil para testing).
    En producción, esto debería ejecutarse automáticamente cada X minutos.
    """
    # if symbol not in IBEX_35_SYMBOLS:  # Deshabilitado: permitir cualquier símbolo
    #     raise HTTPException(status_code=404, detail=f"Símbolo '{symbol}' no encontrado")
    
    try:
        # Obtener precio actual
        data_raw = get_daily_data(symbol, interval="1d", period="1d")
        if not data_raw:
            raise HTTPException(status_code=404, detail="No se pudo obtener precio actual")
        
        current_price = data_raw[-1]["close"]
        
        # Verificar alertas
        triggered = check_alerts_for_symbol(symbol, current_price)
        
        # Enviar notificaciones
        notifications_sent = []
        for alert in triggered:
            if alert["notification_type"] in ["email", "both"]:
                company_info = get_company_info(symbol)
                email_result = send_price_alert_email(alert, company_info["name"])
                notifications_sent.append(email_result)
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "alerts_triggered": len(triggered),
            "triggered_alerts": triggered,
            "notifications_sent": notifications_sent
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ADMIN ====================

@app.post("/api/v1/admin/check-alerts-now")
def manually_check_alerts():
    """
    🔔 Verificar TODAS las alertas activas manualmente (admin).
    
    Endpoint para ejecutar manualmente la verificación de alertas,
    ya que el scheduler automático está deshabilitado en Railway.
    """
    try:
        check_all_alerts()
        return {
            "status": "success",
            "message": "Verificación de alertas completada. Revisa los logs del servidor."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar alertas: {str(e)}")


@app.get("/api/v1/admin/test-email")
def test_email_configuration():
    """
    📧 Prueba la configuración de email (admin).
    """
    result = test_email_config()
    return result


# ==================== NUEVOS ENDPOINTS AI/ML ====================

@app.get("/api/v1/admin/ml/feature-importance")
def get_ml_feature_importance():
    """
    📊 Obtiene la importancia de cada feature en el modelo ML.
    
    Útil para entender qué indicadores son más importantes para las predicciones.
    Solo funciona si el modelo está entrenado.
    """
    try:
        scorer = get_scorer(use_hybrid=True)
        if scorer and scorer.ml_predictor.is_trained:
            importance = scorer.get_feature_importance()
            return {
                "model_status": "trained",
                "feature_importance": importance,
                "total_features": len(importance)
            }
        else:
            return {
                "model_status": "not_trained",
                "message": "Modelo no entrenado. Usa modo básico o entrena primero.",
                "feature_importance": {}
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/admin/ml/train-model")
def train_ml_model(
    symbol: str = Query("^IBEX", description="Símbolo para entrenar (default: índice IBEX)"),
    days_ahead: int = Query(15, ge=1, le=30, description="Días futuros a predecir"),
    test_size: float = Query(0.2, ge=0.1, le=0.4, description="Proporción de datos para test")
):
    """
    🤖 Entrena el modelo ML con datos históricos (admin).
    
    Parámetros:
    - symbol: Símbolo para entrenar (por defecto índice IBEX)
    - days_ahead: Número de días futuros a predecir (default 15)
    - test_size: Proporción de datos para test (default 0.2 = 20%)
    
    ⚠️ Advertencia: Este proceso puede tardar varios minutos.
    """
    try:
        from sklearn.model_selection import train_test_split
        import numpy as np
        
        # Obtener datos históricos (5 años)
        df = get_stock_data_cached(symbol, period="5y")
        if df is None or len(df) < 500:
            raise HTTPException(
                status_code=400,
                detail="Datos insuficientes para entrenar (mínimo 500 días)"
            )
        
        print(f"🔄 Iniciando entrenamiento con {len(df)} días de datos...")
        
        # Crear target: 1 si sube en N días, 0 si baja
        df["future_return"] = df["close"].shift(-days_ahead) / df["close"] - 1
        df["target"] = (df["future_return"] > 0).astype(int)
        
        # Eliminar filas con NaN
        df_clean = df.dropna()
        
        if len(df_clean) < 100:
            raise HTTPException(
                status_code=400,
                detail="Datos insuficientes después de limpiar NaN"
            )
        
        # Preparar features
        feature_cols = ['rsi', 'macd', 'macd_signal', 'sma_20', 'sma_50',
                       'bb_upper', 'bb_middle', 'bb_lower', 'volume', 'close']
        
        X = df_clean[feature_cols].values
        y = df_clean["target"].values
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False  # No shuffle para series temporales
        )
        
        # Entrenar modelo
        scorer = get_scorer(use_hybrid=True)
        scorer.ml_predictor.train(X_train, y_train, X_test, y_test)
        
        # Guardar modelo
        model_path = "data/models/ibex_xgboost.pkl"
        scorer.ml_predictor.save_model(model_path)
        
        # Obtener métricas
        importance = scorer.get_feature_importance()
        
        return {
            "status": "success",
            "message": "Modelo entrenado exitosamente",
            "model_path": model_path,
            "training_stats": {
                "total_samples": len(df_clean),
                "train_samples": len(X_train),
                "test_samples": len(X_test),
                "days_ahead": days_ahead,
                "features_used": len(feature_cols)
            },
            "feature_importance": importance
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en entrenamiento: {str(e)}")


@app.get("/api/v1/admin/ml/model-status")
def get_ml_model_status():
    """
    📊 Obtiene el estado del sistema híbrido AI.
    
    Muestra qué componentes están activos y sus configuraciones.
    """
    try:
        scorer = get_scorer(use_hybrid=True)
        
        return {
            "hybrid_system": {
                "status": "active",
                "components": {
                    "danelfin": {
                        "status": "active",
                        "weight": "25%"
                    },
                    "ml_predictor": {
                        "status": "trained" if scorer.ml_predictor.is_trained else "basic_mode",
                        "weight": "40%",
                        "model_type": "XGBoost"
                    },
                    "prophet": {
                        "status": "available" if scorer.prophet.is_available else "unavailable",
                        "weight": "20%"
                    },
                    "sentiment": {
                        "status": "enabled" if scorer.enable_sentiment else "disabled",
                        "weight": "15%"
                    }
                },
                "methodology": "Hybrid AI: Danelfin + XGBoost + Prophet + FinBERT"
            }
        }
    except Exception as e:
        return {
            "hybrid_system": {
                "status": "error",
                "error": str(e)
            }
        }

