"""
ML Model Manager
Handles loading, caching, and inference for machine learning models
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import List, Tuple, Optional, Dict

class MLModelManager:
    """
    Manages ML models for disease prediction and symptom extraction
    Implements lazy loading and fallback mechanisms
    """
    
    def __init__(self, models_dir='models'):
        self.models_dir = models_dir
        self.disease_model = None
        self.symptom_vectorizer = None
        self.feature_names = None
        self._models_loaded = False
        
    def _load_models(self):
        """Lazy load models on first use"""
        if self._models_loaded:
            return True
            
        try:
            disease_model_path = os.path.join(self.models_dir, 'disease_predictor.pkl')
            vectorizer_path = os.path.join(self.models_dir, 'symptom_vectorizer.pkl')
            
            if os.path.exists(disease_model_path):
                self.disease_model = joblib.load(disease_model_path)
                print("✓ Disease prediction model loaded")
            
            if os.path.exists(vectorizer_path):
                self.symptom_vectorizer = joblib.load(vectorizer_path)
                self.feature_names = self.symptom_vectorizer.get_feature_names_out()
                print("✓ Symptom vectorizer loaded")
            
            self._models_loaded = True
            return self.disease_model is not None
            
        except Exception as e:
            print(f"⚠️  Error loading ML models: {e}")
            print("   Falling back to rule-based system")
            return False
    
    def predict_disease(
        self, 
        symptoms: List[str], 
        age: Optional[int] = None, 
        gender: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """
        Predict diseases based on symptoms and demographics
        
        Args:
            symptoms: List of symptom strings
            age: Patient age (optional)
            gender: Patient gender (optional)
            
        Returns:
            List of (disease_name, confidence) tuples, sorted by confidence
        """
        # Try to load models if not already loaded
        if not self._load_models():
            return []  # Return empty, will fall back to rules
        
        try:
            # Create feature vector
            features = self._create_feature_vector(symptoms, age, gender)
            
            # Get predictions
            probabilities = self.disease_model.predict_proba(features)[0]
            classes = self.disease_model.classes_
            
            # Sort by confidence
            predictions = [(classes[i], float(probabilities[i])) 
                          for i in range(len(classes))]
            predictions.sort(key=lambda x: x[1], reverse=True)
            
            # Return top 3 predictions with confidence > 0.1
            return [(disease, conf) for disease, conf in predictions[:3] 
                   if conf > 0.1]
            
        except Exception as e:
            print(f"⚠️  Error in disease prediction: {e}")
            return []  # Fall back to rules
    
    def _create_feature_vector(
        self, 
        symptoms: List[str], 
        age: Optional[int], 
        gender: Optional[str]
    ) -> np.ndarray:
        """Create feature vector from symptoms and demographics"""
        
        # Create symptom text
        symptom_text = ' '.join(symptoms)
        
        # Vectorize symptoms
        if self.symptom_vectorizer:
            symptom_features = self.symptom_vectorizer.transform([symptom_text]).toarray()[0]
        else:
            # Simple binary encoding if vectorizer not available
            symptom_features = np.zeros(len(self.feature_names))
            for symptom in symptoms:
                if symptom in self.feature_names:
                    idx = list(self.feature_names).index(symptom)
                    symptom_features[idx] = 1
        
        # Add demographic features
        additional_features = []
        
        # Age group (categorical)
        if age is not None:
            if age < 18:
                age_group = [1, 0, 0, 0]  # child
            elif age < 40:
                age_group = [0, 1, 0, 0]  # young adult
            elif age < 65:
                age_group = [0, 0, 1, 0]  # adult
            else:
                age_group = [0, 0, 0, 1]  # senior
        else:
            age_group = [0, 0, 0, 0]
        
        additional_features.extend(age_group)
        
        # Gender (categorical)
        if gender == 'male':
            gender_features = [1, 0]
        elif gender == 'female':
            gender_features = [0, 1]
        else:
            gender_features = [0, 0]
        
        additional_features.extend(gender_features)
        
        # Symptom count
        additional_features.append(len(symptoms))
        
        # Combine all features
        features = np.concatenate([symptom_features, additional_features])
        
        return features.reshape(1, -1)
    
    def extract_symptoms(self, text: str) -> List[Tuple[str, float]]:
        """
        Extract symptoms from natural language text
        
        Args:
            text: User's message
            
        Returns:
            List of (symptom, confidence) tuples
            
        Note: This is a placeholder for future NLP model integration
        Currently returns empty list to use rule-based extraction
        """
        # TODO: Implement DistilBERT-based symptom extraction
        # For now, return empty to use rule-based extraction
        return []
    
    def is_available(self) -> bool:
        """Check if ML models are available"""
        return self._load_models()
    
    def get_model_info(self) -> Dict[str, any]:
        """Get information about loaded models"""
        self._load_models()
        
        return {
            'disease_model_loaded': self.disease_model is not None,
            'vectorizer_loaded': self.symptom_vectorizer is not None,
            'num_features': len(self.feature_names) if self.feature_names is not None else 0,
            'num_diseases': len(self.disease_model.classes_) if self.disease_model else 0
        }
