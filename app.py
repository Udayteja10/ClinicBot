"""
Flask Backend Server for Health Chatbot
Handles API endpoints and manages chatbot sessions
"""

import os
import sqlite3
import json
import re
from datetime import datetime

from flask import Flask, request, jsonify, session, send_from_directory, g
from flask_cors import CORS
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps, ImageFilter
import pytesseract
import numpy as np

try:
    import easyocr
    EASY_OCR_AVAILABLE = True
except Exception:
    EASY_OCR_AVAILABLE = False

from chatbot_engine import ChatbotEngine
from medical_knowledge import (
    MEDICATION_RECOMMENDATIONS, COMMON_MED_NAMES, MEDICATION_INTERACTIONS, COMMON_MED_MISSPELLINGS,
    MEDICATION_SAFETY_INFO
)
import config

app = Flask(__name__, static_folder='.')
app.config['SECRET_KEY'] = config.SECRET_KEY
CORS(app)

# Store chatbot instances per session
chatbot_sessions = {}
APP_BOOT_TOKEN = str(uuid.uuid4())

# Database setup for authenticated storage
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'user_store.db')
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'data', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

RX_KEYWORDS = [
    'antibiotic', 'oseltamivir', 'amoxicillin', 'azithromycin', 'doxycycline',
    'ciprofloxacin', 'metronidazole', 'fluconazole', 'pred', 'dexamethasone',
    'sumatriptan', 'rizatriptan', 'ondansetron', 'metoclopramide',
    'domperidone', 'alprazolam', 'propranolol', 'rifaximin'
]

OTC_HINTS = {
    'paracetamol': ['fever', 'pain', 'headache', 'body ache', 'muscle pain'],
    'ibuprofen': ['fever', 'pain', 'headache', 'body ache', 'muscle pain'],
    'cetirizine': ['runny nose', 'sneezing', 'allergy', 'itching', 'hives', 'rash'],
    'loratadine': ['runny nose', 'sneezing', 'allergy', 'itching', 'hives', 'rash'],
    'antacid': ['heartburn', 'indigestion', 'nausea', 'stomach pain', 'acid'],
    'calcium carbonate': ['heartburn', 'indigestion', 'nausea', 'stomach pain', 'acid'],
    'bismuth subsalicylate': ['nausea', 'upset stomach', 'diarrhea'],
    'loperamide': ['diarrhea'],
    'oral rehydration solution': ['diarrhea', 'vomiting', 'dehydration'],
    'ors': ['diarrhea', 'vomiting', 'dehydration'],
    'famotidine': ['heartburn', 'acid reflux'],
    'omeprazole': ['heartburn', 'acid reflux'],
    'pantoprazole': ['heartburn', 'acid reflux']
}


def _normalize_text(text: str) -> str:
    lowered = text.lower()
    cleaned = re.sub(r'[^a-z0-9\s]+', ' ', lowered)
    return re.sub(r'\s+', ' ', cleaned).strip()


def _build_med_alias_map():
    alias_map = {}
    for condition in MEDICATION_RECOMMENDATIONS.values():
        for med in condition.get('medications', []):
            name = med.get('name', '')
            if not name:
                continue
            base = name.split('(')[0].strip()
            if base:
                alias_map[_normalize_text(base)] = base.lower()

            # Pull aliases from parentheses (brands) and slash-separated names
            paren_match = re.search(r'\(([^)]+)\)', name)
            aliases = []
            if paren_match:
                aliases.extend(re.split(r'[\/,]', paren_match.group(1)))
            aliases.extend(name.split('/'))

            for alias in aliases:
                alias_clean = re.sub(r'[^a-zA-Z\s]+', ' ', alias).strip()
                alias_clean = ' '.join(alias_clean.split())
                if len(alias_clean) >= 3:
                    alias_map[_normalize_text(alias_clean)] = (base or alias_clean).lower()

    for med in COMMON_MED_NAMES:
        alias_map[_normalize_text(med)] = med.lower()

    for misspelling, canonical in COMMON_MED_MISSPELLINGS.items():
        alias_map[_normalize_text(misspelling)] = canonical.lower()

    return alias_map


MED_ALIAS_MAP = _build_med_alias_map()
_EASY_READER = None


def _get_easy_reader():
    global _EASY_READER
    if not EASY_OCR_AVAILABLE:
        return None
    if _EASY_READER is None:
        _EASY_READER = easyocr.Reader(['en'], gpu=False)
    return _EASY_READER


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


