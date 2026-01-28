"""
Sistema de scoring híbrido que combina:
1. Análisis técnico Danelfin (indicadores tradicionales)
2. Machine Learning XGBoost (predicción de tendencia)
3. Sentiment Analysis FinBERT (análisis de noticias)
4. Prophet (predicción de precio con series temporales)
"""
from typing import Dict, Optional
import pandas as pd
from app.scoring.danelfin_score import DanelfinScorer
from app.models.predictor import MLPredictor
from app.scoring.sentiment import get_finbert_analyzer
from app.models.prophet_predictor import get_prophet_predictor


class HybridScorer:
    """
    Sistema de scoring híbrido que integra múltiples metodologías de análisis.
    
    Pesos de componentes:
    - Technical (Danelfin): 25% - Indicadores técnicos tradicionales
    - ML Prediction: 40% - Machine Learning predictivo (más importante)
    - Sentiment: 15% - Análisis de noticias con FinBERT
    - Prophet: 20% - Predicción de precio con series temporales
    """
    
    def __init__(self, ml_model_path: Optional[str] = None, enable_sentiment: bool = False):
        """
        Args:
            ml_model_path: Ruta al modelo ML pre-entrenado
            enable_sentiment: Si True, habilita análisis de sentiment (requiere noticias)
        """
        self.danelfin = DanelfinScorer()
        self.ml_predictor = MLPredictor(model_path=ml_model_path)
        self.prophet = get_prophet_predictor()
        
        # Sentiment es opcional (requiere textos de noticias)
        self.enable_sentiment = enable_sentiment
        if enable_sentiment:
            self.sentiment_analyzer = get_finbert_analyzer()
        
        # Pesos de cada componente (deben sumar 1.0)
        self.weights = {
            'technical': 0.25,     # Danelfin tradicional
            'ml_prediction': 0.40, # ML es el más importante
            'sentiment': 0.15,     # Sentiment de noticias
            'prophet': 0.20        # Predicción de precio
        }
        
        print("🚀 HybridScorer inicializado")
        print(f"   ML Model: {'✅ Entrenado' if self.ml_predictor.is_trained else '⚠️ Básico'}")
        print(f"   Prophet: {'✅ Disponible' if self.prophet.is_available else '❌ No disponible'}")
        print(f"   Sentiment: {'✅ Habilitado' if enable_sentiment else '❌ Deshabilitado'}")
    
    def calculate_hybrid_score(self, 
                               data: pd.DataFrame, 
                               news_text: Optional[str] = None) -> Dict:
        """
        Calcula score híbrido combinando todas las metodologías.
        
        Args:
            data: DataFrame con datos OHLCV e indicadores técnicos
            news_text: Texto de noticias para análisis de sentiment (opcional)
            
        Returns:
            Dict con score total, señal, confianza y desglose de componentes
        """
        if len(data) < 50:
            return {
                'total_score': 5.0,
                'rating': 'NEUTRAL',
                'signal': 'HOLD',
                'confidence': 'LOW',
                'reason': 'Datos insuficientes para análisis híbrido',
                'components': {}
            }
        
        # 1. Score técnico Danelfin (25%)
        danelfin_result = self.danelfin.calculate_score(data)
        technical_score = danelfin_result['total_score']
        
        # 2. Predicción ML (40%)
        ml_result = self.ml_predictor.predict_trend(data)
        ml_score = ml_result['ml_score']
        ml_signal = ml_result['prediction']
        
        # 3. Predicción Prophet (20%)
        prophet_result = self.prophet.predict_next_days(data, days=5)
        prophet_score = self.prophet.get_prophet_score_0_10(data, days=5)
        
        # 4. Sentiment (15%) - solo si está habilitado y hay texto
        if self.enable_sentiment and news_text:
            sentiment_result = self.sentiment_analyzer.analyze_text(news_text)
            sentiment_score = self.sentiment_analyzer.get_sentiment_score_0_10(news_text)
        else:
            sentiment_result = {'sentiment': 'neutral', 'score': 0.0}
            sentiment_score = 5.0  # Neutral si no hay datos
        
        # Calcular score total ponderado
        total_score = (
            technical_score * self.weights['technical'] +
            ml_score * self.weights['ml_prediction'] +
            sentiment_score * self.weights['sentiment'] +
            prophet_score * self.weights['prophet']
        )
        
        total_score = round(total_score, 1)
        
        # Determinar señal final (ML tiene más peso)
        if ml_signal == 'BUY' and total_score >= 6.0:
            final_signal = 'BUY'
        elif ml_signal == 'SELL' and total_score <= 5.0:
            final_signal = 'SELL'
        elif total_score >= 7.0:
            final_signal = 'BUY'
        elif total_score <= 4.0:
            final_signal = 'SELL'
        else:
            final_signal = 'HOLD'
        
        # Calcular confianza
        confidence = self._calculate_confidence([
            danelfin_result,
            ml_result,
            prophet_result,
            sentiment_result
        ])
        
        # Rating basado en score total
        rating = self._get_rating(total_score)
        
        # Generar razones
        reasons = self._generate_reasons(
            danelfin_result, ml_result, prophet_result, 
            sentiment_result, final_signal
        )
        
        return {
            'total_score': total_score,
            'rating': rating,
            'signal': final_signal,
            'confidence': confidence,
            'reason': reasons[0] if reasons else 'Análisis híbrido completado',
            'components': {
                'technical': {
                    'score': round(technical_score, 1),
                    'weight': f"{self.weights['technical']*100:.0f}%",
                    'contribution': round(technical_score * self.weights['technical'], 1),
                    'sub_scores': danelfin_result
                },
                'ml_prediction': {
                    'score': round(ml_score, 1),
                    'weight': f"{self.weights['ml_prediction']*100:.0f}%",
                    'contribution': round(ml_score * self.weights['ml_prediction'], 1),
                    'signal': ml_signal,
                    'probability': ml_result['probability'],
                    'details': ml_result
                },
                'prophet': {
                    'score': round(prophet_score, 1),
                    'weight': f"{self.weights['prophet']*100:.0f}%",
                    'contribution': round(prophet_score * self.weights['prophet'], 1),
                    'predicted_change_pct': prophet_result.get('expected_change_pct', 0),
                    'details': prophet_result
                },
                'sentiment': {
                    'score': round(sentiment_score, 1),
                    'weight': f"{self.weights['sentiment']*100:.0f}%",
                    'contribution': round(sentiment_score * self.weights['sentiment'], 1),
                    'sentiment': sentiment_result.get('sentiment', 'neutral'),
                    'enabled': self.enable_sentiment,
                    'details': sentiment_result
                }
            },
            'methodology': 'Hybrid AI: Danelfin + XGBoost + Prophet + FinBERT'
        }
    
    def _calculate_confidence(self, results: list) -> str:
        """Calcula confianza basada en consenso de señales"""
        confidences = []
        
        for result in results:
            if isinstance(result, dict):
                conf = result.get('confidence', 'LOW')
                if conf == 'HIGH':
                    confidences.append(3)
                elif conf == 'MEDIUM':
                    confidences.append(2)
                else:
                    confidences.append(1)
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 1
        
        if avg_confidence >= 2.5:
            return 'HIGH'
        elif avg_confidence >= 1.5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _get_rating(self, score: float) -> str:
        """Convierte score numérico a rating"""
        if score >= 8.0:
            return 'STRONG BUY'
        elif score >= 7.0:
            return 'BUY'
        elif score >= 6.0:
            return 'MODERATE BUY'
        elif score >= 5.0:
            return 'NEUTRAL'
        elif score >= 4.0:
            return 'MODERATE SELL'
        elif score >= 3.0:
            return 'SELL'
        else:
            return 'STRONG SELL'
    
    def _generate_reasons(self, danelfin_result, ml_result, 
                         prophet_result, sentiment_result, signal) -> list:
        """Genera lista de razones para la recomendación"""
        reasons = []
        
        # Razón de ML (más importante)
        if ml_result['prediction'] == 'BUY':
            reasons.append(f"🤖 ML predice subida con {ml_result['probability']*100:.0f}% probabilidad")
        elif ml_result['prediction'] == 'SELL':
            reasons.append(f"🤖 ML predice bajada con {(1-ml_result['probability'])*100:.0f}% probabilidad")
        
        # Razón de Prophet
        expected_change = prophet_result.get('expected_change_pct', 0)
        if expected_change != 0:
            direction = "alza" if expected_change > 0 else "caída"
            reasons.append(f"📈 Prophet proyecta {direction} de {abs(expected_change):.1f}% en 5 días")
        
        # Razón técnica
        tech_score = danelfin_result['total_score']
        if tech_score >= 7:
            reasons.append(f"✅ Indicadores técnicos fuertes ({tech_score}/10)")
        elif tech_score <= 4:
            reasons.append(f"⚠️ Indicadores técnicos débiles ({tech_score}/10)")
        
        # Razón de sentiment (si disponible)
        if sentiment_result.get('sentiment') == 'positive':
            reasons.append(f"📰 Sentiment de noticias positivo")
        elif sentiment_result.get('sentiment') == 'negative':
            reasons.append(f"📰 Sentiment de noticias negativo")
        
        return reasons
    
    def get_feature_importance(self) -> Dict:
        """Retorna importancia de features del modelo ML"""
        return self.ml_predictor.get_feature_importance()


# Singleton global
_hybrid_scorer_instance = None

def get_hybrid_scorer(ml_model_path: Optional[str] = None, 
                     enable_sentiment: bool = False) -> HybridScorer:
    """
    Retorna instancia singleton de HybridScorer.
    
    Args:
        ml_model_path: Ruta al modelo ML
        enable_sentiment: Habilitar análisis de sentiment
    """
    global _hybrid_scorer_instance
    if _hybrid_scorer_instance is None:
        _hybrid_scorer_instance = HybridScorer(
            ml_model_path=ml_model_path,
            enable_sentiment=enable_sentiment
        )
    return _hybrid_scorer_instance
