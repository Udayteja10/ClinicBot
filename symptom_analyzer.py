"""
Symptom Analyzer - Medical Reasoning and Risk Assessment
Analyzes symptoms, identifies conditions, and calculates risk levels
"""

import re
from typing import Dict, List

import numpy as np
from scipy.spatial.distance import cdist
from sklearn.feature_extraction.text import TfidfVectorizer
from medical_knowledge import (
    SYMPTOM_CATEGORIES, CONDITIONS, FOLLOWUP_QUESTIONS,
    RISK_FACTORS, ADVICE_TEMPLATES, get_symptom_category,
    MEDICATION_RECOMMENDATIONS, COMMON_MED_NAMES, MEDICATION_INTERACTIONS,
    COMMON_MED_MISSPELLINGS
)

# Import ML model manager
try:
    from ml_models import MLModelManager
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  ML models not available, using rule-based system only")

SYMPTOM_ALIASES = {
    'tummy ache': 'abdominal pain',
    'stomach ache': 'abdominal pain',
    'belly pain': 'abdominal pain',
    'stomach pain': 'abdominal pain',
    'throwing up': 'vomiting',
    'puking': 'vomiting',
    'vomitting': 'vomiting',
    'loose stools': 'diarrhea',
    'diarrhoea': 'diarrhea',
    'queasy': 'nausea',
    'nauseous': 'nausea',
    'blocked nose': 'stuffy nose',
    'stuffed nose': 'stuffy nose',
    'runny nose': 'runny nose',
    'sneezing': 'runny nose',
    'short of breath': 'shortness of breath',
    'cant breathe': 'difficulty breathing',
    'can not breathe': 'difficulty breathing',
    'trouble breathing': 'difficulty breathing',
    'breathing trouble': 'difficulty breathing',
    'light headed': 'lightheaded',
    'lightheadedness': 'lightheaded',
    'head pain': 'headache',
    'migraine': 'headache',
    'body aches': 'body ache',
    'body ache': 'body ache',
    'body pain': 'body ache',
    'body pains': 'body ache',
    'aching': 'body ache',
    'tired': 'fatigue',
    'exhausted': 'fatigue',
    'dizzy': 'dizziness',
    'breathless': 'shortness of breath',
    'coughing': 'cough',
    'thyroid problem': 'thyroid',
    'thyroid issue': 'thyroid',
    'thyroid disease': 'thyroid',
    'feverish': 'fever',
    'chilly': 'chills',
    'sorethroat': 'sore throat'
}

SYMPTOM_PATTERNS = [
    (r'\b(body|whole body|full body|all over)\s*(pain|ache|aches|hurt|hurts|sore|soreness)\b', 'body ache'),
    (r'\b(head|headache|head pain|head hurts|head hurting)\b', 'headache'),
    (r'\b(chest)\s*(pain|hurts|tightness|pressure)\b', 'chest pain'),
    (r'\b(stomach|belly|abdomen|abdominal)\s*(pain|ache|aches|hurt|hurts|cramp|cramps|sore)\b', 'abdominal pain'),
    (r'\b(throat)\s*(pain|sore|hurts|scratchy)\b', 'sore throat'),
    (r'\b(ear)\s*(pain|ache|hurts)\b', 'earache'),
    (r'\b(back)\s*(pain|ache|hurts|sore)\b', 'back pain'),
    (r'\b(neck)\s*(pain|ache|stiff|stiffness)\b', 'neck pain'),
    (r'\b(joint|knee|ankle|wrist|elbow|shoulder)\s*(pain|ache|aches|sore)\b', 'joint pain'),
    (r'\b(muscle|arm|leg)\s*(pain|ache|aches|sore)\b', 'muscle pain'),
    (r'\b(feel|feeling)\s*(hot|feverish|warm)\b', 'fever'),
    (r'\b(runny|blocked|stuffy)\s*nose\b', 'runny nose'),
    (r'\b(trouble|difficulty)\s*breathing\b', 'difficulty breathing')
]

CONTEXT_QUESTIONS = [
    ("Have you been sleeping well recently?", "sleep_deprivation"),
    ("Have you been drinking enough water today?", "dehydration"),
    ("Have you been under unusual stress lately?", "stress"),
    ("Have you been in close contact with anyone who is sick?", "sick_contact"),
    ("Any recent travel or major routine changes?", "recent_travel")
]

DISPLAY_SYMPTOM_MAP = {
    'abdominal pain': 'stomach pain'
}

LOW_INFORMATION_MESSAGES = {
    'yes', 'no', 'not sure', 'maybe', 'ok', 'okay', 'fine', 'idk', 'dont know', 'don\'t know',
    'na', 'n/a', 'none', 'nil'
}

