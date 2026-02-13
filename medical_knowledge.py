"""
Medical Knowledge Base
Contains symptom definitions, conditions, risk rules, and emergency keywords
"""

# Emergency keywords that trigger immediate safety alerts
EMERGENCY_KEYWORDS = {
    'critical': [
        'chest pain', 'heart attack', 'stroke', 'can\'t breathe', 'cannot breathe',
        'difficulty breathing', 'choking', 'severe bleeding', 'heavy bleeding',
        'unconscious', 'passed out', 'suicide', 'suicidal', 'overdose',
        'severe head injury', 'seizure', 'convulsion', 'paralysis', 'numbness in face',
        'slurred speech', 'confusion', 'disoriented', 'severe burn', 'poisoning'
    ],
    'urgent': [
        'high fever', 'severe pain', 'vomiting blood', 'blood in stool',
        'severe headache', 'vision loss', 'sudden vision change', 'severe dizziness',
        'fainting', 'rapid heartbeat', 'irrytgular heartbeat', 'severe abdominal pain'
    ]
}

# Symptom categories and their associated symptoms
SYMPTOM_CATEGORIES = {
    'respiratory': [
        'cough', 'shortness of breath', 'wheezing', 'chest tightness',
        'runny nose', 'stuffy nose', 'congestion', 'sore throat',
        'difficulty breathing', 'rapid breathing', 'phlegm', 'mucus'
    ],
    'fever_related': [
        'fever', 'chills', 'sweating', 'night sweats', 'hot', 'cold',
        'temperature', 'shivering'
    ],
    'pain': [
        'headache', 'body ache', 'muscle pain', 'joint pain', 'back pain',
        'neck pain', 'chest pain', 'abdominal pain', 'stomach pain',
        'pain', 'ache', 'sore', 'tender'
    ],
    'gastrointestinal': [
        'nausea', 'vomiting', 'diarrhea', 'constipation', 'bloating',
        'stomach upset', 'indigestion', 'heartburn', 'loss of appetite',
        'abdominal cramps'
    ],
    'neurological': [
        'dizziness', 'vertigo', 'confusion', 'memory loss', 'numbness',
        'tingling', 'weakness', 'fatigue', 'tiredness', 'exhaustion',
        'lightheaded'
    ],
    'endocrine': [
        'thyroid', 'hypothyroid', 'hyperthyroid', 'goiter', 'neck swelling',
        'weight gain', 'weight loss', 'palpitations', 'heat intolerance',
        'cold intolerance', 'hair loss'
    ],
    'skin': [
        'rash', 'itching', 'hives', 'redness', 'swelling', 'bruising',
        'discoloration', 'spots', 'bumps'
    ],
    'ear_nose_throat': [
        'earache', 'ear pain', 'hearing loss', 'ringing in ears',
        'sore throat', 'hoarse voice', 'difficulty swallowing'
    ]
}

# Common conditions with their typical symptom patterns
CONDITIONS = {
    'common_cold': {
        'symptoms': ['runny nose', 'stuffy nose', 'sore throat', 'cough', 'mild headache'],
        'risk_level': 'low',
        'description': 'Common viral infection of the upper respiratory tract'
    },
    'flu': {
        'symptoms': ['fever', 'chills', 'body ache', 'fatigue', 'cough', 'headache', 'sore throat'],
        'risk_level': 'medium',
        'description': 'Influenza - viral infection affecting the respiratory system'
    },
    'gastroenteritis': {
        'symptoms': ['nausea', 'vomiting', 'diarrhea', 'abdominal cramps', 'fever'],
        'risk_level': 'medium',
        'description': 'Stomach flu - inflammation of the digestive tract'
    },
    'migraine': {
        'symptoms': ['severe headache', 'nausea', 'sensitivity to light', 'dizziness'],
        'risk_level': 'medium',
        'description': 'Severe recurring headache disorder'
    },
    'allergic_reaction': {
        'symptoms': ['rash', 'itching', 'hives', 'swelling', 'runny nose', 'sneezing'],
        'risk_level': 'low',
        'description': 'Immune system response to allergen'
    },
    'respiratory_infection': {
        'symptoms': ['cough', 'fever', 'chest tightness', 'shortness of breath', 'fatigue'],
        'risk_level': 'medium',
        'description': 'Infection affecting the respiratory system'
    },
    'dehydration': {
        'symptoms': ['dizziness', 'fatigue', 'dry mouth', 'headache', 'dark urine'],
        'risk_level': 'medium',
        'description': 'Insufficient fluid in the body'
    }
    ,
    'thyroid_disorder': {
        'symptoms': ['thyroid', 'weight gain', 'weight loss', 'fatigue', 'palpitations', 'heat intolerance', 'cold intolerance', 'neck swelling', 'hair loss'],
        'risk_level': 'medium',
        'description': 'Possible thyroid disorder (overactive or underactive)'
    }
}

# Follow-up questions based on symptom categories
FOLLOWUP_QUESTIONS = {
    'respiratory': [
        "Is your cough dry or are you bringing up phlegm?",
        "Do you experience shortness of breath during rest or only during activity?",
        "Have you noticed any wheezing sounds when breathing?",
        "Is there any chest tightness or discomfort?"
    ],
    'fever_related': [
        "What is your current temperature if you've measured it?",
        "Are you experiencing chills or night sweats?",
        "Does the fever come and go, or is it constant?",
        "Have you taken any fever-reducing medication?"
    ],
    'pain': [
        "On a scale of 1-10, how would you rate the pain intensity?",
        "Is the pain constant or does it come and go?",
        "Does anything make the pain better or worse?",
        "Does the pain radiate to other areas?",
        "Did you stay up late last night or have trouble sleeping?",
        "Have you been under a lot of stress lately?",
        "Have you been staring at screens (phone/computer) for long hours?",
        "Have you been drinking enough water today?",
        "Did you skip any meals or eat irregularly?"
    ],
    'gastrointestinal': [
        "How many times have you vomited/had diarrhea in the past 24 hours?",
        "Are you able to keep fluids down?",
        "Have you noticed any blood in vomit or stool?",
        "When did you last eat a normal meal?"
    ],
    'neurological': [
        "Did the dizziness/weakness come on suddenly or gradually?",
        "Do you feel confused or disoriented?",
        "Have you experienced any vision changes?",
        "Is there any numbness or tingling in your extremities?"
    ],
    'endocrine': [
        "Have you noticed weight changes, heat/cold intolerance, or palpitations?",
        "Any neck swelling, hoarseness, or throat pressure?",
        "Have you had thyroid tests or taken thyroid medication before?"
    ],
    'general': [
        "When did these symptoms first start?",
        "Have the symptoms been getting better, worse, or staying the same?",
        "Have you been in contact with anyone who is sick?",
        "Do you have any pre-existing medical conditions?",
        "Are you currently taking any medications?"
    ]
}

# Risk assessment rules
RISK_FACTORS = {
    'age': {
        'high_risk': [0, 5, 65, 120],  # Very young or elderly
        'medium_risk': [6, 17, 60, 64],
        'low_risk': [18, 59]
    },
    'symptom_combinations': {
        'high_risk': [
            ['fever', 'difficulty breathing', 'chest pain'],
            ['severe headache', 'confusion', 'fever'],
            ['vomiting', 'severe abdominal pain', 'fever'],
            ['chest pain', 'shortness of breath'],
            ['severe pain', 'fever', 'rapid heartbeat']
        ],
        'medium_risk': [
            ['fever', 'cough', 'fatigue'],
            ['headache', 'fever', 'body ache'],
            ['nausea', 'vomiting', 'diarrhea'],
            ['severe headache', 'nausea']
        ]
    },
    'duration': {
        'concerning': 7,  # Symptoms lasting more than 7 days
        'urgent': 3  # Severe symptoms lasting more than 3 days
    }
}

# Medical advice templates
ADVICE_TEMPLATES = {
    'low_risk': {
        'general': [
            "Get plenty of rest and stay hydrated",
            "Monitor your symptoms and note any changes",
            "Over-the-counter medications may help with symptom relief",
            "Maintain good hygiene to prevent spreading illness"
        ],
        'when_to_seek_care': "If symptoms worsen or persist beyond a week, please consult a healthcare provider."
    },
    'medium_risk': {
        'general': [
            "Rest and increase fluid intake",
            "Monitor your temperature regularly",
            "Keep track of symptom progression",
            "Avoid strenuous activities"
        ],
        'when_to_seek_care': "I recommend scheduling an appointment with your doctor within the next 1-2 days. If symptoms worsen, seek immediate medical attention."
    },
    'high_risk': {
        'general': [
            "This requires prompt medical evaluation",
            "Do not delay seeking professional care",
            "Keep someone informed of your condition"
        ],
        'when_to_seek_care': "Please seek immediate medical attention. Visit an urgent care center or emergency room today."
    }
}

