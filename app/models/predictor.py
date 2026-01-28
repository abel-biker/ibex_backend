"""
ML Predictor usando XGBoost para predicciones de tendencia.
Basado en el TFM de modelos predictivos para series financieras.
"""
import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Optional
import xgboost as xgb
from pathlib import Path


class MLPredictor:
    """
    Predictor de tendencias usando XGBoost entrenado.
    Predice si el precio subirá o bajará en los próximos 15 días.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Args:
            model_path: Ruta al modelo .pkl entrenado. Si None, busca en ubicación por defecto.
        """
        self.model = None
        self.is_trained = False
        self.feature_names = [
            'rsi', 'macd', 'macd_signal', 'sma_20', 'sma_50', 
            'bb_upper', 'bb_middle', 'bb_lower',
            'volume', 'close'
        ]
        
        # Si no se especifica ruta, buscar en ubicación por defecto
        if model_path is None:
            default_path = "data/models/ibex_xgboost.pkl"
            if os.path.exists(default_path):
                model_path = default_path
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            print("⚠️  No se encontró modelo pre-entrenado. Usando modelo básico.")
            self._create_basic_model()
    
    def _create_basic_model(self):
        """Crea un modelo XGBoost básico con parámetros por defecto"""
        self.model = xgb.XGBClassifier(
            objective='binary:logistic',
            eval_metric='logloss',
            use_label_encoder=False,
            random_state=42,
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8
        )
        self.is_trained = False
    
    def load_model(self, model_path: str):
        """Carga un modelo previamente entrenado"""
        try:
            self.model = joblib.load(model_path)
            self.is_trained = True
            print(f"✅ Modelo cargado desde: {model_path}")
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            self._create_basic_model()
    
    def save_model(self, model_path: str):
        """Guarda el modelo entrenado"""
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(self.model, model_path)
        print(f"✅ Modelo guardado en: {model_path}")
    
    def _extract_features(self, data: pd.DataFrame) -> np.ndarray:
        """
        Extrae features del DataFrame de datos de mercado.
        
        Args:
            data: DataFrame con indicadores técnicos calculados
            
        Returns:
            Array con features para el modelo
        """
        latest = data.iloc[-1]
        
        features = []
        for feature_name in self.feature_names:
            if feature_name in data.columns:
                value = latest.get(feature_name, 0)
                # Reemplazar NaN con 0
                features.append(0 if pd.isna(value) else float(value))
            else:
                features.append(0)
        
        return np.array([features])
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
              X_test: Optional[np.ndarray] = None, 
              y_test: Optional[np.ndarray] = None):
        """
        Entrena el modelo con datos históricos.
        
        Args:
            X_train: Features de entrenamiento
            y_train: Labels (0=bajará, 1=subirá)
            X_test: Features de test (opcional)
            y_test: Labels de test (opcional)
        """
        from sklearn.metrics import accuracy_score, f1_score, roc_curve
        
        print("🔄 Entrenando modelo XGBoost...")
        
        if X_test is not None and y_test is not None:
            eval_set = [(X_train, y_train), (X_test, y_test)]
            self.model.fit(
                X_train, y_train,
                eval_set=eval_set,
                verbose=False
            )
            
            # Calcular umbral óptimo
            y_scores = self.model.predict_proba(X_test)[:, 1]
            fpr, tpr, thresholds = roc_curve(y_test, y_scores)
            optimal_idx = int(np.argmax(tpr - fpr))
            self.optimal_threshold = thresholds[optimal_idx]
            
            y_pred = (y_scores > self.optimal_threshold).astype(int)
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            print(f"✅ Modelo entrenado")
            print(f"   Accuracy: {accuracy:.4f}")
            print(f"   F1-Score: {f1:.4f}")
            print(f"   Umbral óptimo: {self.optimal_threshold:.4f}")
        else:
            self.model.fit(X_train, y_train)
            self.optimal_threshold = 0.5
            print("✅ Modelo entrenado (sin validación)")
        
        self.is_trained = True
    
    def predict_trend(self, data: pd.DataFrame) -> Dict:
        """
        Predice si el precio subirá o bajará en los próximos 15 días.
        
        Args:
            data: DataFrame con datos OHLCV e indicadores
            
        Returns:
            Dict con predicción, probabilidad y confianza
        """
        if len(data) < 50:
            return {
                'prediction': 'HOLD',
                'probability': 0.5,
                'confidence': 'LOW',
                'reason': 'Datos insuficientes para predicción ML',
                'ml_score': 5.0
            }
        
        if not self.is_trained:
            return {
                'prediction': 'HOLD',
                'probability': 0.5,
                'confidence': 'LOW',
                'reason': 'Modelo no entrenado. Usar modo legacy.',
                'ml_score': 5.0
            }
        
        try:
            features = self._extract_features(data)
            proba = self.model.predict_proba(features)[0]
            
            # proba[0] = probabilidad de bajada
            # proba[1] = probabilidad de subida
            
            prob_up = float(proba[1])
            threshold = getattr(self, 'optimal_threshold', 0.5)
            
            # Determinar señal
            if prob_up > threshold + 0.1:  # Subida con confianza
                signal = 'BUY'
                confidence = 'HIGH' if prob_up > 0.7 else 'MEDIUM'
            elif prob_up < threshold - 0.1:  # Bajada con confianza
                signal = 'SELL'
                confidence = 'HIGH' if prob_up < 0.3 else 'MEDIUM'
            else:
                signal = 'HOLD'
                confidence = 'LOW'
            
            # Convertir probabilidad a score 0-10
            ml_score = prob_up * 10
            
            return {
                'prediction': signal,
                'probability': round(prob_up, 3),
                'confidence': confidence,
                'reason': f'ML predice {"subida" if signal == "BUY" else "bajada" if signal == "SELL" else "lateral"} con {prob_up*100:.1f}% probabilidad',
                'ml_score': round(ml_score, 1)
            }
        
        except Exception as e:
            print(f"❌ Error en predicción ML: {e}")
            return {
                'prediction': 'HOLD',
                'probability': 0.5,
                'confidence': 'LOW',
                'reason': f'Error en modelo: {str(e)}',
                'ml_score': 5.0
            }
    
    def get_feature_importance(self) -> Dict:
        """Retorna la importancia de cada feature"""
        if not self.is_trained or not hasattr(self.model, 'feature_importances_'):
            return {}
        
        importances = self.model.feature_importances_
        feature_importance = {
            name: float(imp) 
            for name, imp in zip(self.feature_names, importances)
        }
        
        # Ordenar por importancia
        return dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
