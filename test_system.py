"""
Script de prueba rápida para el sistema IBEX 35 Trading.
Prueba scoring Danelfin y Expert Advisors.
"""
import sys
import pandas as pd
from app.data_providers.market_data import get_daily_data
from app.scoring.danelfin_score import calculate_danelfin_score
from app.ea.expert_advisors import Ensemble_EA, EAConfig
from app.services.ensemble import calculate_rsi, calculate_macd, calculate_bollinger_bands


def test_symbol(symbol: str = "SAN.MC"):
    """Prueba completa de una acción"""
    print(f"\n{'='*60}")
    print(f"  ANÁLISIS DE {symbol}")
    print(f"{'='*60}\n")
    
    # 1. Obtener datos
    print("📊 Obteniendo datos históricos...")
    data_raw = get_daily_data(symbol)
    if not data_raw:
        print(f"❌ No se pudieron obtener datos para {symbol}")
        return
    
    df = pd.DataFrame(data_raw)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values("fecha", ascending=True).reset_index(drop=True)
    
    print(f"✓ {len(df)} días de datos obtenidos (desde {df.iloc[0]['fecha'].strftime('%Y-%m-%d')} hasta {df.iloc[-1]['fecha'].strftime('%Y-%m-%d')})")
    
    # 2. Calcular indicadores
    print("\n📈 Calculando indicadores técnicos...")
    df["sma_20"] = df["close"].rolling(window=20).mean()
    df["sma_50"] = df["close"].rolling(window=50).mean()
    df["rsi"] = calculate_rsi(df["close"])
    
    macd_vals = calculate_macd(df["close"])
    df["macd"] = macd_vals[0]
    df["macd_signal"] = macd_vals[1]
    
    bb_vals = calculate_bollinger_bands(df["close"])
    df["bb_upper"] = bb_vals[0]
    df["bb_middle"] = bb_vals[1]
    df["bb_lower"] = bb_vals[2]
    
    df["date"] = df["fecha"].dt.strftime("%Y-%m-%d")
    
    print("✓ Indicadores calculados: RSI, MACD, SMA 20/50, Bollinger Bands")
    
    # 3. Score Danelfin
    print("\n⭐ Calculando Score Danelfin...")
    score_data = calculate_danelfin_score(df)
    
    latest = df.iloc[-1]
    print(f"\n  Precio actual: €{latest['close']:.2f}")
    print(f"  Score total: {score_data['total_score']:.1f}/10")
    print(f"  Rating: {score_data['rating']}")
    print(f"  Confianza: {score_data['confidence']}")
    print(f"\n  Sub-scores:")
    print(f"    - Técnico:  {score_data['technical_score']:.1f}/10")
    print(f"    - Momentum: {score_data['momentum_score']:.1f}/10")
    print(f"    - Sentiment: {score_data['sentiment_score']:.1f}/10")
    
    print(f"\n  Señales:")
    for signal in score_data['signals'][:5]:
        print(f"    • {signal}")
    
    # 4. Expert Advisor
    print("\n🤖 Analizando con Expert Advisor (Ensemble)...")
    config = EAConfig(
        name="Test EA",
        description="Prueba de EA",
        min_score=0.0  # Sin filtro para prueba
    )
    ea = Ensemble_EA(config)
    
    signal = ea.analyze(df, current_score=score_data['total_score'])
    
    print(f"\n  Señal: {signal['signal'].value}")
    print(f"  Confianza: {signal['confidence']:.2f}")
    print(f"  Razón: {signal['reason']}")
    print(f"  Precio: €{signal['price']:.2f}")
    
    if signal['stop_loss']:
        print(f"  Stop Loss: €{signal['stop_loss']:.2f}")
    if signal['take_profit']:
        print(f"  Take Profit: €{signal['take_profit']:.2f}")
    
    # 5. Backtest rápido
    print("\n🔄 Ejecutando backtest...")
    backtest_results = ea.backtest(df, initial_capital=10000)
    
    print(f"\n  Capital inicial: €10,000")
    print(f"  Capital final: €{backtest_results['equity_curve'][-1]['equity']:.2f}")
    print(f"  Retorno: {backtest_results['total_return_pct']:.2f}%")
    print(f"  Operaciones totales: {backtest_results['total_trades']}")
    print(f"  Operaciones ganadoras: {backtest_results['winning_trades']}")
    print(f"  Win rate: {backtest_results['win_rate']:.2f}%")
    print(f"  Max drawdown: {backtest_results['max_drawdown']:.2f}%")
    print(f"  Sharpe ratio: {backtest_results['sharpe_ratio']:.2f}")
    print(f"  Profit factor: {backtest_results['profit_factor']:.2f}")
    
    print(f"\n{'='*60}\n")


def test_top_5():
    """Prueba rápida de las top 5 empresas del IBEX 35"""
    from app.data_providers.ibex35_symbols import IBEX_35_SYMBOLS
    
    print("\n" + "="*60)
    print("  TOP 5 EMPRESAS DEL IBEX 35")
    print("="*60 + "\n")
    
    # Top empresas por capitalización
    top_symbols = ["SAN.MC", "BBVA.MC", "IBE.MC", "ITX.MC", "TEF.MC"]
    
    results = []
    for symbol in top_symbols:
        try:
            print(f"Analizando {symbol}...", end=" ")
            
            data_raw = get_daily_data(symbol)
            if not data_raw or len(data_raw) < 50:
                print("❌ Datos insuficientes")
                continue
            
            df = pd.DataFrame(data_raw)
            df["fecha"] = pd.to_datetime(df["fecha"])
            df = df.sort_values("fecha", ascending=True).reset_index(drop=True)
            
            # Calcular indicadores
            df["sma_20"] = df["close"].rolling(window=20).mean()
            df["sma_50"] = df["close"].rolling(window=50).mean()
            df["rsi"] = calculate_rsi(df["close"])
            
            macd_vals = calculate_macd(df["close"])
            df["macd"] = macd_vals[0]
            df["macd_signal"] = macd_vals[1]
            
            bb_vals = calculate_bollinger_bands(df["close"])
            df["bb_upper"] = bb_vals[0]
            df["bb_middle"] = bb_vals[1]
            df["bb_lower"] = bb_vals[2]
            
            # Score
            score_data = calculate_danelfin_score(df)
            latest = df.iloc[-1]
            
            results.append({
                'symbol': symbol,
                'name': IBEX_35_SYMBOLS[symbol]['name'],
                'price': latest['close'],
                'score': score_data['total_score'],
                'rating': score_data['rating']
            })
            
            print("✓")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Ordenar por score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    print("\n" + "-"*60)
    print(f"{'EMPRESA':<25} {'PRECIO':>10} {'SCORE':>8} {'RATING':>15}")
    print("-"*60)
    
    for r in results:
        print(f"{r['name']:<25} €{r['price']:>9.2f} {r['score']:>7.1f} {r['rating']:>15}")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    # Prueba individual
    test_symbol("SAN.MC")  # Banco Santander
    
    # Prueba top 5
    # test_top_5()