# Emergency response templates
EMERGENCY_RESPONSES = {
    'critical': {
        'message': "⚠️ EMERGENCY SITUATION DETECTED ⚠️\n\nBased on your symptoms, this could be a medical emergency.",
        'actions': [
            "🚨 Call emergency services (911) immediately",
            "📞 If you're unable to call, ask someone nearby to help",
            "🏥 Go to the nearest emergency room",
            "⏰ Do not wait - seek help NOW"
        ],
        'additional': "While waiting for help: Stay calm, sit or lie down in a comfortable position, and do not eat or drink anything."
    },
    'urgent': {
        'message': "⚠️ URGENT MEDICAL ATTENTION NEEDED ⚠️\n\nYour symptoms require prompt medical evaluation.",
        'actions': [
            "🏥 Visit an urgent care center or emergency room today",
            "📞 Call your doctor immediately for guidance",
            "👤 Have someone accompany you if possible",
            "📝 Bring a list of your current medications"
        ],
        'additional': "Do not drive yourself if you feel dizzy, weak, or impaired in any way."
    }
}

# Medication recommendations for common conditions
MEDICATION_RECOMMENDATIONS = {
    'common_cold': {
        'medications': [
            {
                'name': 'Paracetamol (Crocin/Dolo 650)',
                'dosage': '1 tablet',
                'frequency': '3 times a day',
                'duration': '3-5 days',
                'timing': 'After breakfast, lunch, and dinner',
                'instructions': 'Take with water. Helps reduce fever and body aches. Do not take more than 3 tablets in 24 hours.'
            },
            {
                'name': 'Cetirizine (Zyrtec)',
                'dosage': '1 tablet',
                'frequency': 'Once daily',
                'duration': '5-7 days',
                'timing': 'At night before sleeping',
                'instructions': 'For runny nose and sneezing. May make you sleepy.'
            },
            {
                'name': 'Decongestant (Sinarest/D-Cold)',
                'dosage': '1 tablet',
                'frequency': '2-3 times a day',
                'duration': '3-5 days',
                'timing': 'Morning and evening after meals',
                'instructions': 'For blocked nose and cold symptoms. Avoid if you have high blood pressure.'
            },
            {
                'name': 'Vitamin C (500mg)',
                'dosage': '1 tablet',
                'frequency': 'Twice daily',
                'duration': '1 week',
                'timing': 'After breakfast and dinner',
                'instructions': 'Boosts immunity and helps recovery.'
            },
            {
                'name': 'Zinc tablets',
                'dosage': '1 tablet',
                'frequency': 'Once daily',
                'duration': '5 days',
                'timing': 'After any meal',
                'instructions': 'Helps reduce cold duration. Always take with food.'
            }
        ]
    },
    'flu': {
        'medications': [
            {
                'name': 'Oseltamivir (Tamiflu)',
                'dosage': '1 capsule',
                'frequency': 'Twice daily',
                'duration': '5 days',
                'timing': 'Morning and evening',
                'instructions': 'Antiviral medicine. Most effective when started within 2 days of flu symptoms. Take with or without food.'
            },
            {
                'name': 'Paracetamol (Dolo 650)',
                'dosage': '1 tablet',
                'frequency': '3 times a day',
                'duration': '5-7 days',
                'timing': 'After breakfast, lunch, and dinner',
                'instructions': 'For fever and body aches. Drink plenty of water.'
            },
            {
                'name': 'Ibuprofen (Brufen)',
                'dosage': '1 tablet',
                'frequency': '2-3 times a day',
                'duration': '3-5 days',
                'timing': 'After meals only',
                'instructions': 'For pain and inflammation. Never take on empty stomach.'
            },
            {
                'name': 'Cough syrup (Benadryl/Ascoril)',
                'dosage': '2 teaspoons (10ml)',
                'frequency': '3 times a day',
                'duration': '5 days',
                'timing': 'Morning, afternoon, and night',
                'instructions': 'For dry cough. May make you sleepy, avoid driving.'
            },
            {
                'name': 'Multivitamin with Zinc',
                'dosage': '1 tablet',
                'frequency': 'Once daily',
                'duration': '10 days',
                'timing': 'After breakfast',
                'instructions': 'Boosts immunity during recovery.'
            }
        ]
    },
    'headache': {
        'medications': [
            {
                'name': 'Paracetamol (Crocin)',
                'dosage': '1 tablet',
                'frequency': 'When needed (up to 3 times a day)',
                'duration': '2-3 days',
                'timing': 'After meals',
                'instructions': 'For mild to moderate headache. Drink plenty of water. Wait at least 6 hours between doses.'
            },
            {
                'name': 'Ibuprofen (Brufen)',
                'dosage': '1 tablet',
                'frequency': 'When needed (up to 2-3 times a day)',
                'duration': '2-3 days',
                'timing': 'After meals only',
                'instructions': 'Alternative to paracetamol. Avoid if you have stomach problems.'
            },
            {
                'name': 'Aspirin (Disprin)',
                'dosage': '1 tablet',
                'frequency': 'When needed',
                'duration': '2 days',
                'timing': 'After meals',
                'instructions': 'For headache relief. Not for children or teenagers.'
            },
            {
                'name': 'Saridon/Combiflam',
                'dosage': '1 tablet',
                'frequency': 'When needed',
                'duration': 'As needed',
                'timing': 'After meals',
                'instructions': 'Combination pain reliever. Avoid taking in evening as it contains caffeine.'
            }
        ]
    },
    'migraine': {
        'medications': [
            {
                'name': 'Sumatriptan',
                'dosage': '50mg',
                'frequency': 'At onset of migraine',
                'duration': 'As needed',
                'timing': 'Any time',
                'instructions': 'Take as soon as migraine starts. May repeat after 2 hours if needed. Max 200mg/day.'
            },
            {
                'name': 'Rizatriptan',
                'dosage': '10mg',
                'frequency': 'At onset',
                'duration': 'As needed',
                'timing': 'Any time',
                'instructions': 'Alternative to Sumatriptan. Dissolves on tongue.'
            },
            {
                'name': 'Naproxen',
                'dosage': '500mg',
                'frequency': 'Twice daily',
                'duration': 'During migraine',
                'timing': 'After meals',
                'instructions': 'NSAID for migraine pain. Take with food.'
            },
            {
                'name': 'Metoclopramide',
                'dosage': '10mg',
                'frequency': 'Three times daily',
                'duration': '2-3 days',
                'timing': '30 min before meals',
                'instructions': 'For nausea associated with migraine.'
            },
            {
                'name': 'Magnesium supplement',
                'dosage': '400mg',
                'frequency': 'Once daily',
                'duration': 'Ongoing prevention',
                'timing': 'At bedtime',
                'instructions': 'May help prevent migraines. Long-term use.'
            }
        ]
    },
    'gastroenteritis': {
        'medications': [
            {
                'name': 'ORS (Oral Rehydration Solution)',
                'dosage': '1 sachet in 1 liter water',
                'frequency': 'Sip frequently throughout day',
                'duration': '2-3 days',
                'timing': 'Any time',
                'instructions': 'Most important - prevents dehydration. Drink slowly.'
            },
            {
                'name': 'Loperamide (Imodium)',
                'dosage': '2mg',
                'frequency': 'After each loose stool (max 16mg/day)',
                'duration': '2 days',
                'timing': 'As needed',
                'instructions': 'For diarrhea. Stop if symptoms improve or fever develops.'
            },
            {
                'name': 'Ondansetron',
                'dosage': '4mg',
                'frequency': 'Every 8 hours',
                'duration': '2-3 days',
                'timing': 'Before meals',
                'instructions': 'For severe nausea and vomiting.'
            },
            {
                'name': 'Probiotics (Saccharomyces boulardii)',
                'dosage': '250mg',
                'frequency': 'Twice daily',
                'duration': '5-7 days',
                'timing': 'Before meals',
                'instructions': 'Helps restore gut bacteria and reduce diarrhea duration.'
            },
            {
                'name': 'Zinc sulfate',
                'dosage': '20mg',
                'frequency': 'Once daily',
                'duration': '10-14 days',
                'timing': 'After meals',
                'instructions': 'Reduces duration of diarrhea, especially in children.'
            }
        ]
    },
    'nausea': {
        'medications': [
            {
                'name': 'Bismuth subsalicylate (Chewable tablets)',
                'dosage': '2 tablets',
                'frequency': 'Every 30-60 minutes as needed',
                'duration': 'Up to 2 days',
                'timing': 'As needed',
                'instructions': 'For nausea/upset stomach. Avoid if aspirin allergy, on blood thinners, pregnant, or under 12. May darken tongue/stool.'
            },
            {
                'name': 'Antacid (Calcium carbonate)',
                'dosage': '1-2 chewable tablets',
                'frequency': 'Up to 4 times/day as needed',
                'duration': '2-3 days',
                'timing': 'After meals or at bedtime',
                'instructions': 'Helpful if nausea comes with acidity/heartburn.'
            }
        ]
    },
    'cough': {
        'medications': [
            {
                'name': 'Dextromethorphan (Cough suppressant)',
                'dosage': '10-20mg',
                'frequency': 'Every 4-6 hours as needed',
                'duration': '3-5 days',
                'timing': 'As needed',
                'instructions': 'Best for dry cough. Avoid if taking MAOIs or if you have asthma without clinician advice.'
            },
            {
                'name': 'Guaifenesin (Expectorant)',
                'dosage': '200-400mg',
                'frequency': 'Every 4 hours as needed',
                'duration': '3-5 days',
                'timing': 'With plenty of water',
                'instructions': 'Best for wet cough with phlegm. Drink water to help loosen mucus.'
            },
            {
                'name': 'Throat lozenges',
                'dosage': '1 lozenge',
                'frequency': 'Every 2-3 hours as needed',
                'duration': 'As needed',
                'timing': 'As needed',
                'instructions': 'Soothes throat irritation from coughing.'
            }
        ]
    },
    'respiratory_infection': {
        'medications': [
            {
                'name': 'Azithromycin (Zithromax)',
                'dosage': '500mg',
                'frequency': 'Once daily',
                'duration': '3 days',
                'timing': 'After meals',
                'instructions': 'Antibiotic - complete full course even if feeling better.'
            },
            {
                'name': 'Amoxicillin',
                'dosage': '500mg',
                'frequency': 'Three times daily',
                'duration': '7 days',
                'timing': 'After meals',
                'instructions': 'Alternative antibiotic. Complete full course.'
            },
            {
                'name': 'Paracetamol',
                'dosage': '500mg',
                'frequency': 'Every 6-8 hours',
                'duration': '5 days',
                'timing': 'After meals',
                'instructions': 'For fever and discomfort.'
            },
            {
                'name': 'Guaifenesin (Expectorant)',
                'dosage': '200mg',
                'frequency': 'Every 4 hours',
                'duration': '5-7 days',
                'timing': 'With plenty of water',
                'instructions': 'Helps loosen mucus. Drink lots of fluids.'
            },
            {
                'name': 'Bromhexine',
                'dosage': '8mg',
                'frequency': 'Three times daily',
                'duration': '5-7 days',
                'timing': 'After meals',
                'instructions': 'Mucolytic - helps clear chest congestion.'
            },
            {
                'name': 'Vitamin C',
                'dosage': '1000mg',
                'frequency': 'Once daily',
                'duration': '10 days',
                'timing': 'After breakfast',
                'instructions': 'Supports immune function during infection.'
            }
        ]
    },
    'allergic_reaction': {
        'medications': [
            {
                'name': 'Cetirizine (Zyrtec)',
                'dosage': '10mg',
                'frequency': 'Once daily',
                'duration': '5-7 days',
                'timing': 'At bedtime',
                'instructions': 'Antihistamine for allergy symptoms. May cause drowsiness.'
            },
            {
                'name': 'Loratadine (Claritin)',
                'dosage': '10mg',
                'frequency': 'Once daily',
                'duration': '5-7 days',
                'timing': 'Morning',
                'instructions': 'Non-drowsy antihistamine alternative.'
            },
            {
                'name': 'Fexofenadine (Allegra)',
                'dosage': '120mg',
                'frequency': 'Once daily',
                'duration': '5-7 days',
                'timing': 'Morning',
                'instructions': 'Non-drowsy, fast-acting antihistamine.'
            },
            {
                'name': 'Prednisolone',
                'dosage': '20mg',
                'frequency': 'Once daily',
                'duration': '5 days (tapering)',
                'timing': 'Morning after breakfast',
                'instructions': 'Steroid for severe allergic reactions. Follow tapering schedule.'
            },
            {
                'name': 'Hydrocortisone Cream 1%',
                'dosage': 'Apply thin layer',
                'frequency': 'Twice daily',
                'duration': '5-7 days',
                'timing': 'Morning and night',
                'instructions': 'For skin rash/itching. Apply to affected area only.'
            },
            {
                'name': 'Calamine Lotion',
                'dosage': 'Apply as needed',
                'frequency': '3-4 times daily',
                'duration': '5-7 days',
                'timing': 'Any time',
                'instructions': 'Soothes itchy skin. Let dry before dressing.'
            }
        ]
    },
    'urinary_tract_infection': {
        'medications': [
            {
                'name': 'Nitrofurantoin',
                'dosage': '100mg',
                'frequency': 'Twice daily',
                'duration': '5-7 days',
                'timing': 'After meals',
                'instructions': 'Antibiotic for UTI. Take with food. Urine may turn dark yellow/brown.'
            },
            {
                'name': 'Trimethoprim-Sulfamethoxazole (Bactrim)',
                'dosage': '800mg/160mg',
                'frequency': 'Twice daily',
                'duration': '3 days',
                'timing': 'After meals',
                'instructions': 'Alternative antibiotic. Drink plenty of water.'
            },
            {
                'name': 'Phenazopyridine (Pyridium)',
                'dosage': '200mg',
                'frequency': 'Three times daily',
                'duration': '2 days',
                'timing': 'After meals',
                'instructions': 'For urinary pain/burning. Will turn urine orange/red.'
            },
            {
                'name': 'Cranberry extract',
                'dosage': '500mg',
                'frequency': 'Twice daily',
                'duration': '7-10 days',
                'timing': 'Any time',
                'instructions': 'May help prevent recurrence. Not a substitute for antibiotics.'
            }
        ]
    },
    'acid_reflux': {
        'medications': [
            {
                'name': 'Omeprazole (Prilosec)',
                'dosage': '20mg',
                'frequency': 'Once daily',
                'duration': '14 days',
                'timing': '30 min before breakfast',
                'instructions': 'PPI for acid reduction. Take on empty stomach.'
            },
            {
                'name': 'Pantoprazole',
                'dosage': '40mg',
                'frequency': 'Once daily',
                'duration': '14 days',
                'timing': 'Before breakfast',
                'instructions': 'Alternative PPI. More effective than antacids.'
            },
            {
                'name': 'Ranitidine alternative (Famotidine)',
                'dosage': '20mg',
                'frequency': 'Twice daily',
                'duration': '14 days',
                'timing': 'Before meals',
                'instructions': 'H2 blocker. Works faster than PPIs.'
            },
            {
                'name': 'Antacid (Aluminum/Magnesium hydroxide)',
                'dosage': '10ml',
                'frequency': 'As needed (max 4 times/day)',
                'duration': '7 days',
                'timing': '1 hour after meals',
                'instructions': 'For immediate relief. Shake well before use.'
            },
            {
                'name': 'Sucralfate',
                'dosage': '1g',
                'frequency': 'Four times daily',
                'duration': '14 days',
                'timing': '1 hour before meals and bedtime',
                'instructions': 'Coats and protects stomach lining.'
            }
        ]
    },
    'anxiety': {
        'medications': [
            {
                'name': 'Alprazolam (Xanax)',
                'dosage': '0.25mg',
                'frequency': 'Twice daily as needed',
                'duration': 'Short-term only',
                'timing': 'Morning and evening',
                'instructions': 'For acute anxiety. Habit-forming - use short-term only. Avoid alcohol.'
            },
            {
                'name': 'Propranolol',
                'dosage': '10mg',
                'frequency': 'As needed before stressful events',
                'duration': 'As needed',
                'timing': '1 hour before event',
                'instructions': 'For performance anxiety. Reduces physical symptoms.'
            },
            {
                'name': 'Hydroxyzine',
                'dosage': '25mg',
                'frequency': 'Twice daily',
                'duration': '7-14 days',
                'timing': 'Morning and bedtime',
                'instructions': 'Non-addictive anti-anxiety. May cause drowsiness.'
            },
            {
                'name': 'Ashwagandha',
                'dosage': '300mg',
                'frequency': 'Twice daily',
                'duration': 'Ongoing',
                'timing': 'After meals',
                'instructions': 'Natural supplement for stress. Takes 2-4 weeks for effect.'
            }
        ]
    },
    'insomnia': {
        'medications': [
            {
                'name': 'Melatonin',
                'dosage': '3mg',
                'frequency': 'Once daily',
                'duration': '7-14 days',
                'timing': '30 min before bedtime',
                'instructions': 'Natural sleep aid. Start with low dose.'
            },
            {
                'name': 'Zolpidem (Ambien)',
                'dosage': '5mg',
                'frequency': 'Once daily',
                'duration': 'Short-term (7-10 days)',
                'timing': 'Right before bed',
                'instructions': 'Prescription sleep aid. Ensure 7-8 hours for sleep. Habit-forming.'
            },
            {
                'name': 'Diphenhydramine (Benadryl)',
                'dosage': '25mg',
                'frequency': 'Once daily',
                'duration': '3-5 days',
                'timing': '30 min before bed',
                'instructions': 'OTC sleep aid. May cause next-day drowsiness.'
            },
            {
                'name': 'Magnesium glycinate',
                'dosage': '400mg',
                'frequency': 'Once daily',
                'duration': 'Ongoing',
                'timing': 'Before bedtime',
                'instructions': 'Promotes relaxation and sleep. Gentle on stomach.'
            }
        ]
    },
    'hypertension': {
        'medications': [
            {
                'name': 'Amlodipine',
                'dosage': '5mg',
                'frequency': 'Once daily',
                'duration': 'Long-term',
                'timing': 'Same time daily',
                'instructions': 'Calcium channel blocker. Monitor blood pressure regularly.'
            },
            {
                'name': 'Losartan',
                'dosage': '50mg',
                'frequency': 'Once daily',
                'duration': 'Long-term',
                'timing': 'Morning',
                'instructions': 'ARB for blood pressure. May take 3-6 weeks for full effect.'
            },
            {
                'name': 'Hydrochlorothiazide',
                'dosage': '12.5mg',
                'frequency': 'Once daily',
                'duration': 'Long-term',
                'timing': 'Morning',
                'instructions': 'Diuretic. May increase urination. Take potassium supplement if needed.'
            }
        ]
    },
    'diabetes_type2': {
        'medications': [
            {
                'name': 'Metformin',
                'dosage': '500mg',
                'frequency': 'Twice daily',
                'duration': 'Long-term',
                'timing': 'With meals',
                'instructions': 'First-line diabetes medication. May cause GI upset initially.'
            },
            {
                'name': 'Glimepiride',
                'dosage': '2mg',
                'frequency': 'Once daily',
                'duration': 'Long-term',
                'timing': 'Before breakfast',
                'instructions': 'Sulfonylurea. Monitor for low blood sugar.'
            },
            {
                'name': 'Sitagliptin (Januvia)',
                'dosage': '100mg',
                'frequency': 'Once daily',
                'duration': 'Long-term',
                'timing': 'Any time',
                'instructions': 'DPP-4 inhibitor. Can be taken with or without food.'
            }
        ]
    },
    'general': {
        'medications': [
            {
                'name': 'Paracetamol',
                'dosage': '500mg',
                'frequency': 'Every 6-8 hours as needed',
                'duration': '3-5 days',
                'timing': 'After meals',
                'instructions': 'For general pain and fever relief. Safe for most people.'
            },
            {
                'name': 'Ibuprofen',
                'dosage': '400mg',
                'frequency': 'Every 8 hours as needed',
                'duration': '3-5 days',
                'timing': 'After meals',
                'instructions': 'NSAID for pain and inflammation. Take with food.'
            },
            {
                'name': 'Multivitamin',
                'dosage': '1 tablet',
                'frequency': 'Once daily',
                'duration': '30 days',
                'timing': 'After breakfast',
                'instructions': 'General health support during recovery.'
            },
            {
                'name': 'Vitamin D3',
                'dosage': '1000 IU',
                'frequency': 'Once daily',
                'duration': 'Ongoing',
                'timing': 'With any meal',
                'instructions': 'For bone health and immunity. Fat-soluble vitamin.'
            }
        ]
    },
    'asthma': {
        'medications': [
            {
                'name': 'Salbutamol (Albuterol) Inhaler',
                'dosage': '2 puffs',
                'frequency': 'Every 4-6 hours as needed',
                'duration': 'Ongoing',
                'timing': 'When wheezing/breathless',
                'instructions': 'Rescue inhaler. Rinse mouth after use. Carry with you always.'
            },
            {
                'name': 'Budesonide Inhaler',
                'dosage': '200mcg',
                'frequency': 'Twice daily',
                'duration': 'Long-term',
                'timing': 'Morning and evening',
                'instructions': 'Preventive steroid inhaler. Rinse mouth after use to prevent thrush.'
            },
            {
                'name': 'Montelukast (Singulair)',
                'dosage': '10mg',
                'frequency': 'Once daily',
                'duration': 'Long-term',
                'timing': 'Evening',
                'instructions': 'Leukotriene modifier. Helps prevent asthma attacks.'
            },
            {
                'name': 'Prednisolone (for acute attacks)',
                'dosage': '40mg',
                'frequency': 'Once daily',
                'duration': '5-7 days',
                'timing': 'Morning with food',
                'instructions': 'For asthma exacerbations. Take full course as prescribed.'
            }
        ]
    },
    'bronchitis': {
        'medications': [
            {
                'name': 'Amoxicillin-Clavulanate (Augmentin)',
                'dosage': '625mg',
                'frequency': 'Three times daily',
                'duration': '7 days',
                'timing': 'After meals',
                'instructions': 'Antibiotic for bacterial bronchitis. Complete full course.'
            },
            {
                'name': 'Doxycycline',
                'dosage': '100mg',
                'frequency': 'Twice daily',
                'duration': '7 days',
                'timing': 'After meals',
                'instructions': 'Alternative antibiotic. Avoid sun exposure. Take with plenty of water.'
            },
            {
                'name': 'Guaifenesin',
                'dosage': '400mg',
                'frequency': 'Every 4 hours',
                'duration': '7 days',
                'timing': 'With water',
                'instructions': 'Expectorant to loosen mucus. Drink 8 glasses of water daily.'
            },
            {
                'name': 'Codeine cough syrup',
                'dosage': '10ml',
                'frequency': 'Every 6 hours',
                'duration': '5 days',
                'timing': 'As needed',
                'instructions': 'For persistent cough. May cause drowsiness. Avoid driving.'
            }
        ]
    },
    'sinusitis': {
        'medications': [
            {
                'name': 'Amoxicillin',
                'dosage': '500mg',
                'frequency': 'Three times daily',
                'duration': '10 days',
                'timing': 'After meals',
                'instructions': 'Antibiotic for bacterial sinusitis. Complete full course.'
            },
            {
                'name': 'Pseudoephedrine',
                'dosage': '60mg',
                'frequency': 'Every 6 hours',
                'duration': '5-7 days',
                'timing': 'After meals',
                'instructions': 'Decongestant. Avoid if you have high blood pressure or heart issues.'
            },
            {
                'name': 'Fluticasone nasal spray',
                'dosage': '2 sprays each nostril',
                'frequency': 'Once daily',
                'duration': '14 days',
                'timing': 'Morning',
                'instructions': 'Steroid nasal spray. Point away from septum. May take 3-5 days for effect.'
            },
            {
                'name': 'Saline nasal irrigation',
                'dosage': '1 bottle',
                'frequency': '2-3 times daily',
                'duration': '7-10 days',
                'timing': 'Any time',
                'instructions': 'Rinses sinuses. Use distilled or boiled water only.'
            }
        ]
    },
    'tonsillitis': {
        'medications': [
            {
                'name': 'Penicillin V',
                'dosage': '500mg',
                'frequency': 'Four times daily',
                'duration': '10 days',
                'timing': 'Every 6 hours',
                'instructions': 'Antibiotic for strep throat. Must complete full 10-day course.'
            },
            {
                'name': 'Azithromycin',
                'dosage': '500mg',
                'frequency': 'Once daily',
                'duration': '5 days',
                'timing': 'After meals',
                'instructions': 'Alternative if allergic to penicillin. Take full course.'
            },
            {
                'name': 'Benzydamine throat spray',
                'dosage': '4-8 sprays',
                'frequency': 'Every 2-3 hours',
                'duration': '5-7 days',
                'timing': 'As needed',
                'instructions': 'Local anesthetic for throat pain. Do not swallow immediately.'
            },
            {
                'name': 'Chlorhexidine mouthwash',
                'dosage': '10ml',
                'frequency': 'Twice daily',
                'duration': '7 days',
                'timing': 'After brushing',
                'instructions': 'Antiseptic gargle. Do not eat/drink for 30 min after use.'
            }
        ]
    },
    'skin_infection': {
        'medications': [
            {
                'name': 'Cephalexin',
                'dosage': '500mg',
                'frequency': 'Four times daily',
                'duration': '7-10 days',
                'timing': 'Every 6 hours',
                'instructions': 'Antibiotic for skin infections. Take with or without food.'
            },
            {
                'name': 'Clindamycin',
                'dosage': '300mg',
                'frequency': 'Four times daily',
                'duration': '7-10 days',
                'timing': 'Every 6 hours',
                'instructions': 'For MRSA or penicillin allergy. Take with full glass of water.'
            },
            {
                'name': 'Mupirocin ointment 2%',
                'dosage': 'Apply thin layer',
                'frequency': 'Three times daily',
                'duration': '7-10 days',
                'timing': 'After cleaning area',
                'instructions': 'Topical antibiotic. Cover with bandage if needed.'
            },
            {
                'name': 'Fusidic acid cream',
                'dosage': 'Apply thin layer',
                'frequency': 'Three times daily',
                'duration': '7 days',
                'timing': 'After cleaning',
                'instructions': 'For impetigo and minor skin infections.'
            }
        ]
    },
    'eczema_dermatitis': {
        'medications': [
            {
                'name': 'Betamethasone cream 0.1%',
                'dosage': 'Apply thin layer',
                'frequency': 'Twice daily',
                'duration': '7-14 days',
                'timing': 'Morning and night',
                'instructions': 'Potent steroid cream. Use sparingly. Not for face unless directed.'
            },
            {
                'name': 'Triamcinolone cream 0.1%',
                'dosage': 'Apply thin layer',
                'frequency': 'Twice daily',
                'duration': '7-14 days',
                'timing': 'Morning and night',
                'instructions': 'Medium-potency steroid. Apply to affected areas only.'
            },
            {
                'name': 'Cetirizine',
                'dosage': '10mg',
                'frequency': 'Once daily',
                'duration': '14-30 days',
                'timing': 'Evening',
                'instructions': 'For itching. May cause drowsiness.'
            },
            {
                'name': 'Emollient cream (Cetaphil/CeraVe)',
                'dosage': 'Apply liberally',
                'frequency': '3-4 times daily',
                'duration': 'Ongoing',
                'timing': 'After bathing and as needed',
                'instructions': 'Moisturizer to prevent dryness. Apply to damp skin.'
            }
        ]
    },
    'fungal_infection': {
        'medications': [
            {
                'name': 'Fluconazole',
                'dosage': '150mg',
                'frequency': 'Once weekly',
                'duration': '2-4 weeks',
                'timing': 'Any time',
                'instructions': 'For yeast infections. Single dose for vaginal, weekly for skin.'
            },
            {
                'name': 'Terbinafine',
                'dosage': '250mg',
                'frequency': 'Once daily',
                'duration': '6-12 weeks',
                'timing': 'After meals',
                'instructions': 'For nail fungus. Requires liver function monitoring.'
            },
            {
                'name': 'Clotrimazole cream 1%',
                'dosage': 'Apply thin layer',
                'frequency': 'Twice daily',
                'duration': '14-28 days',
                'timing': 'Morning and night',
                'instructions': 'For athlete\'s foot, ringworm, jock itch. Continue 1 week after clearing.'
            },
            {
                'name': 'Ketoconazole shampoo 2%',
                'dosage': 'Apply to scalp',
                'frequency': 'Twice weekly',
                'duration': '4-8 weeks',
                'timing': 'During shower',
                'instructions': 'For scalp fungus/dandruff. Leave on 5 minutes before rinsing.'
            }
        ]
    },
    'acne': {
        'medications': [
            {
                'name': 'Doxycycline',
                'dosage': '100mg',
                'frequency': 'Once daily',
                'duration': '8-12 weeks',
                'timing': 'After breakfast',
                'instructions': 'Antibiotic for moderate acne. Use sunscreen. Avoid dairy 2 hours before/after.'
            },
            {
                'name': 'Isotretinoin (Accutane)',
                'dosage': '20mg',
                'frequency': 'Once daily',
                'duration': '4-6 months',
                'timing': 'With fatty meal',
                'instructions': 'For severe acne. Requires monitoring. AVOID PREGNANCY. Very drying.'
            },
            {
                'name': 'Adapalene gel 0.1%',
                'dosage': 'Apply pea-sized amount',
                'frequency': 'Once daily',
                'duration': 'Ongoing',
                'timing': 'Night',
                'instructions': 'Retinoid gel. Start every other night. Use sunscreen daily.'
            },
            {
                'name': 'Benzoyl peroxide 5%',
                'dosage': 'Apply thin layer',
                'frequency': 'Once or twice daily',
                'duration': 'Ongoing',
                'timing': 'After cleansing',
                'instructions': 'Antibacterial. May bleach fabrics. Start with lower strength.'
            },
            {
                'name': 'Clindamycin gel 1%',
                'dosage': 'Apply thin layer',
                'frequency': 'Twice daily',
                'duration': '8-12 weeks',
                'timing': 'Morning and night',
                'instructions': 'Topical antibiotic. Best combined with benzoyl peroxide.'
            }
        ]
    },
    'conjunctivitis': {
        'medications': [
            {
                'name': 'Moxifloxacin eye drops 0.5%',
                'dosage': '1 drop each eye',
                'frequency': 'Three times daily',
                'duration': '7 days',
                'timing': 'Every 8 hours',
                'instructions': 'Antibiotic eye drops. Do not touch dropper to eye. Discard after treatment.'
            },
            {
                'name': 'Tobramycin eye drops',
                'dosage': '1-2 drops',
                'frequency': 'Every 4 hours',
                'duration': '5-7 days',
                'timing': 'While awake',
                'instructions': 'For bacterial conjunctivitis. Refrigerate after opening.'
            },
            {
                'name': 'Artificial tears',
                'dosage': '1-2 drops',
                'frequency': 'Every 2-4 hours',
                'duration': 'As needed',
                'timing': 'Any time',
                'instructions': 'For viral conjunctivitis comfort. Preservative-free preferred.'
            },
            {
                'name': 'Ketotifen eye drops',
                'dosage': '1 drop each eye',
                'frequency': 'Twice daily',
                'duration': '7-14 days',
                'timing': 'Morning and evening',
                'instructions': 'For allergic conjunctivitis. Remove contacts before use.'
            }
        ]
    },
    'ear_infection': {
        'medications': [
            {
                'name': 'Amoxicillin',
                'dosage': '500mg',
                'frequency': 'Three times daily',
                'duration': '7-10 days',
                'timing': 'Every 8 hours',
                'instructions': 'For middle ear infection. Complete full course even if feeling better.'
            },
            {
                'name': 'Ciprofloxacin ear drops',
                'dosage': '4 drops',
                'frequency': 'Twice daily',
                'duration': '7 days',
                'timing': 'Morning and evening',
                'instructions': 'For outer ear infection. Warm to room temp. Lie down 5 min after instilling.'
            },
            {
                'name': 'Ofloxacin ear drops',
                'dosage': '5 drops',
                'frequency': 'Twice daily',
                'duration': '7 days',
                'timing': 'Morning and evening',
                'instructions': 'Alternative ear drops. Keep ear dry during treatment.'
            },
            {
                'name': 'Acetic acid ear drops',
                'dosage': '3-4 drops',
                'frequency': 'Three times daily',
                'duration': '7 days',
                'timing': 'Every 8 hours',
                'instructions': 'For swimmer\'s ear. Creates acidic environment hostile to bacteria.'
            }
        ]
    },
    'thyroid_hypothyroid': {
        'medications': [
            {
                'name': 'Levothyroxine (Synthroid)',
                'dosage': '50mcg',
                'frequency': 'Once daily',
                'duration': 'Lifelong',
                'timing': '30-60 min before breakfast',
                'instructions': 'Thyroid hormone replacement. Take on empty stomach. Consistent timing crucial.'
            },
            {
                'name': 'Liothyronine (T3)',
                'dosage': '5mcg',
                'frequency': 'Once or twice daily',
                'duration': 'Lifelong',
                'timing': 'Morning',
                'instructions': 'For T3 supplementation. Usually combined with levothyroxine.'
            }
        ]
    },
    'cholesterol': {
        'medications': [
            {
                'name': 'Atorvastatin (Lipitor)',
                'dosage': '20mg',
                'frequency': 'Once daily',
                'duration': 'Long-term',
                'timing': 'Evening',
                'instructions': 'Statin for cholesterol. Avoid grapefruit. Monitor liver function.'
            },
            {
                'name': 'Rosuvastatin (Crestor)',
                'dosage': '10mg',
                'frequency': 'Once daily',
                'duration': 'Long-term',
                'timing': 'Evening',
                'instructions': 'Potent statin. Report muscle pain immediately.'
            },
            {
                'name': 'Ezetimibe (Zetia)',
                'dosage': '10mg',
                'frequency': 'Once daily',
                'duration': 'Long-term',
                'timing': 'Any time',
                'instructions': 'Cholesterol absorption inhibitor. Often combined with statin.'
            },
            {
                'name': 'Fenofibrate',
                'dosage': '145mg',
                'frequency': 'Once daily',
                'duration': 'Long-term',
                'timing': 'With meals',
                'instructions': 'For high triglycerides. Monitor kidney function.'
            }
        ]
    },
    'osteoporosis': {
        'medications': [
            {
                'name': 'Alendronate (Fosamax)',
                'dosage': '70mg',
                'frequency': 'Once weekly',
                'duration': 'Long-term',
                'timing': 'First thing in morning',
                'instructions': 'Take with full glass water. Stay upright 30 min. Nothing else for 30 min.'
            },
            {
                'name': 'Calcium carbonate',
                'dosage': '500mg',
                'frequency': 'Twice daily',
                'duration': 'Ongoing',
                'timing': 'With meals',
                'instructions': 'For bone health. Take with vitamin D for better absorption.'
            },
            {
                'name': 'Vitamin D3',
                'dosage': '2000 IU',
                'frequency': 'Once daily',
                'duration': 'Ongoing',
                'timing': 'With calcium',
                'instructions': 'Essential for calcium absorption and bone health.'
            }
        ]
    },
    'arthritis_rheumatoid': {
        'medications': [
            {
                'name': 'Methotrexate',
                'dosage': '15mg',
                'frequency': 'Once weekly',
                'duration': 'Long-term',
                'timing': 'Same day each week',
                'instructions': 'DMARD for RA. Take folic acid 1mg daily. Avoid alcohol. Monitor liver.'
            },
            {
                'name': 'Hydroxychloroquine (Plaquenil)',
                'dosage': '200mg',
                'frequency': 'Twice daily',
                'duration': 'Long-term',
                'timing': 'With meals',
                'instructions': 'For mild RA. Eye exams every 6-12 months required.'
            },
            {
                'name': 'Sulfasalazine',
                'dosage': '500mg',
                'frequency': 'Twice daily initially',
                'duration': 'Long-term',
                'timing': 'After meals',
                'instructions': 'DMARD. Gradually increase dose. May turn urine orange.'
            },
            {
                'name': 'Prednisone',
                'dosage': '5-10mg',
                'frequency': 'Once daily',
                'duration': 'Short-term or low-dose long-term',
                'timing': 'Morning with food',
                'instructions': 'Steroid for inflammation. Lowest effective dose. Taper slowly.'
            }
        ]
    },
    'osteoarthritis': {
        'medications': [
            {
                'name': 'Celecoxib (Celebrex)',
                'dosage': '200mg',
                'frequency': 'Once or twice daily',
                'duration': 'Long-term',
                'timing': 'With food',
                'instructions': 'COX-2 inhibitor. Easier on stomach than other NSAIDs.'
            },
            {
                'name': 'Naproxen',
                'dosage': '500mg',
                'frequency': 'Twice daily',
                'duration': 'Long-term',
                'timing': 'After meals',
                'instructions': 'NSAID for pain and inflammation. Take with food.'
            },
            {
                'name': 'Glucosamine + Chondroitin',
                'dosage': '1500mg/1200mg',
                'frequency': 'Once daily',
                'duration': 'Ongoing',
                'timing': 'With meals',
                'instructions': 'Joint supplement. May take 2-3 months for effect.'
            },
            {
                'name': 'Tramadol',
                'dosage': '50mg',
                'frequency': 'Every 6 hours as needed',
                'duration': 'As needed',
                'timing': 'With or without food',
                'instructions': 'Pain reliever. May cause dizziness. Habit-forming potential.'
            }
        ]
    },
    'gout': {
        'medications': [
            {
                'name': 'Colchicine',
                'dosage': '0.6mg',
                'frequency': 'Twice daily during attack',
                'duration': '3-5 days',
                'timing': 'With or without food',
                'instructions': 'For acute gout. May cause diarrhea. Start at first sign of attack.'
            },
            {
                'name': 'Indomethacin',
                'dosage': '50mg',
                'frequency': 'Three times daily',
                'duration': '5-7 days',
                'timing': 'After meals',
                'instructions': 'NSAID for acute gout pain. Take with food.'
            },
            {
                'name': 'Allopurinol',
                'dosage': '100mg',
                'frequency': 'Once daily',
                'duration': 'Long-term prevention',
                'timing': 'After meals',
                'instructions': 'Prevents gout attacks. Start low, increase gradually. Drink plenty water.'
            },
            {
                'name': 'Febuxostat',
                'dosage': '40mg',
                'frequency': 'Once daily',
                'duration': 'Long-term',
                'timing': 'Any time',
                'instructions': 'Alternative to allopurinol. Lowers uric acid.'
            }
        ]
    },
    'constipation': {
        'medications': [
            {
                'name': 'Bisacodyl',
                'dosage': '5mg',
                'frequency': 'Once daily',
                'duration': '3-7 days',
                'timing': 'Bedtime',
                'instructions': 'Stimulant laxative. Works in 6-12 hours. Short-term use only.'
            },
            {
                'name': 'Polyethylene glycol (MiraLAX)',
                'dosage': '17g in 8oz water',
                'frequency': 'Once daily',
                'duration': 'As needed',
                'timing': 'Any time',
                'instructions': 'Osmotic laxative. Safe for long-term use. Takes 1-3 days.'
            },
            {
                'name': 'Psyllium husk (Metamucil)',
                'dosage': '1 tablespoon',
                'frequency': 'Twice daily',
                'duration': 'Ongoing',
                'timing': 'With meals',
                'instructions': 'Fiber supplement. Drink plenty of water. Prevents constipation.'
            },
            {
                'name': 'Docusate sodium',
                'dosage': '100mg',
                'frequency': 'Twice daily',
                'duration': '7 days',
                'timing': 'With water',
                'instructions': 'Stool softener. Gentle. Good for post-surgery or pregnancy.'
            }
        ]
    },
    'diarrhea': {
        'medications': [
            {
                'name': 'Loperamide (Imodium)',
                'dosage': '2mg',
                'frequency': 'After each loose stool',
                'duration': '2 days max',
                'timing': 'As needed (max 8mg/day)',
                'instructions': 'Anti-diarrheal. Stop if fever develops or blood in stool.'
            },
            {
                'name': 'Bismuth subsalicylate (Pepto-Bismol)',
                'dosage': '30ml',
                'frequency': 'Every 30-60 min as needed',
                'duration': '2 days',
                'timing': 'As needed (max 8 doses/day)',
                'instructions': 'For diarrhea and upset stomach. May darken tongue/stool.'
            },
            {
                'name': 'Rifaximin',
                'dosage': '200mg',
                'frequency': 'Three times daily',
                'duration': '3 days',
                'timing': 'With or without food',
                'instructions': 'Antibiotic for traveler\'s diarrhea. Non-absorbed.'
            }
        ]
    },
    'hemorrhoids': {
        'medications': [
            {
                'name': 'Hydrocortisone suppository',
                'dosage': '25mg',
                'frequency': 'Twice daily',
                'duration': '7 days',
                'timing': 'Morning and bedtime',
                'instructions': 'For internal hemorrhoids. Insert after bowel movement.'
            },
            {
                'name': 'Preparation H cream',
                'dosage': 'Apply to area',
                'frequency': '3-4 times daily',
                'duration': '7 days',
                'timing': 'After bowel movements',
                'instructions': 'For external hemorrhoids. Clean area first.'
            },
            {
                'name': 'Diosmin + Hesperidin',
                'dosage': '500mg',
                'frequency': 'Twice daily',
                'duration': '14-30 days',
                'timing': 'With meals',
                'instructions': 'Vein strengthener. Reduces hemorrhoid symptoms.'
            }
        ]
    },
    'peptic_ulcer': {
        'medications': [
            {
                'name': 'Omeprazole',
                'dosage': '40mg',
                'frequency': 'Once daily',
                'duration': '4-8 weeks',
                'timing': 'Before breakfast',
                'instructions': 'PPI for ulcer healing. Take on empty stomach.'
            },
            {
                'name': 'Clarithromycin',
                'dosage': '500mg',
                'frequency': 'Twice daily',
                'duration': '14 days',
                'timing': 'With meals',
                'instructions': 'Part of H. pylori triple therapy. Complete full course.'
            },
            {
                'name': 'Amoxicillin',
                'dosage': '1000mg',
                'frequency': 'Twice daily',
                'duration': '14 days',
                'timing': 'With meals',
                'instructions': 'Part of H. pylori triple therapy with PPI and clarithromycin.'
            },
            {
                'name': 'Sucralfate',
                'dosage': '1g',
                'frequency': 'Four times daily',
                'duration': '4-8 weeks',
                'timing': 'Before meals and bedtime',
                'instructions': 'Coats ulcer. Take 1 hour before meals on empty stomach.'
            }
        ]
    },
    'vertigo_dizziness': {
        'medications': [
            {
                'name': 'Betahistine',
                'dosage': '16mg',
                'frequency': 'Three times daily',
                'duration': '14-30 days',
                'timing': 'After meals',
                'instructions': 'For Meniere\'s disease and vertigo. May take weeks for effect.'
            },
            {
                'name': 'Meclizine (Antivert)',
                'dosage': '25mg',
                'frequency': 'Three times daily',
                'duration': '7-14 days',
                'timing': 'As needed',
                'instructions': 'For vertigo and motion sickness. May cause drowsiness.'
            },
            {
                'name': 'Dimenhydrinate (Dramamine)',
                'dosage': '50mg',
                'frequency': 'Every 4-6 hours',
                'duration': 'As needed',
                'timing': '30 min before travel',
                'instructions': 'For motion sickness. Causes drowsiness.'
            },
            {
                'name': 'Prochlorperazine',
                'dosage': '5mg',
                'frequency': 'Three times daily',
                'duration': '5-7 days',
                'timing': 'After meals',
                'instructions': 'For severe vertigo and nausea. May cause drowsiness.'
            }
        ]
    },
    'anemia_iron_deficiency': {
        'medications': [
            {
                'name': 'Ferrous sulfate',
                'dosage': '325mg',
                'frequency': 'Once or twice daily',
                'duration': '3-6 months',
                'timing': 'On empty stomach or with vitamin C',
                'instructions': 'Iron supplement. May cause constipation and dark stools. Avoid with dairy.'
            },
            {
                'name': 'Ferrous gluconate',
                'dosage': '325mg',
                'frequency': 'Twice daily',
                'duration': '3-6 months',
                'timing': 'Between meals',
                'instructions': 'Gentler iron alternative. Better tolerated than sulfate.'
            },
            {
                'name': 'Vitamin B12 (Cyanocobalamin)',
                'dosage': '1000mcg',
                'frequency': 'Once daily',
                'duration': '1-3 months',
                'timing': 'Any time',
                'instructions': 'For B12 deficiency anemia. Sublingual or oral.'
            },
            {
                'name': 'Folic acid',
                'dosage': '5mg',
                'frequency': 'Once daily',
                'duration': '4 months',
                'timing': 'Any time',
                'instructions': 'For folate deficiency anemia. Important in pregnancy.'
            }
        ]
    },
    'depression': {
        'medications': [
            {
                'name': 'Sertraline (Zoloft)',
                'dosage': '50mg',
                'frequency': 'Once daily',
                'duration': 'Long-term (6+ months)',
                'timing': 'Morning',
                'instructions': 'SSRI antidepressant. Takes 4-6 weeks for effect. Do not stop abruptly.'
            },
            {
                'name': 'Escitalopram (Lexapro)',
                'dosage': '10mg',
                'frequency': 'Once daily',
                'duration': 'Long-term',
                'timing': 'Morning or evening',
                'instructions': 'SSRI. Well-tolerated. Takes several weeks for full effect.'
            },
            {
                'name': 'Bupropion (Wellbutrin)',
                'dosage': '150mg',
                'frequency': 'Once or twice daily',
                'duration': 'Long-term',
                'timing': 'Morning',
                'instructions': 'NDRI antidepressant. Less sexual side effects. Avoid in seizure disorders.'
            },
            {
                'name': 'Mirtazapine',
                'dosage': '15mg',
                'frequency': 'Once daily',
                'duration': 'Long-term',
                'timing': 'Bedtime',
                'instructions': 'Helps with sleep and appetite. May cause weight gain.'
            }
        ]
    },
    'smoking_cessation': {
        'medications': [
            {
                'name': 'Varenicline (Chantix)',
                'dosage': '1mg',
                'frequency': 'Twice daily',
                'duration': '12 weeks',
                'timing': 'After meals',
                'instructions': 'Start 1 week before quit date. Most effective cessation aid.'
            },
            {
                'name': 'Bupropion SR (Zyban)',
                'dosage': '150mg',
                'frequency': 'Twice daily',
                'duration': '7-12 weeks',
                'timing': 'Morning and evening',
                'instructions': 'Start 1-2 weeks before quit date. Also treats depression.'
            },
            {
                'name': 'Nicotine patch',
                'dosage': '21mg',
                'frequency': 'Once daily',
                'duration': '8-10 weeks (tapering)',
                'timing': 'Apply in morning',
                'instructions': 'Apply to clean, dry, hairless skin. Rotate sites. Taper dose.'
            },
            {
                'name': 'Nicotine gum',
                'dosage': '2mg or 4mg',
                'frequency': 'Every 1-2 hours',
                'duration': '12 weeks',
                'timing': 'As needed for cravings',
                'instructions': 'Chew slowly until peppery, then park between cheek and gum.'
            }
        ]
    },
    'vitamin_deficiencies': {
        'medications': [
            {
                'name': 'Vitamin B Complex',
                'dosage': '1 tablet',
                'frequency': 'Once daily',
                'duration': '30-90 days',
                'timing': 'After breakfast',
                'instructions': 'For B vitamin deficiencies. May turn urine bright yellow.'
            },
            {
                'name': 'Vitamin D3',
                'dosage': '2000-5000 IU',
                'frequency': 'Once daily',
                'duration': 'Ongoing',
                'timing': 'With fatty meal',
                'instructions': 'For vitamin D deficiency. Fat-soluble. Check levels periodically.'
            },
            {
                'name': 'Omega-3 fish oil',
                'dosage': '1000mg',
                'frequency': 'Once or twice daily',
                'duration': 'Ongoing',
                'timing': 'With meals',
                'instructions': 'For heart and brain health. Choose quality brand to avoid fishy burps.'
            },
            {
                'name': 'Magnesium glycinate',
                'dosage': '400mg',
                'frequency': 'Once daily',
                'duration': 'Ongoing',
                'timing': 'Evening',
                'instructions': 'For magnesium deficiency. Helps with sleep, muscle cramps.'
            }
        ]
    },
    'menstrual_pain': {
        'medications': [
            {
                'name': 'Mefenamic acid (Ponstel)',
                'dosage': '500mg',
                'frequency': 'Three times daily',
                'duration': '2-3 days during period',
                'timing': 'After meals',
                'instructions': 'NSAID specifically for menstrual pain. Start at onset of period.'
            },
            {
                'name': 'Naproxen',
                'dosage': '500mg',
                'frequency': 'Twice daily',
                'duration': 'During period',
                'timing': 'After meals',
                'instructions': 'For dysmenorrhea. Take with food.'
            },
            {
                'name': 'Tranexamic acid',
                'dosage': '500mg',
                'frequency': 'Three times daily',
                'duration': 'During heavy flow days',
                'timing': 'With or without food',
                'instructions': 'Reduces heavy menstrual bleeding by 40-50%.'
            },
            {
                'name': 'Combined oral contraceptive',
                'dosage': '1 tablet',
                'frequency': 'Once daily',
                'duration': 'Ongoing',
                'timing': 'Same time daily',
                'instructions': 'Regulates periods, reduces pain and flow. Requires prescription.'
            }
        ]
    },
    'vaginal_yeast_infection': {
        'medications': [
            {
                'name': 'Fluconazole',
                'dosage': '150mg',
                'frequency': 'Single dose',
                'duration': '1 day',
                'timing': 'Any time',
                'instructions': 'Oral antifungal. Single dose usually sufficient. Repeat in 3 days if needed.'
            },
            {
                'name': 'Clotrimazole vaginal cream 1%',
                'dosage': '1 applicator',
                'frequency': 'Once daily at bedtime',
                'duration': '7 days',
                'timing': 'Bedtime',
                'instructions': 'Insert applicator deep into vagina. Use pad for discharge.'
            },
            {
                'name': 'Miconazole vaginal suppository',
                'dosage': '200mg',
                'frequency': 'Once daily at bedtime',
                'duration': '3 days',
                'timing': 'Bedtime',
                'instructions': 'Insert high into vagina. May use with external cream.'
            }
        ]
    },
    'erectile_dysfunction': {
        'medications': [
            {
                'name': 'Sildenafil (Viagra)',
                'dosage': '50mg',
                'frequency': 'As needed',
                'duration': 'As needed',
                'timing': '1 hour before activity',
                'instructions': 'PDE5 inhibitor. Avoid with nitrates. Lasts 4-6 hours.'
            },
            {
                'name': 'Tadalafil (Cialis)',
                'dosage': '10mg',
                'frequency': 'As needed or daily 5mg',
                'duration': 'As needed',
                'timing': '30 min before activity',
                'instructions': 'Lasts up to 36 hours. Daily low-dose option available.'
            },
            {
                'name': 'Vardenafil (Levitra)',
                'dosage': '10mg',
                'frequency': 'As needed',
                'duration': 'As needed',
                'timing': '1 hour before activity',
                'instructions': 'Similar to sildenafil. Avoid with nitrates.'
            }
        ]
    },
    'benign_prostatic_hyperplasia': {
        'medications': [
            {
                'name': 'Tamsulosin (Flomax)',
                'dosage': '0.4mg',
                'frequency': 'Once daily',
                'duration': 'Long-term',
                'timing': '30 min after same meal daily',
                'instructions': 'Alpha blocker. Improves urinary flow. May cause dizziness.'
            },
            {
                'name': 'Finasteride (Proscar)',
                'dosage': '5mg',
                'frequency': 'Once daily',
                'duration': 'Long-term',
                'timing': 'Any time',
                'instructions': '5-alpha reductase inhibitor. Shrinks prostate. Takes 3-6 months for effect.'
            },
            {
                'name': 'Dutasteride (Avodart)',
                'dosage': '0.5mg',
                'frequency': 'Once daily',
                'duration': 'Long-term',
                'timing': 'Any time',
                'instructions': 'Similar to finasteride but more potent. Lowers PSA levels.'
            }
        ]
    },
    'neuropathic_pain': {
        'medications': [
            {
                'name': 'Gabapentin (Neurontin)',
                'dosage': '300mg',
                'frequency': 'Three times daily',
                'duration': 'Long-term',
                'timing': 'Every 8 hours',
                'instructions': 'For nerve pain. Start low, increase gradually. May cause dizziness.'
            },
            {
                'name': 'Pregabalin (Lyrica)',
                'dosage': '75mg',
                'frequency': 'Twice daily',
                'duration': 'Long-term',
                'timing': 'Morning and evening',
                'instructions': 'For neuropathic pain. More potent than gabapentin. May cause weight gain.'
            },
            {
                'name': 'Duloxetine (Cymbalta)',
                'dosage': '60mg',
                'frequency': 'Once daily',
                'duration': 'Long-term',
                'timing': 'Morning',
                'instructions': 'SNRI for nerve pain and depression. Swallow whole, do not crush.'
            },
            {
                'name': 'Amitriptyline',
                'dosage': '25mg',
                'frequency': 'Once daily',
                'duration': 'Long-term',
                'timing': 'Bedtime',
                'instructions': 'Tricyclic for nerve pain. Helps sleep. Dry mouth common. Start low.'
            }
        ]
    }
}

