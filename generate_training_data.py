"""
Training Data Generator
Generates synthetic training data from medical knowledge base
"""

import pandas as pd
import random
import itertools
from medical_knowledge import CONDITIONS, SYMPTOM_CATEGORIES

class TrainingDataGenerator:
    """Generate synthetic training data for disease prediction"""
    
    def __init__(self):
        self.conditions = CONDITIONS
        self.symptom_categories = SYMPTOM_CATEGORIES
        
    def generate_synthetic_data(self, num_examples=3000):
        """
        Generate synthetic training examples
        
        Args:
            num_examples: Number of examples to generate
            
        Returns:
            pandas DataFrame with columns: symptoms, age, gender, disease
        """
        data = []
        
        # Get list of all conditions
        condition_names = list(self.conditions.keys())
        
        for _ in range(num_examples):
            # Randomly select a condition
            condition_name = random.choice(condition_names)
            condition_data = self.conditions[condition_name]
            
            # Get typical symptoms for this condition
            typical_symptoms = condition_data['symptoms']
            
            # Select 2-5 symptoms (with some randomness)
            num_symptoms = random.randint(2, min(5, len(typical_symptoms)))
            selected_symptoms = random.sample(typical_symptoms, num_symptoms)
            
            # Add some noise: occasionally add unrelated symptom (10% chance)
            if random.random() < 0.1:
                all_symptoms = []
                for symptoms in SYMPTOM_CATEGORIES.values():
                    all_symptoms.extend(symptoms)
                noise_symptom = random.choice(all_symptoms)
                if noise_symptom not in selected_symptoms:
                    selected_symptoms.append(noise_symptom)
            
            # Generate demographics
            age = self._generate_age(condition_name)
            gender = random.choice(['male', 'female'])
            
            # Create example
            data.append({
                'symptoms': ' '.join(selected_symptoms),
                'age': age,
                'gender': gender,
                'disease': condition_name
            })
        
        return pd.DataFrame(data)
    
    def _generate_age(self, condition_name):
        """Generate realistic age based on condition"""
        # Age distributions for different conditions
        if 'flu' in condition_name or 'cold' in condition_name:
            # More common in children and elderly
            if random.random() < 0.3:
                return random.randint(5, 17)
            elif random.random() < 0.3:
                return random.randint(65, 85)
            else:
                return random.randint(18, 64)
        
        elif 'migraine' in condition_name:
            # More common in adults
            return random.randint(25, 55)
        
        elif 'gastroenteritis' in condition_name:
            # Can affect all ages
            return random.randint(5, 75)
        
        else:
            # Default distribution
            return random.randint(18, 70)
    
    def augment_data(self, df, augmentation_factor=1.5):
        """
        Augment existing data with variations
        
        Args:
            df: Original DataFrame
            augmentation_factor: How much to increase data (1.5 = 50% more)
            
        Returns:
            Augmented DataFrame
        """
        augmented_rows = []
        num_to_augment = int(len(df) * (augmentation_factor - 1))
        
        for _ in range(num_to_augment):
            # Select random row
            row = df.sample(n=1).iloc[0]
            
            # Create variation
            symptoms = row['symptoms'].split()
            
            # Randomly remove one symptom (if more than 2)
            if len(symptoms) > 2 and random.random() < 0.5:
                symptoms.pop(random.randint(0, len(symptoms) - 1))
            
            # Create augmented row
            augmented_rows.append({
                'symptoms': ' '.join(symptoms),
                'age': row['age'] + random.randint(-5, 5),  # Slight age variation
                'gender': row['gender'],
                'disease': row['disease']
            })
        
        # Combine original and augmented data
        augmented_df = pd.concat([df, pd.DataFrame(augmented_rows)], ignore_index=True)
        
        return augmented_df
    
    def save_data(self, df, filepath='data/training_data.csv'):
        """Save training data to CSV"""
        df.to_csv(filepath, index=False)
        print(f"✓ Saved {len(df)} training examples to {filepath}")
    
    def load_kaggle_data(self, filepath='data/kaggle_disease_symptom.csv'):
        """
        Load Kaggle Disease Symptom Dataset (if available)
        
        Args:
            filepath: Path to Kaggle dataset
            
        Returns:
            DataFrame or None if file doesn't exist
        """
        try:
            df = pd.read_csv(filepath)
            print(f"✓ Loaded {len(df)} examples from Kaggle dataset")
            return df
        except FileNotFoundError:
            print(f"⚠️  Kaggle dataset not found at {filepath}")
            print("   You can download it from: https://www.kaggle.com/datasets/itachi9604/disease-symptom-description-dataset")
            return None
    
    def combine_datasets(self, synthetic_df, kaggle_df=None):
        """Combine synthetic and Kaggle datasets"""
        if kaggle_df is None:
            return synthetic_df
        
        # Ensure consistent column names
        # (Kaggle dataset may have different format - adjust as needed)
        combined = pd.concat([synthetic_df, kaggle_df], ignore_index=True)
        
        print(f"✓ Combined dataset: {len(combined)} total examples")
        return combined


def generate_training_data():
    """Main function to generate all training data"""
    print("=" * 60)
    print("Generating Training Data for ML Models")
    print("=" * 60)
    
    generator = TrainingDataGenerator()
    
    # Generate synthetic data
    print("\n1. Generating synthetic data...")
    synthetic_df = generator.generate_synthetic_data(num_examples=3000)
    print(f"   Generated {len(synthetic_df)} synthetic examples")
    
    # Augment data
    print("\n2. Augmenting data...")
    synthetic_df = generator.augment_data(synthetic_df, augmentation_factor=1.3)
    print(f"   Augmented to {len(synthetic_df)} examples")
    
    # Try to load Kaggle data
    print("\n3. Loading Kaggle dataset (if available)...")
    kaggle_df = generator.load_kaggle_data()
    
    # Combine datasets
    print("\n4. Combining datasets...")
    final_df = generator.combine_datasets(synthetic_df, kaggle_df)
    
    # Save final dataset
    print("\n5. Saving training data...")
    generator.save_data(final_df)
    
    # Print statistics
    print("\n" + "=" * 60)
    print("Training Data Statistics:")
    print("=" * 60)
    print(f"Total examples: {len(final_df)}")
    print(f"Unique diseases: {final_df['disease'].nunique()}")
    print(f"\nDisease distribution:")
    print(final_df['disease'].value_counts())
    print("\n" + "=" * 60)
    
    return final_df


if __name__ == '__main__':
    # Run data generation
    df = generate_training_data()
