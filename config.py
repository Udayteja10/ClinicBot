"""
Configuration settings for the Health Chatbot application
"""

# Flask server settings
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5001
DEBUG_MODE = True

# Session settings
SECRET_KEY = 'health-chatbot-secret-key-change-in-production'
SESSION_TYPE = 'filesystem'

# Emergency contact information
EMERGENCY_CONTACTS = {
    'emergency_number': '911',
    'poison_control': '1-800-222-1222',
    'suicide_prevention': '988'
}

# Feature flags
ENABLE_EMERGENCY_DETECTION = True
ENABLE_RISK_ASSESSMENT = True
MAX_FOLLOWUP_QUESTIONS = 3

# Medical disclaimer
MEDICAL_DISCLAIMER = """
This chatbot is designed for educational and informational purposes only. 
It does not provide medical advice, diagnosis, or treatment. 
Always seek the advice of your physician or other qualified health provider 
with any questions you may have regarding a medical condition.
"""
