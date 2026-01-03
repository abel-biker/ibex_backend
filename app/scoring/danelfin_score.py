"""
Sistema de scoring tipo Danelfin (0-10) para acciones del IBEX 35.
Combina análisis técnico, fundamental y de momentum.
"""
from typing import Dict, Optional
import pandas as pd
import numpy as np


class DanelfinScorer:
    """
    Calcula un score de 0 a 10 para una acción basado en múltiples factores:
    - Análisis técnico (40%): RSI, MACD, Bandas de Bollinger, Medias móviles
    - Momentum (30%): Tendencias de precio, volumen relativo
    - Sentiment de mercado (30%): Posición vs máximos/mínimos, volatilidad
    """
    
    def __init__(self):
        self.weights = {
            'technical': 0.40,
            'momentum': 0.30,
            'sentiment': 0.30
        }
    
    def calculate_score(self, data: pd.DataFrame) -> Dict:
        """
        Calcula el score Danelfin completo para una acción.
        
        Args:
            data: DataFrame con columnas OHLCV y indicadores técnicos calculados
            
        Returns:
            Dict con score total y sub-scores por categoría
        """
        if len(data) < 50:
            return {
                'total_score': 5.0,
                'rating': 'NEUTRAL',
                'technical_score': 5.0,
                'momentum_score': 5.0,
                'sentiment_score': 5.0,
                'confidence': 'LOW',
                'signals': ['Datos insuficientes para análisis completo']
            }
        
        technical_score = self._calculate_technical_score(data)
        momentum_score = self._calculate_momentum_score(data)
        sentiment_score = self._calculate_sentiment_score(data)
        
        total_score = (
            technical_score * self.weights['technical'] +
            momentum_score * self.weights['momentum'] +
            sentiment_score * self.weights['sentiment']
        )
        
        # Redondear a 1 decimal
        total_score = round(total_score, 1)
        
        return {
            'total_score': total_score,
            'rating': self._get_rating(total_score),
            'technical_score': round(technical_score, 1),
            'momentum_score': round(momentum_score, 1),
            'sentiment_score': round(sentiment_score, 1),
            'confidence': self._get_confidence(data),
            'signals': self._generate_signals(data, total_score)
        }
    
    def _calculate_technical_score(self, data: pd.DataFrame) -> float:
        """Análisis técnico: RSI, MACD, MA, Bollinger Bands"""
        score = 5.0  # neutral
        points = []
        
        latest = data.iloc[-1]
        
        # RSI (0-3 puntos)
        if 'rsi' in data.columns and pd.notna(latest['rsi']):
            rsi = latest['rsi']
            if rsi < 30:
                points.append(3.0)  # Sobreventa = oportunidad de compra
            elif rsi < 40:
                points.append(2.0)
            elif 40 <= rsi <= 60:
                points.append(1.0)  # Zona neutral
            elif 60 < rsi < 70:
                points.append(0.5)
            else:  # rsi >= 70
                points.append(0.0)  # Sobrecompra = señal negativa
        
        # MACD (0-2.5 puntos)
        if 'macd' in data.columns and 'macd_signal' in data.columns:
            macd = latest.get('macd')
            macd_signal = latest.get('macd_signal')
            
            if pd.notna(macd) and pd.notna(macd_signal):
                if macd > macd_signal and macd > 0:
                    points.append(2.5)  # Tendencia alcista fuerte
                elif macd > macd_signal:
                    points.append(1.5)  # Cruce alcista
                elif macd < macd_signal and macd < 0:
                    points.append(0.0)  # Tendencia bajista fuerte
                else:
                    points.append(0.5)  # Cruce bajista
        
        # Medias móviles (0-2.5 puntos)
        if 'sma_20' in data.columns and 'sma_50' in data.columns:
            close = latest['close']
            sma_20 = latest.get('sma_20')
            sma_50 = latest.get('sma_50')
            
            if pd.notna(sma_20) and pd.notna(sma_50):
                # Golden cross / Death cross
                if close > sma_20 > sma_50:
                    points.append(2.5)  # Tendencia alcista
                elif close > sma_20 or close > sma_50:
                    points.append(1.5)  # Señal mixta alcista
                elif close < sma_20 < sma_50:
                    points.append(0.0)  # Tendencia bajista
                else:
                    points.append(0.5)  # Señal mixta bajista
        
        # Bollinger Bands (0-2 puntos)
        if 'bb_lower' in data.columns and 'bb_upper' in data.columns:
            close = latest['close']
            bb_lower = latest.get('bb_lower')
            bb_middle = latest.get('bb_middle')
            bb_upper = latest.get('bb_upper')
            
            if all(pd.notna(x) for x in [bb_lower, bb_middle, bb_upper]):
                bb_range = bb_upper - bb_lower
                position = (close - bb_lower) / bb_range if bb_range > 0 else 0.5
                
                if position < 0.2:
                    points.append(2.0)  # Cerca de banda inferior = compra
                elif position < 0.4:
                    points.append(1.5)
                elif 0.4 <= position <= 0.6:
                    points.append(1.0)  # Zona neutral
                elif position > 0.8:
                    points.append(0.0)  # Cerca de banda superior = venta
                else:
                    points.append(0.5)
        
        if points:
            score = sum(points) / len(points) * 10 / 3  # Normalizar a 0-10
        
        return min(10.0, max(0.0, score))
    
    def _calculate_momentum_score(self, data: pd.DataFrame) -> float:
        """Análisis de momentum y tendencia"""
        score = 5.0
        points = []
        
        # Rendimiento reciente (0-4 puntos)
        if len(data) >= 20:
            returns_5d = (data['close'].iloc[-1] / data['close'].iloc[-6] - 1) * 100
            returns_20d = (data['close'].iloc[-1] / data['close'].iloc[-21] - 1) * 100
            
            # 5 días
            if returns_5d > 5:
                points.append(2.0)
            elif returns_5d > 2:
                points.append(1.5)
            elif returns_5d > 0:
                points.append(1.0)
            elif returns_5d > -2:
                points.append(0.5)
            else:
                points.append(0.0)
            
            # 20 días
            if returns_20d > 10:
                points.append(2.0)
            elif returns_20d > 5:
                points.append(1.5)
            elif returns_20d > 0:
                points.append(1.0)
            elif returns_20d > -5:
                points.append(0.5)
            else:
                points.append(0.0)
        
        # Volumen relativo (0-3 puntos)
        if 'volume' in data.columns and len(data) >= 20:
            avg_volume_20 = data['volume'].iloc[-21:-1].mean()
            current_volume = data['volume'].iloc[-1]
            
            if pd.notna(avg_volume_20) and avg_volume_20 > 0:
                volume_ratio = current_volume / avg_volume_20
                
                if volume_ratio > 2:
                    points.append(3.0)  # Alto volumen = confirmación
                elif volume_ratio > 1.5:
                    points.append(2.0)
                elif volume_ratio > 1:
                    points.append(1.5)
                elif volume_ratio > 0.7:
                    points.append(1.0)
                else:
                    points.append(0.5)  # Bajo volumen = señal débil
        
        # Tendencia de máximos y mínimos (0-3 puntos)
        if len(data) >= 10:
            recent_highs = data['high'].iloc[-10:]
            recent_lows = data['low'].iloc[-10:]
            
            # Contar máximos y mínimos crecientes
            higher_highs = sum(recent_highs.iloc[i] > recent_highs.iloc[i-1] 
                             for i in range(1, len(recent_highs)))
            higher_lows = sum(recent_lows.iloc[i] > recent_lows.iloc[i-1] 
                            for i in range(1, len(recent_lows)))
            
            trend_score = (higher_highs + higher_lows) / 18  # Max 18 (9+9)
            points.append(trend_score * 3)
        
        if points:
            score = sum(points) / len(points) * 10 / 3  # Normalizar a 0-10
        
        return min(10.0, max(0.0, score))
    
    def _calculate_sentiment_score(self, data: pd.DataFrame) -> float:
        """Análisis de sentiment: posición vs máximos/mínimos, volatilidad"""
        score = 5.0
        points = []
        
        latest = data.iloc[-1]
        
        # Distancia a máximos/mínimos de 52 semanas (0-4 puntos)
        if len(data) >= 252:
            high_52w = data['high'].iloc[-252:].max()
            low_52w = data['low'].iloc[-252:].min()
            current_price = latest['close']
            
            if high_52w > low_52w:
                position = (current_price - low_52w) / (high_52w - low_52w)
                
                if position < 0.2:
                    points.append(4.0)  # Cerca de mínimos = oportunidad
                elif position < 0.4:
                    points.append(3.0)
                elif 0.4 <= position <= 0.6:
                    points.append(2.0)  # Zona media
                elif position < 0.8:
                    points.append(1.0)
                else:
                    points.append(0.0)  # Cerca de máximos = cuidado
        elif len(data) >= 60:
            # Fallback a 3 meses
            high_3m = data['high'].iloc[-60:].max()
            low_3m = data['low'].iloc[-60:].min()
            current_price = latest['close']
            
            if high_3m > low_3m:
                position = (current_price - low_3m) / (high_3m - low_3m)
                points.append(position * 2 + 1)  # 1-3 puntos
        
        # Volatilidad (0-3 puntos) - menor volatilidad = mejor
        if len(data) >= 20:
            returns = data['close'].pct_change().iloc[-20:]
            volatility = returns.std() * 100
            
            if volatility < 1:
                points.append(3.0)  # Baja volatilidad
            elif volatility < 2:
                points.append(2.0)
            elif volatility < 3:
                points.append(1.5)
            elif volatility < 5:
                points.append(1.0)
            else:
                points.append(0.5)  # Alta volatilidad
        
        # Racha de días positivos/negativos (0-3 puntos)
        if len(data) >= 10:
            last_10_changes = data['close'].diff().iloc[-10:]
            positive_days = (last_10_changes > 0).sum()
            
            if positive_days >= 7:
                points.append(3.0)
            elif positive_days >= 6:
                points.append(2.5)
            elif positive_days >= 5:
                points.append(2.0)
            elif positive_days >= 4:
                points.append(1.5)
            else:
                points.append(0.5)
        
        if points:
            score = sum(points) / len(points) * 10 / 4  # Normalizar a 0-10
        
        return min(10.0, max(0.0, score))
    
    def _get_rating(self, score: float) -> str:
        """Convierte score numérico a rating textual"""
        if score >= 8.0:
            return 'STRONG BUY'
        elif score >= 6.5:
            return 'BUY'
        elif score >= 5.5:
            return 'HOLD'
        elif score >= 4.0:
            return 'NEUTRAL'
        elif score >= 2.5:
            return 'SELL'
        else:
            return 'STRONG SELL'
    
    def _get_confidence(self, data: pd.DataFrame) -> str:
        """Evalúa la confianza del análisis basado en cantidad de datos"""
        if len(data) >= 252:
            return 'HIGH'
        elif len(data) >= 60:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_signals(self, data: pd.DataFrame, score: float) -> list:
        """Genera señales específicas basadas en el análisis"""
        signals = []
        latest = data.iloc[-1]
        
        # RSI
        if 'rsi' in data.columns and pd.notna(latest['rsi']):
            rsi = latest['rsi']
            if rsi < 30:
                signals.append(f"RSI en sobreventa ({rsi:.1f}) - Oportunidad de compra")
            elif rsi > 70:
                signals.append(f"RSI en sobrecompra ({rsi:.1f}) - Considerar venta")
        
        # MACD
        if 'macd' in data.columns and 'macd_signal' in data.columns:
            macd = latest.get('macd')
            macd_signal = latest.get('macd_signal')
            if pd.notna(macd) and pd.notna(macd_signal):
                if len(data) >= 2:
                    prev_macd = data['macd'].iloc[-2]
                    prev_signal = data['macd_signal'].iloc[-2]
                    
                    if prev_macd <= prev_signal and macd > macd_signal:
                        signals.append("MACD cruzó al alza - Señal alcista")
                    elif prev_macd >= prev_signal and macd < macd_signal:
                        signals.append("MACD cruzó a la baja - Señal bajista")
        
        # Medias móviles
        if 'sma_20' in data.columns and 'sma_50' in data.columns:
            close = latest['close']
            sma_20 = latest.get('sma_20')
            sma_50 = latest.get('sma_50')
            
            if pd.notna(sma_20) and pd.notna(sma_50):
                if close > sma_20 and close > sma_50:
                    signals.append("Precio por encima de SMA 20 y 50 - Tendencia alcista")
                elif close < sma_20 and close < sma_50:
                    signals.append("Precio por debajo de SMA 20 y 50 - Tendencia bajista")
        
        # Volumen
        if 'volume' in data.columns and len(data) >= 20:
            avg_volume = data['volume'].iloc[-21:-1].mean()
            current_volume = latest['volume']
            if pd.notna(avg_volume) and avg_volume > 0:
                if current_volume > avg_volume * 2:
                    signals.append(f"Volumen excepcional ({current_volume/avg_volume:.1f}x promedio)")
        
        # Score general
        if score >= 7:
            signals.append(f"⭐ Score excelente ({score}/10) - Fuerte potencial alcista")
        elif score <= 3:
            signals.append(f"⚠️ Score bajo ({score}/10) - Señales bajistas predominantes")
        
        return signals if signals else ["Sin señales destacadas"]


def calculate_danelfin_score(data: pd.DataFrame) -> Dict:
    """
    Función helper para calcular el score Danelfin de una acción.
    
    Args:
        data: DataFrame con datos OHLCV y indicadores
        
    Returns:
        Dict con score y detalles del análisis
    """
    scorer = DanelfinScorer()
    return scorer.calculate_score(data)
