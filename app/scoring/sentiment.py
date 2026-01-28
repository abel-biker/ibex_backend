"""
Análisis de sentiment financiero usando FinBERT.
FinBERT es un modelo BERT pre-entrenado específicamente para textos financieros.
"""
from typing import Dict, Optional
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import logging

# Suprimir warnings de transformers
logging.getLogger("transformers").setLevel(logging.ERROR)


class FinBERTSentiment:
    """
    Analizador de sentiment financiero usando FinBERT de ProsusAI.
    Analiza texto (noticias, reportes) y retorna sentiment positivo/negativo/neutral.
    """
    
    def __init__(self, use_gpu: bool = False):
        """
        Args:
            use_gpu: Si True, usa GPU si está disponible
        """
        self.model_name = "ProsusAI/finbert"
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        self.is_loaded = False
        
        # Lazy loading - solo carga cuando se use por primera vez
        print("📊 FinBERT Sentiment Analyzer inicializado (lazy loading)")
    
    def _load_model(self):
        """Carga el modelo FinBERT (solo cuando sea necesario)"""
        if self.is_loaded:
            return
        
        try:
            print(f"🔄 Cargando modelo FinBERT en {self.device}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            self.is_loaded = True
            print("✅ FinBERT cargado exitosamente")
        except Exception as e:
            print(f"❌ Error cargando FinBERT: {e}")
            print("💡 Ejecuta: pip install transformers torch")
            self.is_loaded = False
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analiza el sentiment de un texto financiero.
        
        Args:
            text: Texto a analizar (noticia, reporte, tweet, etc.)
            
        Returns:
            Dict con sentiment, score (-1 a +1) y confianza
        """
        if not text or len(text.strip()) < 10:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'reason': 'Texto insuficiente'
            }
        
        # Cargar modelo si no está cargado
        if not self.is_loaded:
            self._load_model()
        
        if not self.is_loaded:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'reason': 'Modelo no disponible'
            }
        
        try:
            # Tokenizar
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                truncation=True, 
                max_length=512,
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Predecir
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Resultados
            probs_cpu = probs.cpu().numpy()[0]
            labels = ['negative', 'neutral', 'positive']
            
            sentiment_idx = int(probs.argmax().item())
            sentiment = labels[sentiment_idx]
            
            # Score: -1 (muy negativo) a +1 (muy positivo)
            sentiment_score = float(probs_cpu[2] - probs_cpu[0])  # positive - negative
            confidence = float(probs_cpu[sentiment_idx])
            
            return {
                'sentiment': sentiment,
                'score': round(sentiment_score, 3),
                'confidence': round(confidence, 3),
                'reason': f'Sentiment {sentiment} detectado con {confidence*100:.1f}% confianza',
                'probabilities': {
                    'negative': round(float(probs_cpu[0]), 3),
                    'neutral': round(float(probs_cpu[1]), 3),
                    'positive': round(float(probs_cpu[2]), 3)
                }
            }
        
        except Exception as e:
            print(f"❌ Error en análisis de sentiment: {e}")
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'reason': f'Error: {str(e)}'
            }
    
    def analyze_news_batch(self, news_list: list) -> Dict:
        """
        Analiza múltiples noticias y retorna sentiment agregado.
        
        Args:
            news_list: Lista de textos de noticias
            
        Returns:
            Dict con sentiment promedio
        """
        if not news_list:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'count': 0
            }
        
        results = [self.analyze_text(news) for news in news_list]
        
        # Promediar scores
        avg_score = sum(r['score'] for r in results) / len(results)
        avg_confidence = sum(r['confidence'] for r in results) / len(results)
        
        # Determinar sentiment global
        if avg_score > 0.2:
            sentiment = 'positive'
        elif avg_score < -0.2:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': round(avg_score, 3),
            'confidence': round(avg_confidence, 3),
            'count': len(results),
            'reason': f'Análisis de {len(results)} noticias: {sentiment}'
        }
    
    def get_sentiment_score_0_10(self, text: Optional[str] = None) -> float:
        """
        Retorna score de 0 a 10 para integrar con Danelfin.
        
        Args:
            text: Texto a analizar (opcional)
            
        Returns:
            Score de 0 (muy negativo) a 10 (muy positivo)
        """
        if not text:
            return 5.0  # Neutral
        
        result = self.analyze_text(text)
        
        # Convertir score [-1, +1] a [0, 10]
        score_0_10 = (result['score'] + 1) * 5
        
        return round(score_0_10, 1)


# Singleton global (lazy loading)
_finbert_instance = None

def get_finbert_analyzer() -> FinBERTSentiment:
    """Retorna instancia singleton de FinBERT"""
    global _finbert_instance
    if _finbert_instance is None:
        _finbert_instance = FinBERTSentiment()
    return _finbert_instance
