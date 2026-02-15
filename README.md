Medical Symptom Analyzer
An educational health chatbot that combines machine learning with medical rules to analyze symptoms and suggest possible conditions.
This is not a diagnostic tool and is for research and learning purposes only.
DISCLAIMER: This is not medical advice. Always consult a healthcare professional. In emergencies, call 911 or your local emergency number.
Performance
98.6% accuracy on synthetic test data (585 examples)
84.6% accuracy on 13 realistic clinical test cases (including edge cases like minimal or ambiguous symptoms)
Supports 8 conditions: Flu, Common Cold, Migraine, Gastroenteritis, Allergic Reaction, Respiratory Infection, Dehydration, Thyroid Disorder
Real-time inference: under 7ms for first prediction
The gap between synthetic and clinical accuracy reflects the challenge of real-world symptom variability — a key reason this remains an educational prototype.
Quick Start
Install dependencies:
pip install -r requirements.txt
Run the app:
python app.py
Open in your browser: http://localhost:5001
Example conversation:
User: "Hi"
User: "25, male"
User: "I have fever, cough, and body ache"
Validate Results
Run the clinical test suite:
python test_ml_integration.py
Expected output: 11 out of 13 correct predictions (84.6% accuracy)
To retrain the model:
python generate_training_data.py
python train_model.py
Tech Stack
Backend: Python, Flask
ML: XGBoost, TF-IDF, scikit-learn
Frontend: HTML, CSS, JavaScript
Training data: 3,900 synthetically generated examples
Project Structure
Medical-Chatbot/
├── app.py # Web server
├── symptom_analyzer.py # Hybrid ML + rule engine
├── medical_knowledge.py # Disease/symptom rules
├── safety_layer.py # Emergency detection
├── data/
│ └── training_data.csv
├── models/ # Saved ML models
└── index.html # Chat UI
License
For educational use only. Not FDA-approved. Not intended for clinical or medical use.