# Common medicines not always listed in recommendations (for interaction checks)
COMMON_MED_NAMES = [
    'aspirin', 'warfarin', 'clopidogrel', 'naproxen', 'diclofenac',
    'sertraline', 'fluoxetine', 'paroxetine', 'citalopram', 'escitalopram',
    'linezolid', 'phenelzine', 'tranylcypromine'
]

# Common misspellings -> canonical name
COMMON_MED_MISSPELLINGS = {
    'paracetomol': 'paracetamol',
    'paracetmol': 'paracetamol',
    'paracetemol': 'paracetamol',
    'paracetomol': 'paracetamol',
    'acetominophen': 'paracetamol',
    'acetaminophen': 'paracetamol',
    'ibuprofene': 'ibuprofen',
    'ibuprofin': 'ibuprofen',
    'amoxycillin': 'amoxicillin',
    'azithromicin': 'azithromycin',
    'diclofinac': 'diclofenac'
}

# Basic medication interaction rules (non-exhaustive)
MEDICATION_INTERACTIONS = [
    {
        'group_a': ['ibuprofen', 'naproxen', 'diclofenac'],
        'group_b': ['ibuprofen', 'naproxen', 'diclofenac'],
        'severity': 'medium',
        'message': 'Avoid combining NSAIDs (ibuprofen/naproxen/diclofenac); it raises stomach and bleeding risk.'
    },
    {
        'group_a': ['ibuprofen', 'naproxen', 'diclofenac', 'aspirin'],
        'group_b': ['warfarin', 'clopidogrel'],
        'severity': 'high',
        'message': 'NSAIDs or aspirin with blood thinners can significantly increase bleeding risk.'
    },
    {
        'group_a': ['dextromethorphan'],
        'group_b': ['sertraline', 'fluoxetine', 'paroxetine', 'citalopram', 'escitalopram', 'phenelzine', 'tranylcypromine', 'linezolid'],
        'severity': 'high',
        'message': 'Dextromethorphan with SSRIs/MAOIs can raise serotonin syndrome risk.'
    },
    {
        'group_a': ['aspirin'],
        'group_b': ['ibuprofen'],
        'severity': 'low',
        'message': 'Ibuprofen can reduce aspirin’s antiplatelet effect if taken together.'
    }
]