def _ensure_session_fresh():
    boot_token = session.get('boot_token')
    if boot_token and boot_token != APP_BOOT_TOKEN:
        session.pop('user_id', None)
        session.pop('username', None)
        session.pop('boot_token', None)


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def _reset_users_table_if_needed(cursor):
    cursor.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in cursor.fetchall()]
    if cols and 'username' not in cols:
        cursor.execute("DROP TABLE IF EXISTS users")


def init_db():
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()
    _reset_users_table_if_needed(cursor)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS carepacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS timeline_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            severity INTEGER NOT NULL,
            note TEXT,
            created_at TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT
        )
        """
    )
    db.commit()
    db.close()


init_db()

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('.', path)


@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip().lower()
    password = data.get('password') or ''

    if len(username) < 3 or len(password) < 6:
        return jsonify({'error': 'Username (>=3) and password (>=6) required'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        return jsonify({'error': 'Username already exists'}), 409

    password_hash = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
        (username, password_hash, datetime.utcnow().isoformat())
    )
    db.commit()

    user_id = cursor.lastrowid
    session['user_id'] = user_id
    session['username'] = username
    session['boot_token'] = APP_BOOT_TOKEN

    return jsonify({'message': 'Registered', 'user': {'username': username}})


@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip().lower()
    password = data.get('password') or ''

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    if not row or not check_password_hash(row['password_hash'], password):
        return jsonify({'error': 'Invalid username or password'}), 401

    session['user_id'] = row['id']
    session['username'] = username
    session['boot_token'] = APP_BOOT_TOKEN

    return jsonify({'message': 'Logged in', 'user': {'username': username}})


@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('boot_token', None)
    return jsonify({'message': 'Logged out'})


@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Return authentication status"""
    _ensure_session_fresh()
    user_id = session.get('user_id')
    username = session.get('username')
    return jsonify({
        'logged_in': user_id is not None,
        'auth_configured': True,
        'user': {'username': username} if username else None
    })


def get_current_user_id():
    _ensure_session_fresh()
    return session.get('user_id')


def log_chat_message(user_id, session_id, role, message):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO chat_history (user_id, session_id, role, message, created_at) VALUES (?, ?, ?, ?, ?)""",
            (user_id, session_id, role, message, datetime.utcnow().isoformat())
        )
        db.commit()
        return True
    except sqlite3.Error as exc:
        print(f"Chat history log failed: {exc}")
        return False


@app.route('/api/carepack/save', methods=['POST'])
def save_carepack():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    data = request.get_json() or {}
    content = data.get('content')
    if not content:
        return jsonify({'error': 'Content required'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO carepacks (user_id, content, created_at) VALUES (?, ?, ?)""",
        (user_id, content, datetime.utcnow().isoformat())
    )
    db.commit()

    return jsonify({'message': 'CarePack saved'})


@app.route('/api/carepack/list', methods=['GET'])
def list_carepacks():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """SELECT id, content, created_at FROM carepacks WHERE user_id = ? ORDER BY created_at DESC""",
        (user_id,)
    )
    rows = cursor.fetchall()
    carepacks = [
        {
            'id': row['id'],
            'content': row['content'],
            'created_at': row['created_at']
        }
        for row in rows
    ]
    return jsonify({'carepacks': carepacks})


@app.route('/api/carepack/delete/<int:carepack_id>', methods=['DELETE'])
def delete_carepack(carepack_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """DELETE FROM carepacks WHERE id = ? AND user_id = ?""",
        (carepack_id, user_id)
    )
    db.commit()
    return jsonify({'message': 'CarePack deleted'})


@app.route('/api/history', methods=['GET'])
def list_history():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT session_id,
               MIN(created_at) AS started_at,
               MAX(created_at) AS last_at,
               COUNT(*) AS message_count
        FROM chat_history
        WHERE user_id = ?
        GROUP BY session_id
        ORDER BY last_at DESC
        LIMIT 20
        """,
        (user_id,)
    )
    rows = cursor.fetchall()
    sessions = [
        {
            'session_id': row['session_id'],
            'started_at': row['started_at'],
            'last_at': row['last_at'],
            'message_count': row['message_count']
        }
        for row in rows
    ]
    return jsonify({'sessions': sessions})


@app.route('/api/history/<session_id>', methods=['GET'])
def get_history_session(session_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT role, message, created_at
        FROM chat_history
        WHERE user_id = ? AND session_id = ?
        ORDER BY created_at ASC
        """,
        (user_id, session_id)
    )
    rows = cursor.fetchall()
    messages = [
        {
            'role': row['role'],
            'message': row['message'],
            'created_at': row['created_at']
        }
        for row in rows
    ]
    return jsonify({'messages': messages})


