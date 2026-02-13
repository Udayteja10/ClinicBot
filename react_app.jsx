const { useEffect, useRef, useState } = React;

const API_BASE_URL = window.location.origin;
const AUTH_SESSION_KEY = 'healthchat_auth_session';

const QUICK_REPLIES = {
  greeting: [
    { label: 'Hi', value: 'hi' },
    { label: 'Hello', value: 'hello' }
  ],
  collecting_info_gender: [
    { label: 'Male', value: 'male' },
    { label: 'Female', value: 'female' },
    { label: 'Other', value: 'other' }
  ],
  collecting_info_age: [
    { label: 'Under 18', value: '16' },
    { label: '18-29', value: '22' },
    { label: '30-49', value: '35' },
    { label: '50+', value: '55' }
  ],
  symptoms: [
    { label: 'Fever', value: 'fever' },
    { label: 'Cough', value: 'cough' },
    { label: 'Headache', value: 'headache' },
    { label: 'Sore throat', value: 'sore throat' },
    { label: 'Nausea', value: 'nausea' },
    { label: 'Body ache', value: 'body ache' }
  ],
  followup: [
    { label: "Didn't measure", value: "didn't measure" },
    { label: 'Not sure', value: 'not sure' },
    { label: 'No', value: 'no' },
    { label: 'Yes', value: 'yes' }
  ],
  complete: [
    { label: 'Relief Plan', value: 'plan' },
    { label: 'Doctor Summary', value: 'summary' },
    { label: 'Start Over', value: 'restart' }
  ]
};

function formatMessageText(text) {
  let formatted = text;
  formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  formatted = formatted.replace(/^([•📋🔍⚕️💡⏰🚨📞🏥👤📝])\s*(.+)$/gm, '<li>$2</li>');
  formatted = formatted.replace(/(<li>.*<\/li>\s*)+/g, '<ul>$&</ul>');
  formatted = formatted.replace(/\n\n/g, '</p><p>');
  formatted = '<p>' + formatted + '</p>';
  formatted = formatted.replace(/<p>\s*<\/p>/g, '');
  formatted = formatted.replace(/<p>\s*<ul>/g, '<ul>');
  formatted = formatted.replace(/<\/ul>\s*<\/p>/g, '</ul>');
  return formatted;
}

