"""
Predictor de precios usando Prophet de Meta.
Prophet es especializado en series temporales con estacionalidad y tendencias.
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional
import warnings

warnings.filterwarnings('ignore')


class ProphetPredictor:
    """
    Predictor de precios futuros usando Prophet de Facebook/Meta.
    Predice precio para los próximos N días considerando tendencias y estacionalidad.
    """
    
    def __init__(self):
        """Inicializa el predictor Prophet"""
        self.is_available = False
        self.model = None
        
        try:
            from prophet import Prophet
            self.Prophet = Prophet
            self.is_available = True
            print("✅ Prophet disponible")
        except ImportError:
            print("⚠️  Prophet no instalado. Ejecuta: pip install prophet")
            self.is_available = False
    
    def predict_next_days(self, data: pd.DataFrame, days: int = 5) -> Dict:
        """
        Predice precio para los próximos N días.
        
        Args:
            data: DataFrame con columnas 'date' y 'close'
            days: Número de días a predecir (default: 5)
            
        Returns:
            Dict con predicción de precio y cambio esperado
        """
        if not self.is_available:
            return {
                'predicted_price': None,
                'current_price': None,
                'expected_change_pct': 0.0,
                'signal': 'HOLD',
                'confidence': 'LOW',
                'reason': 'Prophet no disponible',
                'forecast_days': 0
            }
        
        if len(data) < 30:
            return {
                'predicted_price': None,
                'current_price': data.iloc[-1]['close'] if len(data) > 0 else None,
                'expected_change_pct': 0.0,
                'signal': 'HOLD',
                'confidence': 'LOW',
                'reason': 'Datos insuficientes (mínimo 30 días)',
                'forecast_days': 0
            }
        
        try:
            # Preparar datos para Prophet
            df = data[['date', 'close']].copy()
            df.columns = ['ds', 'y']
            
            # Asegurar que ds es datetime
            if not pd.api.types.is_datetime64_any_dtype(df['ds']):
                df['ds'] = pd.to_datetime(df['ds'])
            
            # Crear y entrenar modelo
            model = self.Prophet(
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=False,
                changepoint_prior_scale=0.05,
                seasonality_mode='multiplicative'
            )
            
            # Suprimir output de Prophet
            import logging
            logging.getLogger('prophet').setLevel(logging.ERROR)
            
            model.fit(df)
            
            # Hacer predicción
            future = model.make_future_dataframe(periods=days, freq='D')
            forecast = model.predict(future)
            
            # Extraer resultados
            current_price = float(df.iloc[-1]['y'])
            predicted_price = float(forecast.iloc[-1]['yhat'])
            
            # Calcular cambio esperado
            expected_change = predicted_price - current_price
            expected_change_pct = (expected_change / current_price) * 100
            
            # Determinar señal
            if expected_change_pct > 2:
                signal = 'BUY'
                confidence = 'HIGH' if expected_change_pct > 5 else 'MEDIUM'
            elif expected_change_pct < -2:
                signal = 'SELL'
                confidence = 'HIGH' if expected_change_pct < -5 else 'MEDIUM'
            else:
                signal = 'HOLD'
                confidence = 'LOW'
            
            # Límites de predicción (intervalo de confianza)
            lower_bound = float(forecast.iloc[-1]['yhat_lower'])
            upper_bound = float(forecast.iloc[-1]['yhat_upper'])
            
            return {
                'predicted_price': round(predicted_price, 2),
                'current_price': round(current_price, 2),
                'expected_change': round(expected_change, 2),
                'expected_change_pct': round(expected_change_pct, 2),
                'signal': signal,
                'confidence': confidence,
                'reason': f'Prophet predice {"subida" if signal == "BUY" else "bajada" if signal == "SELL" else "lateral"} de {abs(expected_change_pct):.1f}% en {days} días',
                'forecast_days': days,
                'confidence_interval': {
                    'lower': round(lower_bound, 2),
                    'upper': round(upper_bound, 2)
                }
            }
        
        except Exception as e:
            print(f"❌ Error en Prophet: {e}")
            return {
                'predicted_price': None,
                'current_price': data.iloc[-1]['close'] if len(data) > 0 else None,
                'expected_change_pct': 0.0,
                'signal': 'HOLD',
                'confidence': 'LOW',
                'reason': f'Error: {str(e)}',
                'forecast_days': 0
            }
    
    def get_trend_strength(self, data: pd.DataFrame) -> Dict:
        """
        Analiza la fuerza de la tendencia actual usando Prophet.
        
        Args:
            data: DataFrame con 'date' y 'close'
            
        Returns:
            Dict con información de tendencia
        """
        if not self.is_available or len(data) < 30:
            return {
                'trend': 'unknown',
                'strength': 0.0,
                'confidence': 'LOW'
            }
        
        try:
            df = data[['date', 'close']].copy()
            df.columns = ['ds', 'y']
            
            if not pd.api.types.is_datetime64_any_dtype(df['ds']):
                df['ds'] = pd.to_datetime(df['ds'])
            
            model = self.Prophet(
                daily_seasonality=False,
                weekly_seasonality=False,
                yearly_seasonality=False
            )
            
            import logging
            logging.getLogger('prophet').setLevel(logging.ERROR)
            
            model.fit(df)
            forecast = model.predict(df)
            
            # Analizar componente de tendencia
            trend = forecast['trend'].values
            trend_change = (trend[-1] - trend[0]) / trend[0] * 100
            
            if abs(trend_change) > 10:
                strength = 'STRONG'
            elif abs(trend_change) > 5:
                strength = 'MODERATE'
            else:
                strength = 'WEAK'
            
            direction = 'BULLISH' if trend_change > 0 else 'BEARISH'
            
            return {
                'trend': direction,
                'strength': strength,
                'change_pct': round(trend_change, 2),
                'confidence': 'HIGH' if abs(trend_change) > 10 else 'MEDIUM'
            }
        
        except Exception as e:
            return {
                'trend': 'unknown',
                'strength': 'WEAK',
                'change_pct': 0.0,
                'confidence': 'LOW'
            }
    
    def get_prophet_score_0_10(self, data: pd.DataFrame, days: int = 5) -> float:
        """
        Retorna score de 0 a 10 basado en predicción de Prophet.
        
        Args:
            data: DataFrame con datos históricos
            days: Días a predecir
            
        Returns:
            Score de 0 (muy bajista) a 10 (muy alcista)
        """
        prediction = self.predict_next_days(data, days)
        
        if not prediction['expected_change_pct']:
            return 5.0  # Neutral
        
        # Convertir cambio porcentual a score 0-10
        # -10% o menos = 0, +10% o más = 10
        change_pct = prediction['expected_change_pct']
        
        if change_pct <= -10:
            score = 0.0
        elif change_pct >= 10:
            score = 10.0
        else:
            # Mapear linealmente [-10, 10] a [0, 10]
            score = (change_pct + 10) / 2
        
        return round(score, 1)


# Singleton global
_prophet_instance = None

def get_prophet_predictor() -> ProphetPredictor:
    """Retorna instancia singleton de Prophet"""
    global _prophet_instance
    if _prophet_instance is None:
        _prophet_instance = ProphetPredictor()
    return _prophet_instance