@app.route('/api/history/delete/<session_id>', methods=['DELETE'])
def delete_history_session(session_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """DELETE FROM chat_history WHERE user_id = ? AND session_id = ?""",
        (user_id, session_id)
    )
    db.commit()
    return jsonify({'message': 'History session deleted'})


def extract_meds_from_text(text):
    meds = set()
    normalized_text = _normalize_text(text)
    for alias, canonical in MED_ALIAS_MAP.items():
        if not alias:
            continue
        if re.search(rf'\b{re.escape(alias)}\b', normalized_text):
            meds.add(canonical.strip().lower())
    for med in COMMON_MED_NAMES:
        med_norm = _normalize_text(med)
        if med_norm and re.search(rf'\b{re.escape(med_norm)}\b', normalized_text):
            meds.add(med.lower())
    return sorted(meds)


def _preprocess_ocr_image(image):
    gray = image.convert('L')
    gray = ImageOps.autocontrast(gray)
    gray = gray.filter(ImageFilter.SHARPEN)
    # Threshold to improve contrast for handwriting
    bw = gray.point(lambda x: 0 if x < 140 else 255, '1')
    return bw


def _ocr_with_easyocr(image):
    reader = _get_easy_reader()
    if not reader:
        return ''
    try:
        results = reader.readtext(np.array(image), detail=0, paragraph=True)
        if not results:
            return ''
        return "\n".join(results).strip()
    except Exception:
        return ''


def _ocr_with_tesseract(image):
    raw_text = pytesseract.image_to_string(image, config='--oem 1 --psm 6')
    enhanced_text = pytesseract.image_to_string(_preprocess_ocr_image(image), config='--oem 1 --psm 6')
    return enhanced_text if len(enhanced_text) > len(raw_text) else raw_text


def analyze_prescription_safety(meds, symptoms):
    symptom_text = ' '.join(symptoms or []).lower()
    results = []

    for med in meds:
        med_lower = med.lower()
        status = 'unknown'
        label = 'Unclear'
        reason = 'Not enough context to evaluate.'

        if any(keyword in med_lower for keyword in RX_KEYWORDS):
            status = 'needs_clinician'
            label = 'Needs clinician'
            reason = 'Prescription-only medication. Do not start or change dosing without a clinician.'
        else:
            matched_hint = None
            for key, hint_symptoms in OTC_HINTS.items():
                if key in med_lower:
                    matched_hint = hint_symptoms
                    break

            if matched_hint:
                if any(symptom in symptom_text for symptom in matched_hint):
                    status = 'otc_match'
                    label = 'Likely OTC match'
                    reason = 'Commonly used for these symptoms, but safety depends on allergies and conditions.'
                else:
                    status = 'otc_unclear'
                    label = 'OTC but unclear fit'
                    reason = 'Common OTC medication, but it doesn’t clearly match the symptoms provided.'
            else:
                status = 'unknown'
                label = 'Unclear'
                reason = 'Medication not recognized clearly from OCR; verify with a clinician or pharmacist.'

        results.append({
            'name': med.title(),
            'status': status,
            'label': label,
            'reason': reason
        })

    return results


def check_interactions(meds):
    meds_set = set([m.lower() for m in meds])
    warnings = []
    for rule in MEDICATION_INTERACTIONS:
        group_a = set(rule.get('group_a', []))
        group_b = set(rule.get('group_b', []))
        if not group_a or not group_b:
            continue
        if group_a == group_b:
            matched = meds_set.intersection(group_a)
            if len(matched) >= 2:
                warnings.append({
                    'severity': rule.get('severity', 'medium'),
                    'message': rule.get('message', ''),
                    'meds': sorted(matched)
                })
        else:
            matched_a = meds_set.intersection(group_a)
            matched_b = meds_set.intersection(group_b)
            if matched_a and matched_b:
                warnings.append({
                    'severity': rule.get('severity', 'medium'),
                    'message': rule.get('message', ''),
                    'meds': sorted(matched_a.union(matched_b))
                })
    return warnings


def get_med_safety_info(med, raw_text):
    med_lower = med.lower()
    info = MEDICATION_SAFETY_INFO.get(med_lower)

    safe_label = 'Unclear'
    max_doses = None
    note = 'Check the label and your health conditions.'

    if info:
        safe_label = info.get('safe_label', safe_label)
        max_doses = info.get('max_doses_per_day', max_doses)
        note = info.get('note', note)

    # Special handling for paracetamol brand strengths (e.g., Dolo 650)
    if 'paracetamol' in med_lower:
        if re.search(r'\b650\b', raw_text.lower()):
            max_doses = 3
        elif re.search(r'\b500\b', raw_text.lower()):
            max_doses = 4

    return {
        'safe_label': safe_label,
        'max_doses_per_day': max_doses,
        'note': note
    }