# Basic safety guidance for common OTC meds (non-exhaustive)
MEDICATION_SAFETY_INFO = {
    'paracetamol': {
        'safe_label': 'Likely OK for most adults',
        'max_doses_per_day': 3,
        'note': 'Avoid if you have liver disease or heavy alcohol use.'
    },
    'ibuprofen': {
        'safe_label': 'Likely OK for most adults',
        'max_doses_per_day': 3,
        'note': 'Avoid if you have ulcers, kidney disease, or are on blood thinners.'
    },
    'aspirin': {
        'safe_label': 'Caution',
        'max_doses_per_day': 3,
        'note': 'Avoid if under 18 or on blood thinners; can irritate stomach.'
    },
    'dextromethorphan': {
        'safe_label': 'Likely OK for most adults',
        'max_doses_per_day': 4,
        'note': 'Avoid with SSRIs/MAOIs; can cause drowsiness.'
    },
    'guaifenesin': {
        'safe_label': 'Likely OK for most adults',
        'max_doses_per_day': 4,
        'note': 'Drink plenty of water to help it work.'
    },
    'loperamide': {
        'safe_label': 'Caution',
        'max_doses_per_day': 4,
        'note': 'Stop if fever or blood in stool; avoid in severe abdominal pain.'
    },
    'cetirizine': {
        'safe_label': 'Likely OK for most adults',
        'max_doses_per_day': 1,
        'note': 'May cause drowsiness.'
    },
    'famotidine': {
        'safe_label': 'Likely OK for most adults',
        'max_doses_per_day': 2,
        'note': 'Use short‑term unless advised by a clinician.'
    },
    'omeprazole': {
        'safe_label': 'Likely OK for most adults',
        'max_doses_per_day': 1,
        'note': 'Short‑term use unless advised by a clinician.'
    }
}

def get_symptom_category(symptom):
    """Determine which category a symptom belongs to"""
    symptom_lower = symptom.lower()
    for category, symptoms in SYMPTOM_CATEGORIES.items():
        for s in symptoms:
            if s in symptom_lower:
                return category
    return 'general'

def check_emergency(message):
    """Check if message contains emergency keywords"""
    message_lower = message.lower()
    
    for keyword in EMERGENCY_KEYWORDS['critical']:
        if keyword in message_lower:
            return 'critical'
    
    for keyword in EMERGENCY_KEYWORDS['urgent']:
        if keyword in message_lower:
            return 'urgent'
    
    return None
