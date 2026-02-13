"""
Model Training Script
Trains XGBoost disease prediction model on generated data
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import os

class DiseaseModelTrainer:
    """Train and evaluate disease prediction model"""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.feature_names = None
        
    def load_data(self, filepath='data/training_data.csv'):
        """Load training data"""
        print(f"Loading data from {filepath}...")
        df = pd.read_csv(filepath)
        print(f"✓ Loaded {len(df)} examples")
        print(f"✓ {df['disease'].nunique()} unique diseases")
        return df
    
    def prepare_features(self, df):
        """
        Prepare features from raw data
        
        Returns:
            X: Feature matrix
            y: Target labels
        """
        print("\nPreparing features...")
        
        # Vectorize symptoms using TF-IDF
        print("  - Vectorizing symptoms...")
        self.vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2))
        symptom_features = self.vectorizer.fit_transform(df['symptoms']).toarray()
        self.feature_names = self.vectorizer.get_feature_names_out()
        
        # Encode age groups
        print("  - Encoding age groups...")
        age_groups = pd.cut(df['age'], bins=[0, 18, 40, 65, 120], 
                           labels=['child', 'young_adult', 'adult', 'senior'])
        age_encoded = pd.get_dummies(age_groups, prefix='age')
        
        # Encode gender
        print("  - Encoding gender...")
        gender_encoded = pd.get_dummies(df['gender'], prefix='gender')
        
        # Symptom count
        print("  - Calculating symptom count...")
        symptom_count = df['symptoms'].str.split().str.len().values.reshape(-1, 1)
        
        # Combine all features
        print("  - Combining features...")
        X = np.hstack([
            symptom_features,
            age_encoded.values,
            gender_encoded.values,
            symptom_count
        ])
        
        # Encode labels
        print("  - Encoding disease labels...")
        self.label_encoder = LabelEncoder()
        y = self.label_encoder.fit_transform(df['disease'])
        
        print(f"✓ Feature matrix shape: {X.shape}")
        print(f"✓ Number of classes: {len(self.label_encoder.classes_)}")
        
        return X, y
    
    def train_model(self, X_train, y_train, X_val, y_val, tune_hyperparameters=True):
        """
        Train XGBoost model
        
        Args:
            X_train, y_train: Training data
            X_val, y_val: Validation data
            tune_hyperparameters: Whether to perform grid search
        """
        print("\nTraining XGBoost model...")
        
        if tune_hyperparameters:
            print("  - Performing hyperparameter tuning...")
            
            # Define parameter grid
            param_grid = {
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.1, 0.3],
                'n_estimators': [100, 200],
                'min_child_weight': [1, 3],
                'subsample': [0.8, 1.0]
            }
            
            # Grid search
            xgb = XGBClassifier(random_state=42, eval_metric='mlogloss')
            grid_search = GridSearchCV(
                xgb, param_grid, cv=5, 
                scoring='accuracy', n_jobs=-1, verbose=1
            )
            grid_search.fit(X_train, y_train)
            
            self.model = grid_search.best_estimator_
            print(f"  ✓ Best parameters: {grid_search.best_params_}")
            print(f"  ✓ Best CV score: {grid_search.best_score_:.4f}")
            
        else:
            print("  - Training with default parameters...")
            self.model = XGBClassifier(
                max_depth=5,
                learning_rate=0.1,
                n_estimators=200,
                random_state=42,
                eval_metric='mlogloss'
            )
            self.model.fit(X_train, y_train)
        
        # Evaluate on validation set
        print("\n  - Evaluating on validation set...")
        y_val_pred = self.model.predict(X_val)
        val_accuracy = accuracy_score(y_val, y_val_pred)
        
        print(f"  ✓ Validation Accuracy: {val_accuracy:.4f} ({val_accuracy*100:.2f}%)")
        
        return val_accuracy
    
    def evaluate_model(self, X_test, y_test):
        """Evaluate model on test set"""
        print("\nEvaluating on test set...")
        
        y_pred = self.model.predict(X_test)
        test_accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n{'='*60}")
        print(f"TEST SET ACCURACY: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
        print(f"{'='*60}")
        
        # Detailed classification report
        print("\nClassification Report:")
        print(classification_report(
            y_test, y_pred,
            target_names=self.label_encoder.classes_,
            zero_division=0
        ))
        
        return test_accuracy
    
    def save_models(self, model_dir='models'):
        """Save trained models"""
        print(f"\nSaving models to {model_dir}/...")
        
        os.makedirs(model_dir, exist_ok=True)
        
        # Save XGBoost model
        model_path = os.path.join(model_dir, 'disease_predictor.pkl')
        joblib.dump(self.model, model_path)
        print(f"  ✓ Saved disease predictor to {model_path}")
        
        # Save vectorizer
        vectorizer_path = os.path.join(model_dir, 'symptom_vectorizer.pkl')
        joblib.dump(self.vectorizer, vectorizer_path)
        print(f"  ✓ Saved symptom vectorizer to {vectorizer_path}")
        
        # Save label encoder
        encoder_path = os.path.join(model_dir, 'label_encoder.pkl')
        joblib.dump(self.label_encoder, encoder_path)
        print(f"  ✓ Saved label encoder to {encoder_path}")
        
        print("\n✓ All models saved successfully!")


def train_disease_predictor(tune_hyperparameters=False):
    """Main training function"""
    print("=" * 60)
    print("Training Disease Prediction Model")
    print("=" * 60)
    
    trainer = DiseaseModelTrainer()
    
    # Load data
    df = trainer.load_data()
    
    # Prepare features
    X, y = trainer.prepare_features(df)
    
    # Split data: 70% train, 15% validation, 15% test
    print("\nSplitting data...")
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.176, random_state=42, stratify=y_temp  # 0.176 of 85% = 15% of total
    )
    
    print(f"  ✓ Training set: {len(X_train)} examples")
    print(f"  ✓ Validation set: {len(X_val)} examples")
    print(f"  ✓ Test set: {len(X_test)} examples")
    
    # Train model
    val_accuracy = trainer.train_model(X_train, y_train, X_val, y_val, tune_hyperparameters)
    
    # Evaluate on test set
    test_accuracy = trainer.evaluate_model(X_test, y_test)
    
    # Check if accuracy meets target
    if test_accuracy >= 0.88:
        print(f"\n🎉 SUCCESS! Achieved {test_accuracy*100:.2f}% accuracy (target: >88%)")
    else:
        print(f"\n⚠️  Accuracy {test_accuracy*100:.2f}% is below target (88%)")
        print("   Consider:")
        print("   - Generating more training data")
        print("   - Enabling hyperparameter tuning")
        print("   - Adding more features")
    
    # Save models
    trainer.save_models()
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    
    return trainer, test_accuracy


if __name__ == '__main__':
    # Train model (set tune_hyperparameters=True for better accuracy, but slower)
    trainer, accuracy = train_disease_predictor(tune_hyperparameters=False)
