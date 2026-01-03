from typing import Dict, List
import json
from datetime import datetime

def _safe_float(x, default=None):
    try:
        if x is None:
            return default
        # Evitar problemas con Series de pandas
        if hasattr(x, '__len__') and not isinstance(x, str) and not hasattr(x, 'item'):
            # Es algo iterable pero no scalar - devolve default
            return default
        # Importar pandas localmente para chequear NaN
        import pandas as pd
        try:
            if pd.isna(x):
                return default
        except (TypeError, ValueError):
            pass
        if hasattr(x, "item"):
            try:
                val = x.item()
                if pd.isna(val):
                    return default
                return float(val)
            except (TypeError, ValueError):
                return default
        if isinstance(x, (int, float)):
            return float(x)
        return float(x)
    except (TypeError, ValueError):
        return default

def _safe_int(x, default=None):
    try:
        if x is None:
            return default
        import pandas as pd
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

def format_signal(signal: Dict) -> Dict:
    """Normaliza una señal: devuelve tipos nativos y añade campos visuales."""
    emoji_map = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}
    recommendation = str(signal.get("recommendation") or "HOLD")
    emoji = emoji_map.get(recommendation, "⚪")

    confidence = _safe_float(signal.get("confidence"), 0.0) or 0.0
    confidence_pct = int(max(0, min(1, confidence)) * 100)
    bar_filled = "█" * (confidence_pct // 10)
    bar_empty = "░" * (10 - (confidence_pct // 10))
    confidence_bar = f"[{bar_filled}{bar_empty}] {confidence_pct}%"

    pct_change = _safe_float(signal.get("pct_change"), 0.0) or 0.0
    pct_emoji = "📈" if pct_change > 0 else "📉" if pct_change < 0 else "➡️"

    safe = dict(signal)
    safe["recommendation"] = recommendation
    safe["confidence"] = confidence
    safe["confidence_pct"] = confidence_pct
    safe["pct_change"] = pct_change
    safe["close"] = _safe_float(signal.get("close"))
    safe["volume"] = _safe_int(signal.get("volume"))
    safe["rsi"] = _safe_float(signal.get("rsi"))
    safe["sma20"] = _safe_float(signal.get("sma20"))
    safe["sma50"] = _safe_float(signal.get("sma50"))
    safe["signal_emoji"] = emoji
    safe["confidence_bar"] = confidence_bar
    safe["pct_emoji"] = pct_emoji
    safe["formatted_recommendation"] = f"{emoji} {recommendation}"
    return safe

def generate_html_dashboard(symbol: str, signals: List[Dict]) -> str:
    """Genera dashboard HTML moderno con tablas, múltiples gráficos y diseño profesional."""
    if not signals:
        return "<h1>No hay datos disponibles</h1>"

    try:
        signals_sorted = sorted(signals, key=lambda s: (s.get("fecha") or ""))
    except Exception:
        signals_sorted = list(signals)

    normalized = [format_signal(s) for s in signals_sorted]

    # Extraer datos para gráficos
    fechas = [str(s.get("fecha") or "") for s in normalized]
    closes = [_safe_float(s.get("close")) for s in normalized]
    opens = [_safe_float(s.get("open")) for s in normalized]
    highs = [_safe_float(s.get("high")) for s in normalized]
    lows = [_safe_float(s.get("low")) for s in normalized]
    volumes = [_safe_int(s.get("volume"), 0) for s in normalized]
    sma20s = [_safe_float(s.get("sma20")) for s in normalized]
    sma50s = [_safe_float(s.get("sma50")) for s in normalized]
    rsis = [_safe_float(s.get("rsi")) for s in normalized]
    macds = [_safe_float(s.get("macd")) for s in normalized]
    macd_signals = [_safe_float(s.get("macd_signal")) for s in normalized]
    bb_uppers = [_safe_float(s.get("bb_upper")) for s in normalized]
    bb_lowers = [_safe_float(s.get("bb_lower")) for s in normalized]

    # Datos del último día (el más reciente está al final después de sort)
    latest = normalized[-1]
    recommendation = str(latest.get("recommendation") or "HOLD")
    emoji_map = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}
    emoji = emoji_map.get(recommendation, "⚪")
    color_map = {"BUY": "#10b981", "SELL": "#ef4444", "HOLD": "#f59e0b"}
    rec_color = color_map.get(recommendation, "#6b7280")

    confidence = float(latest.get("confidence") or 0.0)
    confidence_pct = int(max(0, min(1, confidence)) * 100)
    latest_close_val = _safe_float(latest.get("close"))
    latest_close = f"€{latest_close_val:.2f}" if latest_close_val is not None else "N/A"
    pct_val = _safe_float(latest.get("pct_change"))
    latest_pct_class = ("positive" if pct_val and pct_val > 0 else "negative" if pct_val and pct_val < 0 else "neutral")
    latest_pct = f"{pct_val:+.2f}%" if pct_val is not None else "N/A"
    latest_rsi_val = _safe_float(latest.get("rsi"))
    latest_rsi = f"{latest_rsi_val:.1f}" if latest_rsi_val is not None else "N/A"
    latest_volume_val = _safe_int(latest.get("volume"))
    latest_volume = f"{latest_volume_val:,}" if latest_volume_val is not None else "N/A"
    
    # Convertir reason a string de forma segura
    reason_val = latest.get("reason")
    if reason_val is None or reason_val == "":
        latest_reason = "Sin análisis disponible"
    else:
        latest_reason = str(reason_val)

    # Calcular estadísticas adicionales
    valid_closes = [c for c in closes if c is not None]
    max_price = max(valid_closes) if valid_closes else 0
    min_price = min(valid_closes) if valid_closes else 0
    avg_price = sum(valid_closes) / len(valid_closes) if valid_closes else 0
    
    valid_volumes = [v for v in volumes if v is not None and v > 0]
    avg_volume = sum(valid_volumes) / len(valid_volumes) if valid_volumes else 0

    # Fecha del último dato (el más reciente)
    latest_date_str = str(latest.get("fecha", ""))
    try:
        # Convertir fecha YYYY-MM-DD a DD/MM/YYYY
        from datetime import datetime
        latest_date_obj = datetime.strptime(latest_date_str, "%Y-%m-%d")
        current_date = latest_date_obj.strftime("%d/%m/%Y")
    except:
        current_date = latest_date_str

    # Generar filas de tabla (últimos 10 días, más reciente primero)
    table_rows = ""
    for s in reversed(normalized[-10:]):
        fecha_raw = s.get("fecha", "N/A")
        # Formatear fecha a DD/MM/YYYY
        try:
            from datetime import datetime
            fecha_obj = datetime.strptime(str(fecha_raw), "%Y-%m-%d")
            fecha = fecha_obj.strftime("%d/%m/%Y")
        except:
            fecha = str(fecha_raw)
        
        close_val = _safe_float(s.get("close"))
        close_str = f"€{close_val:.2f}" if close_val is not None else "N/A"
        pct = _safe_float(s.get("pct_change"))
        pct_str = f"{pct:+.2f}%" if pct is not None else "N/A"
        pct_class = "positive" if pct and pct > 0 else "negative" if pct and pct < 0 else "neutral"
        vol = _safe_int(s.get("volume"))
        vol_str = f"{vol:,}" if vol is not None else "N/A"
        rsi_val = _safe_float(s.get("rsi"))
        rsi_str = f"{rsi_val:.1f}" if rsi_val is not None else "N/A"
        rec = s.get("recommendation", "HOLD")
        rec_emoji = emoji_map.get(rec, "⚪")
        
        table_rows += f"""
            <tr>
                <td>{fecha}</td>
                <td class="price">{close_str}</td>
                <td class="{pct_class}">{pct_str}</td>
                <td>{vol_str}</td>
                <td>{rsi_str}</td>
                <td class="signal">{rec_emoji} {rec}</td>
            </tr>
        """

    # JSON para gráficos
    fechas_json = json.dumps(fechas)
    closes_json = json.dumps(closes)
    opens_json = json.dumps(opens)
    highs_json = json.dumps(highs)
    lows_json = json.dumps(lows)
    volumes_json = json.dumps(volumes)
    sma20s_json = json.dumps(sma20s)
    sma50s_json = json.dumps(sma50s)
    rsis_json = json.dumps(rsis)
    macds_json = json.dumps(macds)
    macd_signals_json = json.dumps(macd_signals)
    bb_uppers_json = json.dumps(bb_uppers)
    bb_lowers_json = json.dumps(bb_lowers)

    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Trading - {symbol}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{ width: 100%; min-height: 100vh; }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 30px 20px;
            color: #1f2937;
        }}
        
        .container {{ 
            max-width: 1600px; 
            margin: 0 auto; 
        }}
        
        /* Search Bar */
        .search-bar {{ 
            background: rgba(255,255,255,0.98); 
            padding: 25px 35px; 
            border-radius: 20px; 
            margin-bottom: 30px; 
            box-shadow: 0 20px 60px rgba(0,0,0,0.2); 
            display: flex; 
            gap: 15px; 
            align-items: center; 
            flex-wrap: wrap;
            backdrop-filter: blur(10px);
        }}
        
        .search-bar input {{ 
            flex: 1; 
            min-width: 250px; 
            padding: 16px 24px; 
            border: 2px solid #e5e7eb; 
            border-radius: 14px; 
            font-size: 1.05em;
            transition: all 0.3s ease;
            font-family: 'Inter', sans-serif;
        }}
        
        .search-bar input:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        
        .search-bar button {{ 
            padding: 16px 36px; 
            background: linear-gradient(135deg, #667eea, #764ba2); 
            color: white; 
            border: none; 
            border-radius: 14px; 
            font-weight: 600; 
            cursor: pointer;
            font-size: 1.05em;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .search-bar button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }}
        
        .limit-selector {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .limit-selector label {{
            font-weight: 600;
            color: #4b5563;
        }}
        
        .limit-selector select {{
            padding: 12px 20px;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            font-size: 1em;
            cursor: pointer;
            background: white;
            transition: all 0.3s ease;
        }}
        
        .limit-selector select:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        /* Header */
        header {{ 
            background: rgba(255,255,255,0.98); 
            padding: 45px 50px; 
            border-radius: 20px; 
            margin-bottom: 30px; 
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            backdrop-filter: blur(10px);
        }}
        
        h1 {{ 
            font-size: 3.8em; 
            font-weight: 900; 
            color: #111827; 
            margin-bottom: 15px;
            letter-spacing: -1px;
        }}
        
        .header-subtitle {{ 
            font-size: 1.15em; 
            color: #6b7280;
            font-weight: 500;
        }}
        
        /* Main Signal Card */
        .main-signal-card {{ 
            background: rgba(255,255,255,0.98); 
            padding: 50px; 
            border-radius: 20px; 
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            backdrop-filter: blur(10px);
        }}
        
        .signal-grid {{ 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 60px; 
            align-items: center; 
            margin-bottom: 45px;
        }}
        
        .signal-display {{
            text-align: center;
        }}
        
        .signal-emoji {{ 
            font-size: 9em; 
            margin-bottom: 25px; 
            display: block;
            animation: pulse 2s ease-in-out infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}
        
        .recommendation-text {{ 
            font-size: 3.5em; 
            font-weight: 900; 
            color: {rec_color}; 
            margin-bottom: 15px;
            letter-spacing: -1px;
        }}
        
        .confidence-section {{
            padding: 25px;
        }}
        
        .confidence-label {{
            font-size: 1.3em;
            font-weight: 700;
            color: #374151;
            margin-bottom: 20px;
        }}
        
        .confidence-bar {{ 
            background: #e5e7eb; 
            height: 55px; 
            border-radius: 30px; 
            overflow: hidden; 
            margin-bottom: 18px;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .confidence-fill {{ 
            height: 100%; 
            background: linear-gradient(90deg, #667eea, #764ba2); 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            color: white; 
            font-weight: 800; 
            font-size: 1.4em; 
            min-width: 70px;
            transition: width 1s ease;
        }}
        
        /* Metrics Grid */
        .metrics-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 25px; 
            margin-bottom: 45px;
        }}
        
        .metric-card {{ 
            background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%); 
            padding: 30px; 
            border-radius: 16px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }}
        
        .metric-label {{ 
            font-size: 0.9em; 
            color: #6b7280; 
            margin-bottom: 14px; 
            font-weight: 600; 
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .metric-value {{ 
            font-size: 2.4em; 
            font-weight: 800; 
            color: #111827;
            letter-spacing: -0.5px;
        }}
        
        .metric-value.positive {{ color: #10b981; }} 
        .metric-value.negative {{ color: #ef4444; }} 
        .metric-value.neutral {{ color: #6b7280; }}
        
        /* Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-bottom: 35px;
        }}
        
        .stat-item {{
            background: linear-gradient(135deg, #e0e7ff 0%, #dbeafe 100%);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }}
        
        .stat-label {{
            font-size: 0.85em;
            color: #4b5563;
            font-weight: 600;
            margin-bottom: 8px;
            text-transform: uppercase;
        }}
        
        .stat-value {{
            font-size: 1.8em;
            font-weight: 700;
            color: #1f2937;
        }}
        
        /* Reason Box */
        .reason-box {{ 
            background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%); 
            padding: 28px; 
            border-radius: 16px; 
            margin-top: 35px;
            border-left: 5px solid #667eea;
        }}
        
        .reason-label {{
            font-weight: 700;
            font-size: 1.1em;
            color: #374151;
            margin-bottom: 10px;
            display: block;
        }}
        
        /* Data Table */
        .table-card {{
            background: rgba(255,255,255,0.98);
            padding: 40px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            backdrop-filter: blur(10px);
        }}
        
        .table-title {{
            font-size: 2em;
            font-weight: 800;
            color: #111827;
            margin-bottom: 25px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95em;
        }}
        
        thead {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }}
        
        th {{
            padding: 16px;
            text-align: left;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }}
        
        td {{
            padding: 14px 16px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        tbody tr:hover {{
            background: #f9fafb;
        }}
        
        tbody tr:last-child td {{
            border-bottom: none;
        }}
        
        td.price {{
            font-weight: 700;
            color: #111827;
        }}
        
        td.positive {{
            color: #10b981;
            font-weight: 600;
        }}
        
        td.negative {{
            color: #ef4444;
            font-weight: 600;
        }}
        
        td.neutral {{
            color: #6b7280;
            font-weight: 600;
        }}
        
        td.signal {{
            font-weight: 700;
        }}
        
        /* Charts Section */
        .charts-section {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(650px, 1fr)); 
            gap: 30px; 
            margin-top: 30px;
        }}
        
        .chart-card {{ 
            background: rgba(255,255,255,0.98); 
            padding: 40px; 
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            backdrop-filter: blur(10px);
        }}
        
        .chart-title {{
            font-size: 1.6em;
            font-weight: 800;
            color: #111827;
            margin-bottom: 25px;
        }}
        
        .chart-container {{ 
            position: relative; 
            height: 380px;
        }}
        
        /* Responsive */
        @media (max-width: 1200px) {{ 
            .signal-grid {{ 
                grid-template-columns: 1fr; 
                gap: 35px; 
            }} 
            
            h1 {{ 
                font-size: 2.8em; 
            }} 
            
            .recommendation-text {{ 
                font-size: 2.8em; 
            }}
            
            .charts-section {{
                grid-template-columns: 1fr;
            }}
        }}
        
        @media (max-width: 768px) {{
            .metrics-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            h1 {{
                font-size: 2.2em;
            }}
            
            .recommendation-text {{
                font-size: 2.2em;
            }}
            
            .signal-emoji {{
                font-size: 6em;
            }}
            
            table {{
                font-size: 0.85em;
            }}
            
            th, td {{
                padding: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Search Bar -->
        <div class="search-bar">
            <input type="text" id="symbolInput" placeholder="Ingresa símbolo (ej: AAPL, MSFT, ^IBEX)" value="{symbol}" />
            <button onclick="searchSymbol()">🔍 Buscar</button>
            <div class="limit-selector">
                <label for="limitSelect">Período:</label>
                <select id="limitSelect" onchange="searchSymbol()">
                    <option value="30">30 días</option>
                    <option value="60">60 días</option>
                    <option value="90">90 días</option>
                    <option value="180">6 meses</option>
                    <option value="365">1 año</option>
                </select>
            </div>
        </div>

        <!-- Header -->
        <header>
            <h1>📊 {symbol}</h1>
            <div class="header-subtitle">Última actualización: {current_date}</div>
        </header>

        <!-- Main Signal Card -->
        <div class="main-signal-card">
            <div class="signal-grid">
                <div class="signal-display">
                    <span class="signal-emoji">{emoji}</span>
                    <div class="recommendation-text">{recommendation}</div>
                </div>

                <div class="confidence-section">
                    <div class="confidence-label">Nivel de Confianza</div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: {confidence_pct}%;">
                            {confidence_pct}%
                        </div>
                    </div>
                    <div style="font-size: 0.95em; color: #6b7280; margin-top: 10px;">
                        Basado en análisis técnico de múltiples indicadores
                    </div>
                </div>
            </div>

            <!-- Metrics Grid -->
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">💰 Precio Actual</div>
                    <div class="metric-value">{latest_close}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">📈 Cambio Diario</div>
                    <div class="metric-value {latest_pct_class}">{latest_pct}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">📊 RSI (14)</div>
                    <div class="metric-value">{latest_rsi}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">📦 Volumen</div>
                    <div class="metric-value" style="font-size: 1.6em;">{latest_volume}</div>
                </div>
            </div>

            <!-- Additional Stats -->
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-label">🔝 Máximo</div>
                    <div class="stat-value">€{max_price:.2f}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">🔻 Mínimo</div>
                    <div class="stat-value">€{min_price:.2f}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">📊 Promedio</div>
                    <div class="stat-value">€{avg_price:.2f}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">📦 Vol. Promedio</div>
                    <div class="stat-value" style="font-size: 1.4em;">{int(avg_volume):,}</div>
                </div>
            </div>

            <!-- Reason Box -->
            <div class="reason-box">
                <span class="reason-label">📋 Análisis Detallado de Indicadores</span>
                <div style="color: #4b5563; line-height: 1.6;">{latest_reason}</div>
            </div>
        </div>

        <!-- Data Table -->
        <div class="table-card">
            <div class="table-title">📅 Historial Reciente (Últimos 10 Días)</div>
            <table>
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Precio</th>
                        <th>Cambio %</th>
                        <th>Volumen</th>
                        <th>RSI</th>
                        <th>Señal</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>

        <!-- Charts Section -->
        <div class="charts-section">
            <!-- Price Chart -->
            <div class="chart-card">
                <div class="chart-title">📈 Precio y Medias Móviles</div>
                <div class="chart-container">
                    <canvas id="priceChart"></canvas>
                </div>
            </div>

            <!-- RSI Chart -->
            <div class="chart-card">
                <div class="chart-title">📊 RSI - Índice de Fuerza Relativa</div>
                <div class="chart-container">
                    <canvas id="rsiChart"></canvas>
                </div>
            </div>

            <!-- Volume Chart -->
            <div class="chart-card">
                <div class="chart-title">📦 Volumen de Operaciones</div>
                <div class="chart-container">
                    <canvas id="volumeChart"></canvas>
                </div>
            </div>

            <!-- MACD Chart -->
            <div class="chart-card">
                <div class="chart-title">📉 MACD - Convergencia/Divergencia</div>
                <div class="chart-container">
                    <canvas id="macdChart"></canvas>
                </div>
            </div>

            <!-- Bollinger Bands Chart -->
            <div class="chart-card">
                <div class="chart-title">🎯 Bandas de Bollinger</div>
                <div class="chart-container">
                    <canvas id="bollingerChart"></canvas>
                </div>
            </div>

            <!-- OHLC Chart -->
            <div class="chart-card">
                <div class="chart-title">🕯️ Rango OHLC (Open-High-Low-Close)</div>
                <div class="chart-container">
                    <canvas id="ohlcChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Search function
        function searchSymbol() {{
            const symbol = document.getElementById('symbolInput').value.toUpperCase().trim();
            const limit = document.getElementById('limitSelect').value;
            if (!symbol) {{ 
                alert('Por favor ingresa un símbolo válido'); 
                return; 
            }}
            window.location.href = '/dashboard/' + symbol + '?limit=' + limit;
        }}

        // Data arrays
        const fechas = {fechas_json};
        const closes = {closes_json};
        const opens = {opens_json};
        const highs = {highs_json};
        const lows = {lows_json};
        const volumes = {volumes_json};
        const sma20s = {sma20s_json};
        const sma50s = {sma50s_json};
        const rsis = {rsis_json};
        const macds = {macds_json};
        const macd_signals = {macd_signals_json};
        const bb_uppers = {bb_uppers_json};
        const bb_lowers = {bb_lowers_json};

        // Common chart options
        const commonOptions = {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{
                    display: true,
                    position: 'top',
                    labels: {{
                        font: {{
                            family: 'Inter',
                            weight: '600'
                        }},
                        padding: 15
                    }}
                }},
                tooltip: {{
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {{
                        family: 'Inter',
                        size: 14,
                        weight: 'bold'
                    }},
                    bodyFont: {{
                        family: 'Inter',
                        size: 13
                    }}
                }}
            }},
            scales: {{
                x: {{
                    grid: {{
                        display: false
                    }},
                    ticks: {{
                        font: {{
                            family: 'Inter'
                        }}
                    }}
                }},
                y: {{
                    grid: {{
                        color: 'rgba(0, 0, 0, 0.05)'
                    }},
                    ticks: {{
                        font: {{
                            family: 'Inter'
                        }}
                    }}
                }}
            }}
        }};

        // 1. Price Chart with SMAs
        const priceCtx = document.getElementById('priceChart').getContext('2d');
        new Chart(priceCtx, {{
            type: 'line',
            data: {{
                labels: fechas,
                datasets: [
                    {{
                        label: 'Precio de Cierre',
                        data: closes,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 2,
                        pointHoverRadius: 6
                    }},
                    {{
                        label: 'SMA 20',
                        data: sma20s,
                        borderColor: '#f59e0b',
                        borderWidth: 2.5,
                        tension: 0.4,
                        borderDash: [8, 4],
                        fill: false,
                        pointRadius: 0
                    }},
                    {{
                        label: 'SMA 50',
                        data: sma50s,
                        borderColor: '#ef4444',
                        borderWidth: 2.5,
                        tension: 0.4,
                        borderDash: [8, 4],
                        fill: false,
                        pointRadius: 0
                    }}
                ]
            }},
            options: {{
                ...commonOptions,
                scales: {{
                    ...commonOptions.scales,
                    y: {{
                        ...commonOptions.scales.y,
                        beginAtZero: false
                    }}
                }}
            }}
        }});

        // 2. RSI Chart
        const rsiCtx = document.getElementById('rsiChart').getContext('2d');
        new Chart(rsiCtx, {{
            type: 'line',
            data: {{
                labels: fechas,
                datasets: [
                    {{
                        label: 'RSI (14)',
                        data: rsis,
                        borderColor: '#764ba2',
                        backgroundColor: 'rgba(118, 75, 162, 0.15)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 2,
                        pointHoverRadius: 6
                    }}
                ]
            }},
            options: {{
                ...commonOptions,
                plugins: {{
                    ...commonOptions.plugins,
                    annotation: {{
                        annotations: {{
                            line1: {{
                                type: 'line',
                                yMin: 70,
                                yMax: 70,
                                borderColor: '#ef4444',
                                borderWidth: 2,
                                borderDash: [6, 3],
                                label: {{
                                    content: 'Sobrecompra (70)',
                                    enabled: true,
                                    position: 'end'
                                }}
                            }},
                            line2: {{
                                type: 'line',
                                yMin: 30,
                                yMax: 30,
                                borderColor: '#10b981',
                                borderWidth: 2,
                                borderDash: [6, 3],
                                label: {{
                                    content: 'Sobreventa (30)',
                                    enabled: true,
                                    position: 'end'
                                }}
                            }}
                        }}
                    }}
                }},
                scales: {{
                    ...commonOptions.scales,
                    y: {{
                        ...commonOptions.scales.y,
                        min: 0,
                        max: 100
                    }}
                }}
            }}
        }});

        // 3. Volume Chart
        const volumeCtx = document.getElementById('volumeChart').getContext('2d');
        new Chart(volumeCtx, {{
            type: 'bar',
            data: {{
                labels: fechas,
                datasets: [
                    {{
                        label: 'Volumen',
                        data: volumes,
                        backgroundColor: 'rgba(102, 126, 234, 0.6)',
                        borderColor: '#667eea',
                        borderWidth: 1
                    }}
                ]
            }},
            options: {{
                ...commonOptions,
                scales: {{
                    ...commonOptions.scales,
                    y: {{
                        ...commonOptions.scales.y,
                        beginAtZero: true
                    }}
                }}
            }}
        }});

        // 4. MACD Chart
        const macdCtx = document.getElementById('macdChart').getContext('2d');
        new Chart(macdCtx, {{
            type: 'line',
            data: {{
                labels: fechas,
                datasets: [
                    {{
                        label: 'MACD',
                        data: macds,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: false,
                        pointRadius: 0
                    }},
                    {{
                        label: 'Señal MACD',
                        data: macd_signals,
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: false,
                        pointRadius: 0
                    }}
                ]
            }},
            options: commonOptions
        }});

        // 5. Bollinger Bands Chart
        const bollingerCtx = document.getElementById('bollingerChart').getContext('2d');
        new Chart(bollingerCtx, {{
            type: 'line',
            data: {{
                labels: fechas,
                datasets: [
                    {{
                        label: 'Precio',
                        data: closes,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: false,
                        pointRadius: 2
                    }},
                    {{
                        label: 'BB Superior',
                        data: bb_uppers,
                        borderColor: '#ef4444',
                        borderWidth: 2,
                        tension: 0.4,
                        borderDash: [5, 3],
                        fill: false,
                        pointRadius: 0
                    }},
                    {{
                        label: 'BB Inferior',
                        data: bb_lowers,
                        borderColor: '#10b981',
                        borderWidth: 2,
                        tension: 0.4,
                        borderDash: [5, 3],
                        fill: false,
                        pointRadius: 0
                    }}
                ]
            }},
            options: {{
                ...commonOptions,
                scales: {{
                    ...commonOptions.scales,
                    y: {{
                        ...commonOptions.scales.y,
                        beginAtZero: false
                    }}
                }}
            }}
        }});

        // 6. OHLC Chart (using error bars to simulate candles)
        const ohlcCtx = document.getElementById('ohlcChart').getContext('2d');
        new Chart(ohlcCtx, {{
            type: 'bar',
            data: {{
                labels: fechas,
                datasets: [
                    {{
                        label: 'Open',
                        data: opens,
                        backgroundColor: 'rgba(102, 126, 234, 0.3)',
                        borderColor: '#667eea',
                        borderWidth: 1
                    }},
                    {{
                        label: 'High',
                        data: highs,
                        backgroundColor: 'rgba(16, 185, 129, 0.3)',
                        borderColor: '#10b981',
                        borderWidth: 1
                    }},
                    {{
                        label: 'Low',
                        data: lows,
                        backgroundColor: 'rgba(239, 68, 68, 0.3)',
                        borderColor: '#ef4444',
                        borderWidth: 1
                    }},
                    {{
                        label: 'Close',
                        data: closes,
                        backgroundColor: 'rgba(118, 75, 162, 0.3)',
                        borderColor: '#764ba2',
                        borderWidth: 1
                    }}
                ]
            }},
            options: {{
                ...commonOptions,
                scales: {{
                    ...commonOptions.scales,
                    y: {{
                        ...commonOptions.scales.y,
                        beginAtZero: false
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    return html