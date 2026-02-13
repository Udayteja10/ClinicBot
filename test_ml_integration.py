"""
Comprehensive Test Suite for ML-Enhanced Chatbot
Tests disease prediction accuracy on diverse symptom combinations
"""

import pandas as pd
from symptom_analyzer import SymptomAnalyzer
from ml_models import MLModelManager

# Test cases covering diverse scenarios
TEST_CASES = [
    # Common conditions
    {
        'name': 'Flu - Classic Symptoms',
        'symptoms': ['fever', 'chills', 'body ache', 'fatigue', 'cough'],
        'age': 35,
        'gender': 'male',
        'expected': 'flu'
    },
    {
        'name': 'Common Cold',
        'symptoms': ['runny nose', 'stuffy nose', 'sore throat', 'cough'],
        'age': 28,
        'gender': 'female',
        'expected': 'common_cold'
    },
    {
        'name': 'Migraine',
        'symptoms': ['severe headache', 'nausea', 'dizziness'],
        'age': 42,
        'gender': 'female',
        'expected': 'migraine'
    },
    {
        'name': 'Gastroenteritis',
        'symptoms': ['nausea', 'vomiting', 'diarrhea', 'abdominal cramps'],
        'age': 30,
        'gender': 'male',
        'expected': 'gastroenteritis'
    },
    {
        'name': 'Allergic Reaction',
        'symptoms': ['rash', 'itching', 'hives', 'runny nose'],
        'age': 25,
        'gender': 'female',
        'expected': 'allergic_reaction'
    },
    {
        'name': 'Respiratory Infection',
        'symptoms': ['cough', 'fever', 'chest tightness', 'shortness of breath'],
        'age': 50,
        'gender': 'male',
        'expected': 'respiratory_infection'
    },
    {
        'name': 'Dehydration',
        'symptoms': ['dizziness', 'fatigue', 'headache'],
        'age': 22,
        'gender': 'male',
        'expected': 'dehydration'
    },
    
    # Edge cases - partial symptoms
    {
        'name': 'Flu - Minimal Symptoms',
        'symptoms': ['fever', 'body ache'],
        'age': 45,
        'gender': 'male',
        'expected': 'flu'
    },
    {
        'name': 'Cold - Single Symptom',
        'symptoms': ['runny nose'],
        'age': 18,
        'gender': 'female',
        'expected': 'common_cold'
    },
    
    # Age variations
    {
        'name': 'Flu - Child',
        'symptoms': ['fever', 'cough', 'body ache'],
        'age': 8,
        'gender': 'male',
        'expected': 'flu'
    },
    {
        'name': 'Flu - Elderly',
        'symptoms': ['fever', 'chills', 'fatigue'],
        'age': 72,
        'gender': 'female',
        'expected': 'flu'
    },
    
    # Ambiguous cases
    {
        'name': 'Headache - Could be Migraine or Dehydration',
        'symptoms': ['headache', 'fatigue'],
        'age': 30,
        'gender': 'female',
        'expected': ['migraine', 'dehydration']
    },
    {
        'name': 'Fever + Cough - Flu or Respiratory',
        'symptoms': ['fever', 'cough'],
        'age': 40,
        'gender': 'male',
        'expected': ['flu', 'respiratory_infection']
    },
]