class SymptomAnalyzer:
    """Analyzes symptoms and provides medical reasoning"""
    
    def __init__(self, use_ml=True):
        self.reported_symptoms = []
        self.symptom_categories = set()
        self.duration_days = None
        self.patient_age = None
        self.patient_gender = None
        self.followup_asked = set()
        self.lifestyle_context = {}  # Track lifestyle factors
        self._symptom_phrases = []
        self._symptom_phrase_to_canonical = {}
        self._symptom_vectorizer = None
        self._symptom_matrix = None
        self.symptom_severity = None
        self.temperature_c = None
        self.cough_type = None
        self.current_meds = []
        self.last_assessment = None
        
        # ML model integration
        self.use_ml = use_ml and ML_AVAILABLE
        self.ml_manager = MLModelManager() if self.use_ml else None

        self._build_symptom_index()
        self._build_med_index()
        
        if self.use_ml:
            print("✓ ML-enhanced symptom analyzer initialized")
        else:
            print("ℹ️  Using rule-based symptom analyzer")

    def _normalize_text(self, text: str) -> str:
        """Normalize text for consistent matching"""
        lowered = text.lower()
        cleaned = re.sub(r'[^a-z0-9\s]+', ' ', lowered)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def _build_symptom_index(self):
        """Build vector index for fuzzy symptom detection using SciPy"""
        phrases: Dict[str, str] = {}

        for category, symptoms in SYMPTOM_CATEGORIES.items():
            for symptom in symptoms:
                normalized = self._normalize_text(symptom)
                phrases[normalized] = symptom

        for alias, canonical in SYMPTOM_ALIASES.items():
            normalized = self._normalize_text(alias)
            phrases[normalized] = canonical

        self._symptom_phrases = list(phrases.keys())
        self._symptom_phrase_to_canonical = phrases

        if not self._symptom_phrases:
            return

    def _build_med_index(self):
        """Build a medication alias map for interaction checks."""
        alias_map = {}
        for condition in MEDICATION_RECOMMENDATIONS.values():
            for med in condition.get('medications', []):
                name = med.get('name', '')
                if not name:
                    continue
                base = name.split('(')[0].strip()
                if base:
                    alias_map[self._normalize_text(base)] = base.lower()

                paren_match = re.search(r'\(([^)]+)\)', name)
                aliases = []
                if paren_match:
                    aliases.extend(re.split(r'[\/,]', paren_match.group(1)))
                aliases.extend(name.split('/'))

                for alias in aliases:
                    alias_clean = re.sub(r'[^a-zA-Z\s]+', ' ', alias).strip()
                    alias_clean = ' '.join(alias_clean.split())
                    if len(alias_clean) >= 3:
                        alias_map[self._normalize_text(alias_clean)] = (base or alias_clean).lower()

        for med in COMMON_MED_NAMES:
            alias_map[self._normalize_text(med)] = med.lower()

        for misspelling, canonical in COMMON_MED_MISSPELLINGS.items():
            alias_map[self._normalize_text(misspelling)] = canonical.lower()

        self._med_alias_map = alias_map

    def extract_current_meds(self, message):
        """Extract medications mentioned in free text."""
        if not hasattr(self, '_med_alias_map'):
            self._build_med_index()
        normalized = self._normalize_text(message)
        found = []
        for alias, canonical in self._med_alias_map.items():
            if alias and re.search(rf'\b{re.escape(alias)}\b', normalized):
                if canonical not in self.current_meds:
                    self.current_meds.append(canonical)
                if canonical not in found:
                    found.append(canonical)
        return found

    def check_med_interactions(self):
        """Check basic medication interactions for current meds."""
        meds = set(self.current_meds)
        warnings = []
        for rule in MEDICATION_INTERACTIONS:
            group_a = set(rule.get('group_a', []))
            group_b = set(rule.get('group_b', []))
            if not group_a or not group_b:
                continue
            if group_a == group_b:
                matched = meds.intersection(group_a)
                if len(matched) >= 2:
                    warnings.append({
                        'severity': rule.get('severity', 'medium'),
                        'message': rule.get('message', ''),
                        'meds': sorted(matched)
                    })
            else:
                matched_a = meds.intersection(group_a)
                matched_b = meds.intersection(group_b)
                if matched_a and matched_b:
                    warnings.append({
                        'severity': rule.get('severity', 'medium'),
                        'message': rule.get('message', ''),
                        'meds': sorted(matched_a.union(matched_b))
                    })
        return warnings

    def _pattern_symptom_match(self, message_normalized: str) -> List[str]:
        """Pattern-based matching for common symptom phrasing."""
        found = []
        for pattern, canonical in SYMPTOM_PATTERNS:
            if re.search(pattern, message_normalized):
                self._add_symptom(canonical, found)
        return found

        self._symptom_vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5))
        self._symptom_matrix = self._symptom_vectorizer.fit_transform(self._symptom_phrases)

    def _add_symptom(self, symptom: str, found_symptoms: List[str]):
        """Add symptom to tracking lists and categories if new"""
        if symptom not in self.reported_symptoms:
            found_symptoms.append(symptom)
            self.reported_symptoms.append(symptom)
            category = get_symptom_category(symptom)
            if category:
                self.symptom_categories.add(category)

    def _fuzzy_symptom_match(self, message: str, max_matches: int = 3, threshold: float = 0.6) -> List[str]:
        """Use SciPy cosine similarity over TF-IDF character n-grams to match symptoms."""
        if not self._symptom_vectorizer or self._symptom_matrix is None:
            return []

        message_vec = self._symptom_vectorizer.transform([message])
        if message_vec.nnz == 0:
            return []

        distances = cdist(message_vec.toarray(), self._symptom_matrix.toarray(), metric='cosine')[0]
        similarities = 1 - distances

        candidates = np.where(similarities >= threshold)[0]
        if candidates.size == 0:
            return []

        sorted_candidates = sorted(candidates, key=lambda i: similarities[i], reverse=True)
        matches = []
        for idx in sorted_candidates[:max_matches]:
            phrase = self._symptom_phrases[idx]
            canonical = self._symptom_phrase_to_canonical.get(phrase)
            if canonical and canonical not in matches:
                matches.append(canonical)
        return matches
    
    def extract_context(self, message):
        """Extract lifestyle and contextual factors from message"""
        message_lower = message.lower()
        
        # Sleep-related context
        if any(phrase in message_lower for phrase in ['stayed up late', 'lack of sleep', 'no sleep', 'didn\'t sleep', 'couldn\'t sleep', 'late night', 'all night', 'sleepless']):
            self.lifestyle_context['sleep_deprivation'] = True
        
        # Stress-related context
        if any(phrase in message_lower for phrase in ['stressed', 'stress', 'anxious', 'anxiety', 'worried', 'tension', 'pressure']):
            self.lifestyle_context['stress'] = True
        
        # Screen time context
        if any(phrase in message_lower for phrase in ['screen', 'computer', 'phone', 'laptop', 'staring at']):
            self.lifestyle_context['screen_time'] = True
        
        # Dehydration context
        if any(phrase in message_lower for phrase in ['didn\'t drink', 'no water', 'dehydrated', 'thirsty']):
            self.lifestyle_context['dehydration'] = True
        
        # Meal skipping
        if any(phrase in message_lower for phrase in ['skipped meal', 'didn\'t eat', 'no food', 'hungry', 'empty stomach']):
            self.lifestyle_context['skipped_meals'] = True

        # Sick contact exposure
        if any(phrase in message_lower for phrase in ['contact with sick', 'around sick', 'someone sick', 'family sick', 'coworker sick']):
            self.lifestyle_context['sick_contact'] = True

        # Travel or routine change
        if any(phrase in message_lower for phrase in ['recent travel', 'just travelled', 'just traveled', 'flight', 'trip']):
            self.lifestyle_context['recent_travel'] = True

        # Smoking/vaping
        if any(phrase in message_lower for phrase in ['smoke', 'smoking', 'vape', 'vaping', 'cigarette']):
            self.lifestyle_context['smoking'] = True

        # Alcohol
        if any(phrase in message_lower for phrase in ['alcohol', 'drinking', 'beer', 'whiskey', 'wine']):
            self.lifestyle_context['alcohol'] = True
        
        return self.lifestyle_context

    def extract_severity(self, message):
        """Extract severity cues and temperature if mentioned"""
        message_lower = message.lower()

        if any(word in message_lower for word in ['severe', 'very bad', 'very high', 'extreme', 'intense']):
            self.symptom_severity = 'severe'
        elif any(word in message_lower for word in ['moderate', 'medium']):
            self.symptom_severity = 'moderate'
        elif any(word in message_lower for word in ['mild', 'light', 'slight']):
            self.symptom_severity = 'mild'

        temp_f_match = re.search(r'(\d{2,3}(?:\.\d+)?)\s*(?:f|°f|fahrenheit)', message_lower)
        temp_c_match = re.search(r'(\d{2,3}(?:\.\d+)?)\s*(?:c|°c|celsius)', message_lower)

        if temp_f_match:
            temp_f = float(temp_f_match.group(1))
            self.temperature_c = (temp_f - 32) * 5 / 9
        elif temp_c_match:
            self.temperature_c = float(temp_c_match.group(1))

        return self.symptom_severity

    def extract_cough_type(self, message):
        """Extract cough type from follow-up responses."""
        message_lower = message.lower()
        if any(word in message_lower for word in ['phlegm', 'mucus', 'wet cough', 'productive']):
            self.cough_type = 'productive'
        elif any(word in message_lower for word in ['dry cough', 'dry', 'non productive']):
            self.cough_type = 'dry'
        return self.cough_type
    
    def extract_symptoms(self, message):
        """Extract symptoms from natural language message"""
        message_normalized = self._normalize_text(message)
        found_symptoms = []
        
        # Exact + alias matches first
        for phrase, canonical in self._symptom_phrase_to_canonical.items():
            if phrase and phrase in message_normalized:
                self._add_symptom(canonical, found_symptoms)

        # Pattern matches (e.g., "body pain", "throat hurts")
        pattern_matches = self._pattern_symptom_match(message_normalized)
        for symptom in pattern_matches:
            if symptom not in found_symptoms:
                found_symptoms.append(symptom)

        # Fuzzy matches (SciPy cosine similarity on char n-grams)
        if (
            not found_symptoms
            and message_normalized
            and len(message_normalized) >= 8
            and message_normalized not in LOW_INFORMATION_MESSAGES
        ):
            fuzzy_matches = self._fuzzy_symptom_match(message_normalized, threshold=0.6)
            for symptom in fuzzy_matches:
                self._add_symptom(symptom, found_symptoms)

        # Remove overly generic symptoms if more specific ones exist
        self._clean_symptom_list(found_symptoms)
        
        return found_symptoms

    def _clean_symptom_list(self, found_symptoms):
        generic = {'ache', 'pain', 'sore'}
        specific_present = any(
            symptom in self.reported_symptoms for symptom in ['body ache', 'headache', 'chest pain', 'abdominal pain']
        )
        if specific_present:
            for g in list(generic):
                if g in self.reported_symptoms:
                    self.reported_symptoms.remove(g)
                if g in found_symptoms:
                    found_symptoms.remove(g)

    def _display_symptom(self, symptom):
        return DISPLAY_SYMPTOM_MAP.get(symptom, symptom)

    def get_display_symptoms(self):
        return [self._display_symptom(symptom) for symptom in self.reported_symptoms]
    
    def extract_duration(self, message):
        """Extract symptom duration from message"""
        message_lower = message.lower()
        
        # Look for duration patterns
        patterns = [
            r'(\d+)\s*days?',
            r'(\d+)\s*weeks?',
            r'since\s+(\d+)\s*days?',
            r'for\s+(\d+)\s*days?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                days = int(match.group(1))
                if 'week' in pattern:
                    days *= 7
                self.duration_days = days
                return days

        # Fuzzy time phrases
        if any(phrase in message_lower for phrase in ['today', 'this morning', 'since morning', 'from morning', 'since today', 'this afternoon', 'this evening']):
            self.duration_days = 1
            return 1
        if any(phrase in message_lower for phrase in ['yesterday', 'last night', 'since yesterday']):
            self.duration_days = 1
            return 1

        hours_match = re.search(r'(\d+)\s*hours?', message_lower)
        if hours_match:
            self.duration_days = 1
            return 1
        
        return None
    
    def set_demographics(self, age, gender):
        """Set patient demographics"""
        self.patient_age = age
        self.patient_gender = gender
    
    def calculate_risk_level(self):
        """Calculate overall risk level based on symptoms, age, and duration"""
        risk_score = 0
        
        # Age-based risk
        if self.patient_age:
            if self.patient_age <= 5 or self.patient_age >= 65:
                risk_score += 2
            elif self.patient_age <= 17 or self.patient_age >= 60:
                risk_score += 1
        
        # Symptom combination risk
        symptom_set = set(self.reported_symptoms)
        symptom_text = ' '.join(self.reported_symptoms).lower()
        for combo in RISK_FACTORS['symptom_combinations']['high_risk']:
            if all(s in symptom_text for s in combo):
                risk_score += 3
                break
        
        for combo in RISK_FACTORS['symptom_combinations']['medium_risk']:
            if all(s in symptom_text for s in combo):
                risk_score += 2
                break
        
        # Duration-based risk
        if self.duration_days:
            if self.duration_days >= RISK_FACTORS['duration']['concerning']:
                risk_score += 2
            elif self.duration_days >= RISK_FACTORS['duration']['urgent']:
                risk_score += 1

        # Temperature-based risk
        if self.temperature_c is not None:
            if self.temperature_c >= 39.5:
                risk_score += 2
            elif self.temperature_c >= 38.5:
                risk_score += 1

        # Severity keywords
        if self.symptom_severity == 'severe':
            risk_score += 1
        
        # Number of symptoms
        if len(self.reported_symptoms) >= 5:
            risk_score += 1
        
        # Determine risk level
        if risk_score >= 5:
            return 'high_risk'
        elif risk_score >= 3:
            return 'medium_risk'
        else:
            return 'low_risk'
    
    def identify_possible_conditions(self):
        """Identify possible conditions using hybrid ML + rule-based approach"""
        
        # Get rule-based predictions
        rule_predictions = self._rule_based_matching()
        
        # If ML is available, combine with ML predictions
        if self.use_ml and self.ml_manager and self.ml_manager.is_available():
            ml_predictions = self._get_ml_predictions()
            
            if ml_predictions:
                # Hybrid approach: 60% ML + 40% rules
                combined = self._combine_predictions(ml_predictions, rule_predictions)
                return combined
        
        # Fall back to rule-based only
        return rule_predictions
    
    def _rule_based_matching(self):
        """Original rule-based condition matching"""
        possible_conditions = []
        
        for condition_name, condition_data in CONDITIONS.items():
            match_count = 0
            condition_symptoms = condition_data['symptoms']
            
            for symptom in self.reported_symptoms:
                for cond_symptom in condition_symptoms:
                    if cond_symptom in symptom or symptom in cond_symptom:
                        match_count += 1
                        break
            
            # If at least 40% of condition symptoms match
            if match_count >= len(condition_symptoms) * 0.4:
                possible_conditions.append({
                    'name': condition_name,
                    'description': condition_data['description'],
                    'match_percentage': (match_count / len(condition_symptoms)) * 100,
                    'risk_level': condition_data['risk_level']
                })
        
        # Sort by match percentage
        possible_conditions.sort(key=lambda x: x['match_percentage'], reverse=True)
        return possible_conditions[:3]  # Return top 3 matches
    
    def _get_ml_predictions(self):
        """Get ML model predictions"""
        try:
            predictions = self.ml_manager.predict_disease(
                self.reported_symptoms,
                self.patient_age,
                self.patient_gender
            )
            
            # Convert to same format as rule-based
            ml_conditions = []
            for disease_name, confidence in predictions:
                if disease_name in CONDITIONS:
                    ml_conditions.append({
                        'name': disease_name,
                        'description': CONDITIONS[disease_name]['description'],
                        'match_percentage': confidence * 100,  # Convert to percentage
                        'risk_level': CONDITIONS[disease_name]['risk_level'],
                        'source': 'ml'
                    })
            
            return ml_conditions
            
        except Exception as e:
            print(f"⚠️  ML prediction error: {e}")
            return []
    
    def _combine_predictions(self, ml_predictions, rule_predictions):
        """Combine ML and rule-based predictions with weighted scoring"""
        combined_scores = {}
        
        # Add ML predictions (60% weight)
        for pred in ml_predictions:
            name = pred['name']
            combined_scores[name] = {
                'name': name,
                'description': pred['description'],
                'risk_level': pred['risk_level'],
                'ml_score': pred['match_percentage'] * 0.6,
                'rule_score': 0
            }
        
        # Add rule-based predictions (40% weight)
        for pred in rule_predictions:
            name = pred['name']
            if name in combined_scores:
                combined_scores[name]['rule_score'] = pred['match_percentage'] * 0.4
            else:
                combined_scores[name] = {
                    'name': name,
                    'description': pred['description'],
                    'risk_level': pred['risk_level'],
                    'ml_score': 0,
                    'rule_score': pred['match_percentage'] * 0.4
                }
        
        # Calculate final scores
        final_predictions = []
        for name, scores in combined_scores.items():
            final_score = scores['ml_score'] + scores['rule_score']
            final_predictions.append({
                'name': name,
                'description': scores['description'],
                'match_percentage': final_score,
                'risk_level': scores['risk_level']
            })
        
        # Sort by final score
        final_predictions.sort(key=lambda x: x['match_percentage'], reverse=True)
        return final_predictions[:3]
    
    def get_followup_questions(self, max_questions=2):
        """Generate relevant follow-up questions based on symptoms"""
        questions = []
        
        # Get questions for each symptom category
        for category in self.symptom_categories:
            if category not in self.followup_asked and category in FOLLOWUP_QUESTIONS:
                category_questions = FOLLOWUP_QUESTIONS[category]
                questions.extend(category_questions[:1])  # Take 1 question per category
                self.followup_asked.add(category)
        
        # Add general questions if we don't have enough
        if len(questions) < max_questions and 'general' not in self.followup_asked:
            general_questions = FOLLOWUP_QUESTIONS['general']
            questions.extend(general_questions[:max_questions - len(questions)])
            self.followup_asked.add('general')

        # Add context-aware questions if still short
        if len(questions) < max_questions:
            for question, flag in CONTEXT_QUESTIONS:
                key = f"context_{flag}"
                if key in self.followup_asked:
                    continue
                if self.lifestyle_context.get(flag):
                    continue
                questions.append(question)
                self.followup_asked.add(key)
                if len(questions) >= max_questions:
                    break
        
        return questions[:max_questions]
    
    def generate_assessment(self):
        """Generate comprehensive medical assessment"""
        risk_level = self.calculate_risk_level()
        possible_conditions = self.identify_possible_conditions()
        advice = ADVICE_TEMPLATES.get(risk_level, ADVICE_TEMPLATES['medium_risk'])
        
        assessment = {
            'symptoms': self.reported_symptoms,
            'risk_level': risk_level,
            'possible_conditions': possible_conditions,
            'advice': advice,
            'duration': self.duration_days,
            'age': self.patient_age,
            'cough_type': self.cough_type,
            'current_meds': self.current_meds
        }
        
        self.last_assessment = assessment
        return assessment
    
    def format_assessment_response(self):
        """Format assessment into a doctor-like response"""
        assessment = self.generate_assessment()
        
        response = "Based on our consultation, here's my assessment:\n\n"
        
        # Summarize symptoms
        display_symptoms = self.get_display_symptoms()
        response += f"📋 **Symptoms Reported**: {', '.join(display_symptoms[:5])}"
        if len(display_symptoms) > 5:
            response += f" and {len(display_symptoms) - 5} more"
        response += "\n\n"

        if self.cough_type:
            response += f"🫁 **Cough Type**: {self.cough_type.title()}\n\n"
        
        # Possible conditions
        if assessment['possible_conditions']:
            response += "🔍 **Possible Conditions**:\n"
            for i, condition in enumerate(assessment['possible_conditions'], 1):
                response += f"{i}. {condition['description'].title()}\n"
            response += "\n"
        
        # Risk level and advice
        risk_level = assessment['risk_level']
        response += f"⚕️ **Assessment**: "
        
        if risk_level == 'high_risk':
            response += "Your symptoms suggest you need prompt medical attention.\n\n"
        elif risk_level == 'medium_risk':
            response += "Your symptoms should be evaluated by a healthcare provider.\n\n"
        else:
            response += "Your symptoms appear to be mild, but monitoring is important.\n\n"
        
        # Medication recommendations (minimal and safe)
        response += "💊 **Medication Recommendations**:\n\n"
        medications = self._get_medication_recommendations(assessment['possible_conditions'])
        
        if self.patient_age is not None and self.patient_age < 12:
            response += ("Pediatric dosing requires a clinician. "
                         "Please consult a healthcare provider for medication guidance.\n\n")
        elif risk_level == 'low_risk' and medications:
            for i, med in enumerate(medications[:2], 1):
                response += f"**{i}. {med['name']}**\n"
                response += f"   • **When to Take**: {med['timing']}\n"
                response += f"   • **Duration**: {med['duration']}\n"
                response += f"   • **Instructions**: {med['instructions']}\n\n"
            response += "Note: Use only one antipyretic at a time unless advised by a clinician.\n\n"
        else:
            response += ("Given the risk level, I don't recommend self-medicating beyond basic relief. "
                         "Please consult a healthcare provider for specific medication guidance.\n\n")
        
        # General advice
        response += "💡 **Additional Recommendations**:\n"
        for advice_item in assessment['advice']['general']:
            response += f"• {advice_item}\n"
        
        # Context-aware guidance
        context_guidance = self._get_context_guidance()
        if context_guidance:
            response += "\n🧭 **Context-Aware Guidance**:\n"
            for tip in context_guidance:
                response += f"• {tip}\n"

        response += f"\n⏰ **Next Steps**: {assessment['advice']['when_to_seek_care']}\n"

        # Contextual insights (unique feature)
        context_insights = self._get_context_insights()
        if context_insights:
            response += "\n🧭 **Possible Contributing Factors Detected**:\n"
            for insight in context_insights:
                response += f"• {insight}\n"

        # Medication interaction check
        if self.current_meds:
            interactions = self.check_med_interactions()
            display_meds = [m.title() for m in self.current_meds]
            response += "\n💊 **Medication Interaction Check**:\n"
            response += f"• Current meds noted: {', '.join(display_meds)}\n"
            if interactions:
                for item in interactions:
                    response += f"• {item['message']} (Meds: {', '.join([m.title() for m in item['meds']])})\n"
            else:
                response += "• No major interactions found in this basic check.\n"

        # Important disclaimer
        response += "\n⚠️ **Important**: These are general recommendations. Always consult a healthcare provider before starting any medication, especially if you have allergies, other medical conditions, or are taking other medications.\n"
        
        return response

    def format_relief_plan_response(self):
        """Create a personalized 24-hour relief plan (unique feature)."""
        risk_level = self.calculate_risk_level()
        plan = []

        plan.append("Hydrate steadily throughout the day (small sips if nauseated).")
        plan.append("Rest and avoid strenuous activity while symptoms are active.")

        if 'fever' in ' '.join(self.reported_symptoms):
            plan.append("Check temperature every 4-6 hours and note trends.")

        if any(symptom in ' '.join(self.reported_symptoms) for symptom in ['headache', 'body ache', 'muscle pain']):
            plan.append("Use a quiet, dim environment and take short screen breaks.")

        if any(symptom in ' '.join(self.reported_symptoms) for symptom in ['cough', 'sore throat', 'congestion']):
            plan.append("Try warm fluids or steam inhalation to ease congestion.")

        if any(symptom in ' '.join(self.reported_symptoms) for symptom in ['nausea', 'vomiting', 'diarrhea']):
            plan.append("Stick to bland foods and avoid heavy/spicy meals.")

        # Context-aware tips
        context_insights = self._get_context_insights()
        if context_insights:
            plan.append("Address possible triggers: " + "; ".join(context_insights[:2]) + ".")
        context_guidance = self._get_context_guidance()
        if context_guidance:
            plan.append("Context-aware tips: " + "; ".join(context_guidance[:2]) + ".")

        # Risk level reminder
        if risk_level == 'high_risk':
            plan.append("Given the risk level, seek prompt medical care today.")
        elif risk_level == 'medium_risk':
            plan.append("If symptoms worsen or persist, schedule a visit within 1-2 days.")
        else:
            plan.append("If symptoms persist beyond a week, consult a healthcare provider.")

        response = "✨ **ReliefPath: Your 24-Hour Plan (Clinic-Hurdle Replacer)**\n\n"
        for item in plan:
            response += f"• {item}\n"

        response += "\nReply `summary` for a doctor-ready summary or `restart` to start a new consultation."
        return response

    def format_doctor_summary_response(self):
        """Generate a concise, doctor-ready summary."""
        assessment = self.generate_assessment()

        age = f"{self.patient_age}" if self.patient_age else "Not provided"
        gender = f"{self.patient_gender}" if self.patient_gender else "Not provided"
        duration = f"{self.duration_days} days" if self.duration_days else "Not specified"
        display_symptoms = self.get_display_symptoms()
        symptoms = ", ".join(display_symptoms) if display_symptoms else "Not specified"

        response = "📝 **Doctor-Ready Summary (Share This at a Clinic)**\n\n"
        response += f"• Age/Gender: {age} / {gender}\n"
        response += f"• Duration: {duration}\n"
        response += f"• Symptoms: {symptoms}\n"
        if self.cough_type:
            response += f"• Cough Type: {self.cough_type.title()}\n"
        response += f"• Risk Level: {assessment['risk_level'].replace('_', ' ').title()}\n"

        if assessment['possible_conditions']:
            top_conditions = ", ".join([c['description'].title() for c in assessment['possible_conditions']])
            response += f"• Possible Conditions: {top_conditions}\n"

        context_insights = self._get_context_insights()
        if context_insights:
            response += f"• Possible Contributors: {', '.join(context_insights)}\n"

        if self.current_meds:
            interactions = self.check_med_interactions()
            response += f"• Current Meds: {', '.join([m.title() for m in self.current_meds])}\n"
            if interactions:
                response += "• Interaction Alerts: " + "; ".join([i['message'] for i in interactions]) + "\n"

        response += "\nQuestions to ask a clinician:\n"
        response += "• What tests (if any) do I need?\n"
        response += "• What warning signs should make me seek urgent care?\n"
        response += "• How should I manage symptoms at home?\n"

        response += "\nReply `plan` for a 24-hour relief plan or `restart` to start a new consultation."
        return response

    def _get_context_insights(self) -> List[str]:
        """Translate lifestyle flags into human-readable insights."""
        insights = []
        if self.lifestyle_context.get('sleep_deprivation'):
            insights.append("Recent sleep loss may be worsening symptoms")
        if self.lifestyle_context.get('stress'):
            insights.append("Stress can amplify pain and fatigue")
        if self.lifestyle_context.get('screen_time'):
            insights.append("Heavy screen time may trigger headaches/eye strain")
        if self.lifestyle_context.get('dehydration'):
            insights.append("Possible dehydration could contribute to dizziness/headache")
        if self.lifestyle_context.get('skipped_meals'):
            insights.append("Skipping meals can worsen fatigue or nausea")
        if self.lifestyle_context.get('sick_contact'):
            insights.append("Recent exposure to someone sick increases infection likelihood")
        if self.lifestyle_context.get('recent_travel'):
            insights.append("Recent travel can increase exposure to new infections")
        if self.lifestyle_context.get('smoking'):
            insights.append("Smoking/vaping can worsen respiratory symptoms")
        if self.lifestyle_context.get('alcohol'):
            insights.append("Alcohol can worsen dehydration and sleep quality")
        return insights

    def _get_context_guidance(self) -> List[str]:
        """Provide actionable guidance based on lifestyle flags."""
        tips = []
        if self.lifestyle_context.get('sleep_deprivation'):
            tips.append("Prioritize sleep tonight (7–9 hours) and take a short nap if needed.")
        if self.lifestyle_context.get('dehydration'):
            tips.append("Increase fluids; sip water or ORS regularly through the day.")
        if self.lifestyle_context.get('stress'):
            tips.append("Reduce stress triggers and try a 3–5 minute breathing break.")
        if self.lifestyle_context.get('screen_time'):
            tips.append("Take screen breaks every 20–30 minutes to reduce strain.")
        if self.lifestyle_context.get('skipped_meals'):
            tips.append("Have small, regular meals to stabilize energy and nausea.")
        if self.lifestyle_context.get('sick_contact'):
            tips.append("Limit close contact, wash hands often, and consider a mask if coughing.")
        if self.lifestyle_context.get('recent_travel'):
            tips.append("Monitor for fever or new symptoms after travel and note exposures.")
        if self.lifestyle_context.get('smoking'):
            tips.append("Avoid smoking/vaping while symptoms are active.")
        if self.lifestyle_context.get('alcohol'):
            tips.append("Avoid alcohol while recovering to prevent dehydration.")
        return tips
    
    def _get_medication_recommendations(self, possible_conditions):
        """Get medication recommendations based on identified conditions"""
        from medical_knowledge import MEDICATION_RECOMMENDATIONS
        
        symptom_text = ' '.join(self.reported_symptoms).lower()

        # Targeted OTC-friendly suggestions for GI symptoms
        if any(word in symptom_text for word in ['nausea', 'vomiting', 'stomach upset', 'indigestion', 'heartburn']):
            return self._filter_medications(MEDICATION_RECOMMENDATIONS.get('nausea', {}).get('medications', []))
        if 'diarrhea' in symptom_text:
            return self._filter_medications(MEDICATION_RECOMMENDATIONS.get('diarrhea', {}).get('medications', []))
        if 'cough' in symptom_text:
            return self._filter_medications(MEDICATION_RECOMMENDATIONS.get('cough', {}).get('medications', []))

        if not possible_conditions:
            return self._filter_medications(MEDICATION_RECOMMENDATIONS.get('general', {}).get('medications', []))
        
        # Get medications for the top matching condition
        top_condition = possible_conditions[0]['name']
        
        # Check if we have specific medications for this condition
        if top_condition in MEDICATION_RECOMMENDATIONS:
            meds = MEDICATION_RECOMMENDATIONS[top_condition]['medications']
            return self._filter_medications(meds)
        
        # Check for headache-specific medications
        if 'headache' in ' '.join(self.reported_symptoms):
            if 'migraine' in top_condition:
                return self._filter_medications(MEDICATION_RECOMMENDATIONS.get('migraine', {}).get('medications', []))
            else:
                return self._filter_medications(MEDICATION_RECOMMENDATIONS.get('headache', {}).get('medications', []))
        
        # Default to general medications
        return self._filter_medications(MEDICATION_RECOMMENDATIONS.get('general', {}).get('medications', []))

    def _filter_medications(self, medications):
        """Reduce medication list to essentials based on symptoms and safety."""
        if not medications:
            return []

        symptom_text = ' '.join(self.reported_symptoms).lower()

        # For cough, prefer targeted option based on cough type
        if 'cough' in symptom_text and self.cough_type:
            cough_pref = []
            for med in medications:
                name_lower = med['name'].lower()
                instructions = med.get('instructions', '').lower()
                if self.cough_type == 'dry' and any(k in name_lower or k in instructions for k in ['dextromethorphan', 'suppressant', 'dry']):
                    cough_pref.append(med)
                if self.cough_type == 'productive' and any(k in name_lower or k in instructions for k in ['guaifenesin', 'expectorant', 'phlegm', 'mucus']):
                    cough_pref.append(med)
            if cough_pref:
                return cough_pref[:1]

        # If fever present, prefer a single antipyretic, but allow one extra
        # symptom-targeted medicine if clearly needed.
        if 'fever' in symptom_text:
            primary = None
            for med in medications:
                if 'paracetamol' in med['name'].lower():
                    primary = med
                    break
            if primary:
                secondary = self._pick_secondary_medication(medications, symptom_text)
                return [primary] + ([secondary] if secondary else [])

        # Remove supplements and higher-risk Rx suggestions from generic advice
        banned_keywords = [
            'vitamin', 'multivitamin', 'zinc',
            'oseltamivir', 'antibiotic', 'amoxicillin', 'azithromycin', 'doxycycline',
            'ciprofloxacin', 'metronidazole', 'fluconazole', 'pred', 'dexamethasone',
            'ondansetron', 'metoclopramide', 'domperidone', 'prochlorperazine',
            'rifaximin'
        ]

        filtered = []
        for med in medications:
            name_lower = med['name'].lower()
            if any(keyword in name_lower for keyword in banned_keywords):
                continue
            filtered.append(med)

        return filtered[:2] if filtered else medications[:1]

    def _pick_secondary_medication(self, medications, symptom_text):
        """Pick one extra medication matched to non-fever symptoms."""
        if any(word in symptom_text for word in ['cough', 'sore throat', 'congestion', 'runny nose']):
            for med in medications:
                name_lower = med['name'].lower()
                if 'cough' in name_lower or 'decongestant' in name_lower or 'cetirizine' in name_lower:
                    return med

        if any(word in symptom_text for word in ['headache', 'body ache', 'muscle pain']):
            for med in medications:
                name_lower = med['name'].lower()
                if 'ibuprofen' in name_lower and 'paracetamol' not in name_lower:
                    return med

        return None
    
    def reset(self):
        """Reset analyzer state"""
        self.reported_symptoms = []
        self.symptom_categories = set()
        self.duration_days = None
        self.patient_age = None
        self.patient_gender = None
        self.followup_asked = set()
        self.lifestyle_context = {}
        self.symptom_severity = None
        self.temperature_c = None
        self.cough_type = None
        self.current_meds = []
        self.last_assessment = None