function getCurrentTime() {
  const now = new Date();
  return now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function ChatApp() {
  const [messages, setMessages] = useState([
    {
      role: 'bot',
      text: `Hey! 👋 I'm your health assistant.\n\nJust chat with me naturally about your symptoms, and I'll help you understand what's going on.\n\nType "hi" to start. You can also use quick replies when they appear.`,
      time: getCurrentTime()
    }
  ]);
  const [sessionId, setSessionId] = useState(null);
  const sessionRef = useRef(null);
  const [isWaiting, setIsWaiting] = useState(false);
  const [input, setInput] = useState('');
  const [state, setState] = useState({ stage: 'greeting', age: null, gender: null });
  const [carePack, setCarePack] = useState({ content: '', ready: false });
  const [authStatus, setAuthStatus] = useState({ logged_in: false, auth_configured: false, user: null });
  const [showAuth, setShowAuth] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [authUsername, setAuthUsername] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authError, setAuthError] = useState('');
  const [authLoading, setAuthLoading] = useState(false);
  const [historySessions, setHistorySessions] = useState([]);
  const [carepackList, setCarepackList] = useState([]);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [historyMessages, setHistoryMessages] = useState([]);
  const [carepackOpen, setCarepackOpen] = useState(false);
  const [carepackView, setCarepackView] = useState('');
  const [prescriptionText, setPrescriptionText] = useState('');
  const [prescriptionMeds, setPrescriptionMeds] = useState([]);
  const [prescriptionSafety, setPrescriptionSafety] = useState([]);
  const [prescriptionError, setPrescriptionError] = useState('');
  const [prescriptionLoading, setPrescriptionLoading] = useState(false);
  const [medCheckInput, setMedCheckInput] = useState('');
  const [medCheckResult, setMedCheckResult] = useState([]);
  const [medCheckInteractions, setMedCheckInteractions] = useState([]);
  const [medCheckSafety, setMedCheckSafety] = useState([]);
  const [medCheckError, setMedCheckError] = useState('');
  const [medCheckLoading, setMedCheckLoading] = useState(false);
  const [timelineOpen, setTimelineOpen] = useState(false);
  const [assessment, setAssessment] = useState(null);
  const [timeline, setTimeline] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('symptom_timeline') || '[]');
    } catch (e) {
      return [];
    }
  });
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('theme');
    if (saved) return saved;
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  });

  const chatRef = useRef(null);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages, isWaiting]);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('theme', theme);
  }, [theme]);

  useEffect(() => {
    const handleMove = (event) => {
      const x = (event.clientX / window.innerWidth - 0.5) * 40;
      const y = (event.clientY / window.innerHeight - 0.5) * 40;
      document.documentElement.style.setProperty('--bg-x', `${x}px`);
      document.documentElement.style.setProperty('--bg-y', `${y}px`);
    };
    window.addEventListener('mousemove', handleMove);
    return () => window.removeEventListener('mousemove', handleMove);
  }, []);

  // Do not persist session ids across reloads to avoid stale sessions

  useEffect(() => {
    localStorage.setItem('symptom_timeline', JSON.stringify(timeline.slice(0, 20)));
  }, [timeline]);

  const refreshAuthStatus = () => {
    fetch('/api/auth/status')
      .then((res) => (res.ok ? res.json() : { logged_in: false, auth_configured: false, user: null }))
      .then((data) => setAuthStatus(data))
      .catch(() => setAuthStatus({ logged_in: false, auth_configured: false, user: null }));
  };

  useEffect(() => {
    const sessionActive = sessionStorage.getItem(AUTH_SESSION_KEY);
    if (!sessionActive) {
      fetch('/api/auth/logout', { method: 'POST' })
        .finally(() => refreshAuthStatus());
    } else {
      refreshAuthStatus();
    }
  }, []);

  const refreshHistoryData = () => {
    if (!authStatus.logged_in) {
      setHistorySessions([]);
      setCarepackList([]);
      return;
    }
    fetch('/api/history')
      .then((res) => (res.ok ? res.json() : { sessions: [] }))
      .then((data) => setHistorySessions(data.sessions || []));
    fetch('/api/carepack/list')
      .then((res) => (res.ok ? res.json() : { carepacks: [] }))
      .then((data) => setCarepackList(data.carepacks || []));
  };

  useEffect(() => {
    refreshHistoryData();
  }, [authStatus.logged_in]);

  const quickReplies = (() => {
    if (!state || !state.stage) return [];
    if (state.stage === 'greeting') return QUICK_REPLIES.greeting;
    if (state.stage === 'collecting_info') {
      if (!state.gender) return QUICK_REPLIES.collecting_info_gender;
      if (!state.age) return QUICK_REPLIES.collecting_info_age;
    }
    if (state.stage === 'symptoms') return QUICK_REPLIES.symptoms;
    if (state.stage === 'followup') return QUICK_REPLIES.followup;
    if (state.stage === 'complete') return QUICK_REPLIES.complete;
    return [];
  })();

  const sendMessage = async (overrideMessage) => {
    const message = (overrideMessage ?? input).trim();
    if (!message || isWaiting) return;

    setMessages((prev) => [...prev, { role: 'user', text: message, time: getCurrentTime() }]);
    setInput('');
    setIsWaiting(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, session_id: sessionRef.current || sessionId })
      });

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.error || 'Failed to get response');
      }
      setSessionId(data.session_id);
      sessionRef.current = data.session_id;
      setState(data.state || state);
      setAssessment(data.state?.assessment || null);
      setMessages((prev) => [...prev, { role: 'bot', text: data.response, time: getCurrentTime() }]);

      if (data.state && data.state.stage === 'complete') {
        setCarePack({ content: data.response, ready: true });
      }
      if (authStatus.logged_in) {
        refreshHistoryData();
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          text: "I couldn't reach the server. Please check that it is running and try again.",
          time: getCurrentTime()
        }
      ]);
    } finally {
      setIsWaiting(false);
    }
  };

  const resetConversation = async () => {
    if (!window.confirm('Start a new consultation?')) return;
    setMessages([
      {
        role: 'bot',
        text: "Welcome back! I'm ready to help with a new consultation.\n\nPlease type 'hello' or 'hi' to begin.",
        time: getCurrentTime()
      }
    ]);
    setState({ stage: 'greeting', age: null, gender: null });
    setCarePack({ content: '', ready: false });
    setAssessment(null);
    setSessionId(null);
    sessionRef.current = null;
    try {
      const response = await fetch(`${API_BASE_URL}/api/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });
      if (!response.ok) throw new Error('Reset failed');
      const data = await response.json();
      setSessionId(data.session_id);
      sessionRef.current = data.session_id;
    } catch (err) {
      console.warn('Failed to reset conversation, continuing with new local session.');
    } finally {
      if (authStatus.logged_in) {
        refreshHistoryData();
      }
    }
  };

  const saveCarePack = async () => {
    if (!authStatus.logged_in) {
      alert('Please sign in to save your CarePack.');
      return;
    }
    if (!carePack.ready) return;

    const payload = { content: carePack.content, created_at: new Date().toISOString() };
    const response = await fetch('/api/carepack/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!response.ok) {
      alert('Failed to save CarePack.');
      return;
    }
    fetch('/api/carepack/list')
      .then((res) => (res.ok ? res.json() : { carepacks: [] }))
      .then((data) => setCarepackList(data.carepacks || []));
    alert('CarePack saved.');
  };

  const addTimelineEntry = () => {
    const severity = document.getElementById('severity-range').value;
    const note = document.getElementById('timeline-note').value.trim() || 'No notes added';
    const entry = { severity, note, timestamp: new Date().toISOString() };
    setTimeline((prev) => [entry, ...prev].slice(0, 20));
    document.getElementById('timeline-note').value = '';

    if (authStatus.logged_in) {
      fetch('/api/timeline/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ severity, note, timestamp: entry.timestamp })
      });
    }
  };

  const openHistory = async (sessionId) => {
    const response = await fetch(`/api/history/${sessionId}`);
    if (!response.ok) {
      return;
    }
    const data = await response.json();
    setHistoryMessages(data.messages || []);
    setHistoryOpen(true);
  };

  const deleteHistorySession = async (sessionId) => {
    if (!window.confirm('Delete this chat history?')) return;
    await fetch(`/api/history/delete/${sessionId}`, { method: 'DELETE' });
    refreshHistoryData();
  };

  const openCarepack = (content) => {
    setCarepackView(content);
    setCarepackOpen(true);
  };

  const handlePrescriptionUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    setPrescriptionLoading(true);
    setPrescriptionError('');
    setPrescriptionText('');
    setPrescriptionMeds([]);
    setPrescriptionSafety([]);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('symptoms', JSON.stringify(assessment?.symptoms || []));

    try {
      const response = await fetch('/api/prescription/upload', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Upload failed');
      }
      setPrescriptionText(data.text || '');
      setPrescriptionMeds(data.medications_detected || []);
      setPrescriptionSafety(data.safety || []);
    } catch (err) {
      setPrescriptionError(err.message);
    } finally {
      setPrescriptionLoading(false);
    }
  };

  const clearTimeline = async () => {
    setTimeline([]);
    localStorage.removeItem('symptom_timeline');
    if (authStatus.logged_in) {
      await fetch('/api/timeline/clear', { method: 'POST' });
    }
  };

  const runMedicationCheck = async () => {
    if (!medCheckInput.trim()) {
      setMedCheckError('Enter the medicines you are taking.');
      return;
    }
    setMedCheckLoading(true);
    setMedCheckError('');
    setMedCheckResult([]);
    setMedCheckInteractions([]);
    setMedCheckSafety([]);
    try {
      const response = await fetch('/api/medication/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: medCheckInput })
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Check failed');
      }
      setMedCheckResult(data.medications_detected || []);
      setMedCheckInteractions(data.interactions || []);
      setMedCheckSafety(data.safety || []);
    } catch (err) {
      setMedCheckError(err.message);
    } finally {
      setMedCheckLoading(false);
    }
  };

  const deleteCarepack = async (id) => {
    await fetch(`/api/carepack/delete/${id}`, { method: 'DELETE' });
    fetch('/api/carepack/list')
      .then((res) => (res.ok ? res.json() : { carepacks: [] }))
      .then((data) => setCarepackList(data.carepacks || []));
  };

  const handleLogout = async () => {
    sessionStorage.removeItem(AUTH_SESSION_KEY);
    await fetch('/api/auth/logout', { method: 'POST' });
    refreshAuthStatus();
  };

  const handleAuthSubmit = async (event) => {
    event.preventDefault();
    setAuthError('');
    setAuthLoading(true);

    const endpoint = authMode === 'register' ? '/api/auth/register' : '/api/auth/login';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: authUsername, password: authPassword })
    });

    const data = await response.json();
    setAuthLoading(false);

    if (!response.ok) {
      setAuthError(data.error || 'Authentication failed');
      return;
    }

    setAuthUsername('');
    setAuthPassword('');
    setShowAuth(false);
    sessionStorage.setItem(AUTH_SESSION_KEY, '1');
    refreshAuthStatus();
  };

  return (
    <div className="container">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <div className="logo-icon">⚕️</div>
            <div className="logo-text">
              <h1>HealthChat AI</h1>
              <p>No-Wait Triage & Care Plan</p>
            </div>
          </div>
          <button className="reset-btn" title="Start New Consultation" onClick={resetConversation}>
            <span>🔄</span> New Consultation
          </button>
        </div>
        <nav className="nav">
          <div className="nav-links">
            <a className="nav-link" href="#chat">Chat</a>
            <a className="nav-link" href="#carepack">CarePack</a>
            <a className="nav-link" href="#history">History</a>
            <a className="nav-link" href="#med-check">Med Check</a>
            <a className="nav-link" href="#prescription">Prescription</a>
            <a className="nav-link" href="#timeline">Timeline</a>
          </div>
          <div className="nav-auth">
            <button
              className="nav-btn theme-toggle"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? '☀️' : '🌙'}
            </button>
            {!authStatus.logged_in && (
              <button className="nav-btn" onClick={() => setShowAuth(true)}>
                Sign in
              </button>
            )}
            {authStatus.logged_in && (
              <>
                <button className="nav-btn" onClick={handleLogout}>Logout</button>
                <span className="user-badge">{authStatus.user?.username || 'Signed in'}</span>
              </>
            )}
          </div>
        </nav>
      </header>

      {showAuth && (
        <div className="auth-modal">
          <div className="auth-card">
            <div className="auth-header">
              <h3>{authMode === 'register' ? 'Create Account' : 'Sign In'}</h3>
              <button className="auth-close" onClick={() => setShowAuth(false)}>×</button>
            </div>
            <form onSubmit={handleAuthSubmit} className="auth-form">
              <label>Username</label>
              <input
                type="text"
                value={authUsername}
                onChange={(e) => setAuthUsername(e.target.value)}
                required
                minLength={3}
                placeholder="e.g. uday123"
              />
              <label>Password</label>
              <input
                type="password"
                value={authPassword}
                onChange={(e) => setAuthPassword(e.target.value)}
                required
                minLength={6}
                placeholder="At least 6 characters"
              />
              {authError && <div className="auth-error">{authError}</div>}
              <button className="secondary-btn" type="submit" disabled={authLoading}>
                {authLoading ? 'Please wait...' : authMode === 'register' ? 'Register' : 'Login'}
              </button>
            </form>
            <div className="auth-switch">
              {authMode === 'register' ? (
                <span>Already have an account? <button type="button" onClick={() => setAuthMode('login')}>Login</button></span>
              ) : (
                <span>New here? <button type="button" onClick={() => setAuthMode('register')}>Create one</button></span>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="disclaimer">
        <div className="disclaimer-icon">ℹ️</div>
        <div className="disclaimer-text">
          <strong>Medical Disclaimer:</strong> This chatbot provides educational information only and is not a
          substitute for professional medical advice, diagnosis, or treatment. In case of emergency, call 911
          immediately.
        </div>
      </div>

      <footer className="site-footer" id="footer">
        <div className="footer-content">
          <div className="footer-brand">
            <div className="footer-mark">
              <span className="pulse-dot"></span>
            </div>
            <div>
              <h3>HealthChat AI</h3>
              <p>Human-first guidance with fast, structured care summaries.</p>
            </div>
          </div>
          <div className="footer-highlights">
            <div className="footer-card">
              <strong>CarePack</strong>
              <span>Actionable plan + red flags</span>
            </div>
            <div className="footer-card">
              <strong>Med Check</strong>
              <span>Basic interaction safety scan</span>
            </div>
            <div className="footer-card">
              <strong>Context Aware</strong>
              <span>Sleep, stress, hydration factors</span>
            </div>
          </div>
        </div>
      </footer>

      <div className="app-shell">
        <aside className="sidebar" id="history">
          <div className="panel-header">
            <h2>Saved History</h2>
            <p>Chat history and CarePacks are saved per account.</p>
          </div>
          {!authStatus.logged_in && (
            <div className="panel-content">Sign in to view your saved history.</div>
          )}
          {authStatus.logged_in && (
            <div className="panel-content">
              <div className="history-columns">
                <div>
                  <h4>Recent Chats</h4>
                  {historySessions.length === 0 && <div className="med-forms">No chats saved yet.</div>}
                  <ul className="history-list">
                    {historySessions.map((item) => (
                      <li key={item.session_id}>
                        <button className="link-btn" onClick={() => openHistory(item.session_id)}>
                          Session {item.session_id.slice(0, 6)} · {item.message_count} messages
                        </button>
                        <button className="link-btn danger" onClick={() => deleteHistorySession(item.session_id)}>
                          Delete
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4>CarePacks</h4>
                  {carepackList.length === 0 && <div className="med-forms">No CarePacks saved yet.</div>}
                  <ul className="history-list">
                    {carepackList.map((item, index) => {
                      const displayIndex = carepackList.length - index;
                      return (
                        <li key={item.id}>
                          <button className="link-btn" onClick={() => openCarepack(item.content)}>
                            CarePack #{displayIndex}
                          </button>
                          <button className="link-btn danger" onClick={() => deleteCarepack(item.id)}>Delete</button>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </aside>

        <main className="chat-container" id="chat">
        <div className="chat-messages" ref={chatRef}>
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}-message`}>
              <div className="message-avatar">{message.role === 'user' ? '👤' : '🤖'}</div>
              <div className="message-content">
                <div
                  className="message-text"
                  dangerouslySetInnerHTML={{ __html: formatMessageText(message.text) }}
                />
                <div className="message-time">{message.time}</div>
              </div>
            </div>
          ))}
          {isWaiting && (
            <div className="message bot-message">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="message-text">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {quickReplies.length > 0 && (
          <div className="quick-replies">
            {quickReplies.map((reply) => (
              <button
                key={reply.label}
                className="quick-reply-btn"
                onClick={() => sendMessage(reply.value)}
              >
                {reply.label}
              </button>
            ))}
          </div>
        )}

        <div className="input-area">
          <div className="input-container">
            <textarea
              id="user-input"
              placeholder="Type your message here..."
              rows="1"
              maxLength="500"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
            ></textarea>
            <button className="send-btn" title="Send message" onClick={() => sendMessage()} disabled={isWaiting}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path
                  d="M22 2L11 13"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M22 2L15 22L11 13L2 9L22 2Z"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          </div>
          <div className="input-hint">Press Enter to send • Shift+Enter for new line</div>
        </div>
        </main>

        <aside className="sidepanel">
      <section className="panel-card carepack-panel" id="carepack">
        <div className="panel-header">
          <h2>CarePack</h2>
          <p>Unique add-on: summary, red flags, and saveable care plan.</p>
        </div>
        <div className="panel-content">
          {carePack.ready ? (
            <>
              <div dangerouslySetInnerHTML={{ __html: formatMessageText(carePack.content) }} />
              {assessment && (
                <div className="carepack-details">
                  <hr style={{ margin: '16px 0', border: 'none', borderTop: '1px solid #e5e7eb' }} />
                  <div><strong>Possible Conditions</strong></div>
                  <ul>
                    {(assessment.possible_conditions || []).map((cond, idx) => (
                      <li key={`${cond.name}-${idx}`}>{cond.description}</li>
                    ))}
                  </ul>
                  <div><strong>Care Tips</strong></div>
                  <ul>
                    {(assessment.advice?.general || []).map((item, idx) => (
                      <li key={`${item}-${idx}`}>{item}</li>
                    ))}
                  </ul>
                  <div><strong>When to Seek Care</strong></div>
                  <div className="med-forms">{assessment.advice?.when_to_seek_care}</div>
                </div>
              )}
            </>
          ) : (
            'Complete a consultation to generate your CarePack.'
          )}
          <hr style={{ margin: '16px 0', border: 'none', borderTop: '1px solid #e5e7eb' }} />
          <div><strong>Red-Flag Checklist</strong></div>
          <ul style={{ marginTop: '8px' }}>
            <li>Trouble breathing or chest pain</li>
            <li>Severe or worsening fever for 3+ days</li>
            <li>Confusion, fainting, or severe weakness</li>
            <li>Persistent vomiting or inability to keep fluids</li>
            <li>New rash with swelling of face/lips</li>
          </ul>
        </div>
        <div className="panel-actions">
          <button className="secondary-btn" onClick={saveCarePack} disabled={!carePack.ready}>Save CarePack</button>
        </div>
        <div className="panel-subtext">
          {authStatus.logged_in
            ? 'You are signed in. Your CarePack will be saved to your profile.'
            : 'Sign in to save your CarePack.'}
        </div>
      </section>

      <section className="panel-card timeline-panel" id="med-check">
        <div className="panel-header">
          <h2>Medication Interaction Checker</h2>
          <p>Enter medicines you are taking to check basic interactions.</p>
        </div>
        <div className="panel-content">
          <textarea
            rows="2"
            value={medCheckInput}
            onChange={(event) => setMedCheckInput(event.target.value)}
            placeholder="Example: ibuprofen + aspirin + sertraline"
          />
          <div className="panel-actions">
            <button className="secondary-btn" onClick={runMedicationCheck} disabled={medCheckLoading}>
              {medCheckLoading ? 'Checking...' : 'Check Interactions'}
            </button>
          </div>
          {medCheckError && <div className="auth-error">{medCheckError}</div>}
          {medCheckResult.length > 0 && (
            <div className="med-forms">
              <strong>Detected Medicines:</strong> {medCheckResult.join(', ')}
            </div>
          )}
          {medCheckSafety.length > 0 && (
            <ul className="safety-list">
              {medCheckSafety.map((item, index) => (
                <li key={`med-safe-${index}`} className="safety-item">
                  <strong>{item.name}</strong>: {item.safe_label}
                  {item.max_doses_per_day && (
                    <> — Max {item.max_doses_per_day} doses/day</>
                  )}
                  {item.note && <> · {item.note}</>}
                </li>
              ))}
            </ul>
          )}
          {medCheckInteractions.length > 0 && (
            <ul className="safety-list">
              {medCheckInteractions.map((item, index) => (
                <li key={`med-int-${index}`} className={`safety-item ${item.severity || 'unknown'}`}>
                  <strong>{item.severity?.toUpperCase() || 'NOTICE'}</strong>: {item.message}
                </li>
              ))}
            </ul>
          )}
          {medCheckResult.length > 0 && medCheckInteractions.length === 0 && (
            <div className="panel-subtext">No major interactions found in this basic check.</div>
          )}
          {medCheckResult.length === 0 && !medCheckLoading && !medCheckError && (
            <div className="panel-subtext">No medicines detected. Please check spelling (e.g., paracetamol).</div>
          )}
          <div className="panel-subtext">Basic check only. Always confirm with a clinician or pharmacist.</div>
        </div>
      </section>

      <section className="panel-card timeline-panel" id="prescription">
        <div className="panel-header">
          <h2>Prescription OCR</h2>
          <p>Upload a prescription photo to extract text and detected medicines.</p>
        </div>
        <div className="panel-content">
          <input type="file" accept="image/*" onChange={handlePrescriptionUpload} />
          {prescriptionLoading && <div className="med-forms">Processing...</div>}
          {prescriptionError && <div className="auth-error">{prescriptionError}</div>}
          {prescriptionText && (
            <>
              <div className="med-forms"><strong>Extracted Text:</strong></div>
              <pre className="ocr-text">{prescriptionText}</pre>
              <div className="med-forms"><strong>Detected Medicines:</strong> {prescriptionMeds.join(', ') || 'None'}</div>
              {prescriptionSafety.length > 0 && (
                <div className="med-safety">
                  <div className="med-forms"><strong>Safety Check (General Info):</strong></div>
                  <ul className="safety-list">
                    {prescriptionSafety.map((item, index) => (
                      <li key={`${item.name}-${index}`} className={`safety-item ${item.status}`}>
                        <strong>{item.name}</strong>: {item.label || 'Unclear'} — {item.reason}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              <div className="panel-subtext">OCR text only. Do not change dosing without a clinician.</div>
            </>
          )}
        </div>
      </section>

      <section className="panel-card timeline-panel" id="timeline">
        <div className="panel-header">
          <h2>Symptom Timeline</h2>
          <p>Track severity over time. Hidden by default.</p>
        </div>
        {!timelineOpen && (
          <button className="secondary-btn" onClick={() => setTimelineOpen(true)}>Show Timeline</button>
        )}
        {timelineOpen && (
          <>
            <div className="timeline-form">
              <label htmlFor="severity-range">Severity (1-10)</label>
              <input type="range" id="severity-range" min="1" max="10" defaultValue="5" />
              <textarea id="timeline-note" rows="2" placeholder="Add a quick note (e.g., fever spiked after lunch)"></textarea>
              <div className="panel-actions">
                <button className="secondary-btn" onClick={addTimelineEntry}>Add Entry</button>
                <button className="nav-btn" onClick={clearTimeline}>Clear Timeline</button>
                <button className="nav-btn" onClick={() => setTimelineOpen(false)}>Hide</button>
              </div>
            </div>
            <ul className="timeline-list">
              {timeline.map((entry, index) => (
                <li key={`${entry.timestamp}-${index}`} className="timeline-item">
                  <strong>Severity {entry.severity}/10</strong> · {new Date(entry.timestamp).toLocaleString()}<br />
                  {entry.note}
                </li>
              ))}
            </ul>
          </>
        )}
      </section>
        </aside>
      </div>

      {historyOpen && (
        <div className="auth-modal">
          <div className="auth-card">
            <div className="auth-header">
              <h3>Chat History</h3>
              <button className="auth-close" onClick={() => setHistoryOpen(false)}>×</button>
            </div>
            <div className="history-transcript">
              {historyMessages.map((msg, idx) => (
                <div key={`${msg.created_at}-${idx}`} className={`history-msg ${msg.role}`}>
                  <strong>{msg.role.toUpperCase()}</strong>: {msg.message}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {carepackOpen && (
        <div className="auth-modal">
          <div className="auth-card">
            <div className="auth-header">
              <h3>Saved CarePack</h3>
              <button className="auth-close" onClick={() => setCarepackOpen(false)}>×</button>
            </div>
            <div className="history-transcript" dangerouslySetInnerHTML={{ __html: formatMessageText(carepackView) }} />
          </div>
        </div>
      )}

    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<ChatApp />);