def run_test_suite():
    """Run comprehensive test suite"""
    print("=" * 70)
    print("ML-Enhanced Chatbot - Comprehensive Test Suite")
    print("=" * 70)
    
    # Initialize analyzers
    print("\nInitializing analyzers...")
    ml_analyzer = SymptomAnalyzer(use_ml=True)
    rule_analyzer = SymptomAnalyzer(use_ml=False)
    
    results = {
        'ml_correct': 0,
        'rule_correct': 0,
        'ml_top3': 0,
        'rule_top3': 0,
        'total': 0,
        'details': []
    }
    
    print(f"\nRunning {len(TEST_CASES)} test cases...\n")
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"Test {i}/{len(TEST_CASES)}: {test['name']}")
        print(f"  Symptoms: {', '.join(test['symptoms'])}")
        print(f"  Demographics: {test['age']}yo {test['gender']}")
        
        # Set up analyzers
        ml_analyzer.reported_symptoms = test['symptoms']
        ml_analyzer.set_demographics(test['age'], test['gender'])
        
        rule_analyzer.reported_symptoms = test['symptoms']
        rule_analyzer.set_demographics(test['age'], test['gender'])
        
        # Get predictions
        ml_predictions = ml_analyzer.identify_possible_conditions()
        rule_predictions = rule_analyzer.identify_possible_conditions()
        
        # Check results
        expected = test['expected'] if isinstance(test['expected'], list) else [test['expected']]
        
        ml_top1 = ml_predictions[0]['name'] if ml_predictions else None
        rule_top1 = rule_predictions[0]['name'] if rule_predictions else None
        
        ml_top3_names = [p['name'] for p in ml_predictions[:3]]
        rule_top3_names = [p['name'] for p in rule_predictions[:3]]
        
        ml_correct = ml_top1 in expected
        rule_correct = rule_top1 in expected
        ml_in_top3 = any(exp in ml_top3_names for exp in expected)
        rule_in_top3 = any(exp in rule_top3_names for exp in expected)
        
        # Update results
        results['total'] += 1
        if ml_correct:
            results['ml_correct'] += 1
        if rule_correct:
            results['rule_correct'] += 1
        if ml_in_top3:
            results['ml_top3'] += 1
        if rule_in_top3:
            results['rule_top3'] += 1
        
        # Print results
        print(f"  Expected: {', '.join(expected)}")
        
        if ml_predictions:
            print(f"  ML Predicted: {ml_top1} ({ml_predictions[0]['match_percentage']:.1f}%) {'✓' if ml_correct else '✗'}")
        else:
            print(f"  ML Predicted: None (no predictions)")
            
        if rule_predictions:
            print(f"  Rule Predicted: {rule_top1} ({rule_predictions[0]['match_percentage']:.1f}%) {'✓' if rule_correct else '✗'}")
        else:
            print(f"  Rule Predicted: None (no predictions)")
        
        if not ml_correct and ml_in_top3 and ml_predictions:
            print(f"  ML Top 3: {', '.join(ml_top3_names)} (Expected in top 3 ✓)")
        
        results['details'].append({
            'test': test['name'],
            'ml_correct': ml_correct,
            'rule_correct': rule_correct,
            'ml_prediction': ml_top1,
            'rule_prediction': rule_top1
        })
        
        print()
    
    # Print summary
    print("=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    
    ml_accuracy = (results['ml_correct'] / results['total']) * 100
    rule_accuracy = (results['rule_correct'] / results['total']) * 100
    ml_top3_accuracy = (results['ml_top3'] / results['total']) * 100
    rule_top3_accuracy = (results['rule_top3'] / results['total']) * 100
    
    print(f"\nTop-1 Accuracy:")
    print(f"  ML-Enhanced:  {results['ml_correct']}/{results['total']} = {ml_accuracy:.1f}%")
    print(f"  Rule-Based:   {results['rule_correct']}/{results['total']} = {rule_accuracy:.1f}%")
    print(f"  Improvement:  {ml_accuracy - rule_accuracy:+.1f}%")
    
    print(f"\nTop-3 Accuracy:")
    print(f"  ML-Enhanced:  {results['ml_top3']}/{results['total']} = {ml_top3_accuracy:.1f}%")
    print(f"  Rule-Based:   {results['rule_top3']}/{results['total']} = {rule_top3_accuracy:.1f}%")
    
    # Performance comparison
    improvement = ml_accuracy - rule_accuracy
    if improvement > 0:
        print(f"\n✅ ML system outperforms rules by {improvement:.1f}%")
    elif improvement < 0:
        print(f"\n⚠️  Rules outperform ML by {-improvement:.1f}%")
    else:
        print(f"\n➖ ML and rules perform equally")
    
    # Check if meets target
    if ml_accuracy >= 88:
        print(f"\n🎉 SUCCESS! ML accuracy {ml_accuracy:.1f}% exceeds 88% target!")
    else:
        print(f"\n⚠️  ML accuracy {ml_accuracy:.1f}% below 88% target")
    
    print("\n" + "=" * 70)
    
    return results


def test_performance():
    """Test model loading and prediction performance"""
    import time
    
    print("\n" + "=" * 70)
    print("PERFORMANCE TESTING")
    print("=" * 70)
    
    # Test model loading time
    print("\n1. Model Loading Time:")
    start = time.time()
    analyzer = SymptomAnalyzer(use_ml=True)
    load_time = time.time() - start
    print(f"   Time: {load_time:.2f}s {'✓' if load_time < 5 else '✗'} (target: <5s)")
    
    # Test prediction time (first call)
    print("\n2. First Prediction Time:")
    analyzer.reported_symptoms = ['fever', 'cough', 'body ache']
    analyzer.set_demographics(30, 'male')
    
    start = time.time()
    predictions = analyzer.identify_possible_conditions()
    first_pred_time = time.time() - start
    print(f"   Time: {first_pred_time:.3f}s {'✓' if first_pred_time < 2 else '✗'} (target: <2s)")
    
    # Test subsequent predictions
    print("\n3. Subsequent Prediction Time:")
    analyzer.reported_symptoms = ['headache', 'nausea']
    
    start = time.time()
    predictions = analyzer.identify_possible_conditions()
    subsequent_time = time.time() - start
    print(f"   Time: {subsequent_time:.3f}s {'✓' if subsequent_time < 1 else '✗'} (target: <1s)")
    
    # Memory usage
    print("\n4. Model Info:")
    if analyzer.ml_manager:
        info = analyzer.ml_manager.get_model_info()
        print(f"   Disease model loaded: {info['disease_model_loaded']}")
        print(f"   Vectorizer loaded: {info['vectorizer_loaded']}")
        print(f"   Number of features: {info['num_features']}")
        print(f"   Number of diseases: {info['num_diseases']}")
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    # Run test suite
    results = run_test_suite()
    
    # Run performance tests
    test_performance()
    
    print("\n✓ All tests complete!")