@app.route('/api/prescription/upload', methods=['POST'])
def upload_prescription():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_DIR, filename)
    file.save(save_path)

    try:
        image = Image.open(save_path)
        text_easy = _ocr_with_easyocr(image)
        text_tess = _ocr_with_tesseract(image)
        text = text_easy if len(text_easy) > len(text_tess) else text_tess
    except Exception as e:
        return jsonify({'error': f'OCR failed: {str(e)}'}), 500

    meds = extract_meds_from_text(text)
    meds_display = [m.title() for m in meds]
    symptoms_raw = request.form.get('symptoms') or '[]'
    try:
        symptoms = json.loads(symptoms_raw)
    except json.JSONDecodeError:
        symptoms = []
    safety = analyze_prescription_safety(meds, symptoms)

    return jsonify({
        'text': text,
        'medications_detected': meds_display,
        'safety': safety,
        'disclaimer': 'OCR text only. Handwriting recognition is best effort. Do not change dosing without a clinician.'
    })


@app.route('/api/medication/check', methods=['POST'])
def medication_check():
    data = request.get_json() or {}
    text = data.get('text') or ''
    meds = extract_meds_from_text(text)
    interactions = check_interactions(meds)
    safety = [
        {
            'name': m.title(),
            **get_med_safety_info(m, text)
        }
        for m in meds
    ]
    return jsonify({
        'medications_detected': [m.title() for m in meds],
        'interactions': interactions,
        'safety': safety,
        'disclaimer': 'This is a basic interaction check. Always confirm with a clinician or pharmacist.'
    })
@app.route('/api/timeline/add', methods=['POST'])
def add_timeline_entry():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    data = request.get_json() or {}
    severity = data.get('severity')
    note = data.get('note', '')
    created_at = data.get('timestamp') or datetime.utcnow().isoformat()

    if severity is None:
        return jsonify({'error': 'Severity required'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO timeline_entries (user_id, severity, note, created_at) VALUES (?, ?, ?, ?)""",
        (user_id, int(severity), note, created_at)
    )
    db.commit()

    return jsonify({'message': 'Timeline entry saved'})


@app.route('/api/timeline/clear', methods=['POST'])
def clear_timeline():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """DELETE FROM timeline_entries WHERE user_id = ?""",
        (user_id,)
    )
    db.commit()
    return jsonify({'message': 'Timeline cleared'})

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint
    Expects: {"message": "user message", "session_id": "optional session id"}
    Returns: {"response": "bot response", "session_id": "session id", "emergency": {...}}
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message']
        session_id = data.get('session_id')
        
        # Create or retrieve chatbot instance
        if not session_id or session_id not in chatbot_sessions:
            session_id = str(uuid.uuid4())
            chatbot_sessions[session_id] = ChatbotEngine()
        
        chatbot = chatbot_sessions[session_id]

        user_id = get_current_user_id()
        if user_id:
            log_chat_message(user_id, session_id, 'user', user_message)
        
        # Process message
        bot_response, emergency_info = chatbot.process_message(user_message)

        if user_id:
            log_chat_message(user_id, session_id, 'bot', bot_response)
        
        # Get current state
        state = chatbot.get_state()
        
        return jsonify({
            'response': bot_response,
            'session_id': session_id,
            'emergency': emergency_info,
            'state': state
        })
    
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': f'Chat error: {str(e)}'}), 500

@app.route('/api/reset', methods=['POST'])
def reset():
    """
    Reset conversation
    Expects: {"session_id": "session id"}
    Returns: {"message": "success", "session_id": "new session id"}
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        # Remove old session if exists
        if session_id and session_id in chatbot_sessions:
            del chatbot_sessions[session_id]
        
        # Create new session
        new_session_id = str(uuid.uuid4())
        chatbot_sessions[new_session_id] = ChatbotEngine()
        
        return jsonify({
            'message': 'Conversation reset successfully',
            'session_id': new_session_id
        })
    
    except Exception as e:
        print(f"Error in reset endpoint: {str(e)}")
        return jsonify({'error': 'An error occurred resetting the conversation'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'active_sessions': len(chatbot_sessions)
    })

if __name__ == '__main__':
    print("="*60)
    print("🏥 Health Chatbot Server Starting...")
    print("="*60)
    print(f"Server running at: http://localhost:{config.SERVER_PORT}")
    print("Press Ctrl+C to stop the server")
    print("="*60)
    
    app.run(
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
        debug=config.DEBUG_MODE
    )
