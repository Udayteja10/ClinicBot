/**
 * Frontend JavaScript for Health Chatbot
 * Handles chat interface, API communication, and user interactions
 */

// Configuration
const API_BASE_URL = 'http://localhost:5001';
let sessionId = null;
let isWaitingForResponse = false;

// DOM Elements
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const resetBtn = document.getElementById('reset-btn');
const emergencyBanner = document.getElementById('emergency-banner');
const dismissEmergencyBtn = document.getElementById('dismiss-emergency');
const quickReplies = document.getElementById('quick-replies');
const carepackContent = document.getElementById('carepack-content');
const saveCarepackBtn = document.getElementById('save-carepack-btn');
const carepackAuthHint = document.getElementById('carepack-auth-hint');
const severityRange = document.getElementById('severity-range');
const timelineNote = document.getElementById('timeline-note');
const timelineAddBtn = document.getElementById('timeline-add-btn');
const timelineList = document.getElementById('timeline-list');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
    setInitialTime();
});

function initializeApp() {
    // Focus on input
    userInput.focus();

    // Auto-resize textarea
    userInput.addEventListener('input', autoResizeTextarea);

    // Clear quick replies on load
    clearQuickReplies();

    // Load timeline from local storage
    loadTimelineEntries();

    updateCarepackAuthHint();
}

function setupEventListeners() {
    // Send message on button click
    sendBtn.addEventListener('click', sendMessage);

    // Send message on Enter (but allow Shift+Enter for new line)
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Reset conversation
    resetBtn.addEventListener('click', resetConversation);

    // Dismiss emergency banner
    dismissEmergencyBtn.addEventListener('click', () => {
        emergencyBanner.classList.add('hidden');
    });

    // Save CarePack
    if (saveCarepackBtn) {
        saveCarepackBtn.addEventListener('click', saveCarepack);
    }

    // Timeline
    if (timelineAddBtn) {
        timelineAddBtn.addEventListener('click', addTimelineEntry);
    }
}

function setInitialTime() {
    const timeElement = document.getElementById('initial-time');
    if (timeElement) {
        timeElement.textContent = getCurrentTime();
    }
}

function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function autoResizeTextarea() {
    userInput.style.height = 'auto';
    userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
}

async function sendMessage() {
    const message = userInput.value.trim();

    // Validate message
    if (!message || isWaitingForResponse) {
        return;
    }

    // Clear input and reset height
    userInput.value = '';
    userInput.style.height = 'auto';

    // Display user message
    displayMessage(message, 'user');

    // Disable input while waiting
    setInputState(false);

    // Show typing indicator
    const typingIndicator = showTypingIndicator();

    try {
        // Send to API
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });

        if (!response.ok) {
            throw new Error('Failed to get response from server');
        }

        const data = await response.json();

        // Update session ID
        sessionId = data.session_id;

        // Remove typing indicator
        removeTypingIndicator(typingIndicator);

        // Check for emergency
        if (data.emergency && data.emergency.is_emergency) {
            showEmergencyBanner(data.emergency.level);
        }

        // Display bot response
        displayMessage(data.response, 'bot');

        // Update quick replies based on conversation state
        updateQuickReplies(data.state);

        // Update CarePack if assessment is complete
        if (data.state && data.state.stage === 'complete') {
            updateCarePack(data.response, data.state);
        }

    } catch (error) {
        console.error('Error sending message:', error);
        removeTypingIndicator(typingIndicator);
        displayMessage(
            "I apologize, but I'm having trouble connecting to the server. Please check that the server is running and try again.",
            'bot',
            true
        );
    } finally {
        // Re-enable input
        setInputState(true);
        userInput.focus();
    }
}

function updateQuickReplies(state) {
    if (!state || !state.stage) {
        clearQuickReplies();
        return;
    }

    if (state.stage === 'greeting') {
        setQuickReplies([
            { label: 'Hi', value: 'hi' },
            { label: 'Hello', value: 'hello' }
        ]);
        return;
    }

    if (state.stage === 'collecting_info') {
        // If gender is missing, offer gender chips
        if (!state.gender) {
            setQuickReplies([
                { label: 'Male', value: 'male' },
                { label: 'Female', value: 'female' },
                { label: 'Other', value: 'other' }
            ]);
            return;
        }

        // If age is missing, offer age range chips
        if (!state.age) {
            setQuickReplies([
                { label: 'Under 18', value: '16' },
                { label: '18-29', value: '22' },
                { label: '30-49', value: '35' },
                { label: '50+', value: '55' }
            ]);
            return;
        }
    }

    if (state.stage === 'symptoms') {
        setQuickReplies([
            { label: 'Fever', value: 'fever' },
            { label: 'Cough', value: 'cough' },
            { label: 'Headache', value: 'headache' },
            { label: 'Sore throat', value: 'sore throat' },
            { label: 'Nausea', value: 'nausea' },
            { label: 'Body ache', value: 'body ache' }
        ]);
        return;
    }

    if (state.stage === 'followup') {
        setQuickReplies([
            { label: "Didn't measure", value: "didn't measure" },
            { label: 'Not sure', value: 'not sure' },
            { label: 'No', value: 'no' },
            { label: 'Yes', value: 'yes' }
        ]);
        return;
    }

    if (state.stage === 'complete') {
        setQuickReplies([
            { label: 'Relief Plan', value: 'plan' },
            { label: 'Doctor Summary', value: 'summary' },
            { label: 'Start Over', value: 'restart' }
        ]);
        return;
    }

    clearQuickReplies();
}

function updateCarePack(responseText, state) {
    if (!carepackContent) {
        return;
    }

    const redFlags = getRedFlagChecklist();
    const redFlagHtml = redFlags.map((item) => `<li>${item}</li>`).join('');

    carepackContent.innerHTML = `
        <div><strong>Assessment Snapshot</strong></div>
        <div class="med-forms" style="margin-top: 8px;">${formatMessageText(responseText)}</div>
        <hr style="margin: 16px 0; border: none; border-top: 1px solid #e5e7eb;">
        <div><strong>Red-Flag Checklist</strong></div>
        <ul style="margin-top: 8px;">${redFlagHtml}</ul>
    `;

    if (saveCarepackBtn) {
        saveCarepackBtn.disabled = false;
    }

    updateCarepackAuthHint();
}

function getRedFlagChecklist() {
    return [
        'Trouble breathing or chest pain',
        'Severe or worsening fever for 3+ days',
        'Confusion, fainting, or severe weakness',
        'Persistent vomiting or inability to keep fluids',
        'New rash with swelling of face/lips'
    ];
}

function updateCarepackAuthHint() {
    if (!carepackAuthHint) {
        return;
    }
    const authStatus = window.__authStatus || { logged_in: false };
    if (authStatus.logged_in) {
        carepackAuthHint.textContent = 'You are signed in. Your CarePack will be saved to your profile.';
    } else {
        carepackAuthHint.textContent = 'Sign in to save your CarePack.';
    }
}

window.updateCarepackAuthHint = updateCarepackAuthHint;

async function saveCarepack() {
    const authStatus = window.__authStatus || { logged_in: false };
    if (!authStatus.logged_in) {
        alert('Please sign in to save your CarePack.');
        return;
    }

    if (!carepackContent) {
        return;
    }

    const payload = {
        content: carepackContent.textContent.trim(),
        created_at: new Date().toISOString()
    };

    try {
        const response = await fetch('/api/carepack/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!response.ok) {
            throw new Error('Failed to save CarePack');
        }
        alert('CarePack saved successfully.');
    } catch (error) {
        console.error(error);
        alert('Unable to save CarePack. Please try again.');
    }
}

function loadTimelineEntries() {
    if (!timelineList) {
        return;
    }
    const stored = localStorage.getItem('symptom_timeline');
    if (!stored) {
        return;
    }
    try {
        const entries = JSON.parse(stored);
        entries.forEach(renderTimelineEntry);
    } catch (error) {
        console.warn('Failed to load timeline', error);
    }
}

function addTimelineEntry() {
    if (!timelineList || !timelineNote || !severityRange) {
        return;
    }

    const entry = {
        severity: severityRange.value,
        note: timelineNote.value.trim() || 'No notes added',
        timestamp: new Date().toISOString()
    };

    renderTimelineEntry(entry);

    const stored = JSON.parse(localStorage.getItem('symptom_timeline') || '[]');
    stored.unshift(entry);
    localStorage.setItem('symptom_timeline', JSON.stringify(stored.slice(0, 20)));

    timelineNote.value = '';

    saveTimelineEntry(entry);
}

function renderTimelineEntry(entry) {
    const item = document.createElement('li');
    item.className = 'timeline-item';
    const time = new Date(entry.timestamp).toLocaleString();
    item.innerHTML = `<strong>Severity ${entry.severity}/10</strong> · ${time}<br>${entry.note}`;
    timelineList.prepend(item);
}

async function saveTimelineEntry(entry) {
    const authStatus = window.__authStatus || { logged_in: false };
    if (!authStatus.logged_in) {
        return;
    }
    try {
        await fetch('/api/timeline/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(entry)
        });
    } catch (error) {
        console.warn('Failed to save timeline entry', error);
    }
}

function setQuickReplies(replies) {
    if (!replies || replies.length === 0) {
        clearQuickReplies();
        return;
    }

    quickReplies.innerHTML = '';
    replies.forEach((reply) => {
        const button = document.createElement('button');
        button.className = 'quick-reply-btn';
        button.textContent = reply.label;
        button.addEventListener('click', () => {
            if (isWaitingForResponse) {
                return;
            }
            userInput.value = reply.value;
            sendMessage();
        });
        quickReplies.appendChild(button);
    });

    quickReplies.classList.remove('hidden');
}

function clearQuickReplies() {
    if (!quickReplies) {
        return;
    }
    quickReplies.classList.add('hidden');
    quickReplies.innerHTML = '';
}

function displayMessage(text, sender, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? '👤' : '🤖';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';

    if (isError) {
        textDiv.style.background = 'linear-gradient(135deg, #FF6B6B, #FF8E8E)';
        textDiv.style.color = 'white';
    }

    // Format text with markdown-like features
    textDiv.innerHTML = formatMessageText(text);

    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = getCurrentTime();

    contentDiv.appendChild(textDiv);
    contentDiv.appendChild(timeDiv);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);

    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    scrollToBottom();
}

function formatMessageText(text) {
    // Convert markdown-like formatting to HTML
    let formatted = text;

    // Bold text (**text**)
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Emoji bullets (convert • to proper list items)
    formatted = formatted.replace(/^([•📋🔍⚕️💡⏰🚨📞🏥👤📝])\s*(.+)$/gm, '<li>$2</li>');

    // Wrap consecutive list items in ul
    formatted = formatted.replace(/(<li>.*<\/li>\s*)+/g, '<ul>$&</ul>');

    // Line breaks
    formatted = formatted.replace(/\n\n/g, '</p><p>');
    formatted = '<p>' + formatted + '</p>';

    // Clean up empty paragraphs
    formatted = formatted.replace(/<p>\s*<\/p>/g, '');
    formatted = formatted.replace(/<p>\s*<ul>/g, '<ul>');
    formatted = formatted.replace(/<\/ul>\s*<\/p>/g, '</ul>');

    return formatted;
}

function showTypingIndicator() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message typing-indicator-container';
    messageDiv.id = 'typing-indicator';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🤖';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const typingDiv = document.createElement('div');
    typingDiv.className = 'message-text';
    typingDiv.innerHTML = `
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

    contentDiv.appendChild(typingDiv);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);

    chatMessages.appendChild(messageDiv);
    scrollToBottom();

    return messageDiv;
}

function removeTypingIndicator(indicator) {
    if (indicator && indicator.parentNode) {
        indicator.parentNode.removeChild(indicator);
    }
}

function setInputState(enabled) {
    isWaitingForResponse = !enabled;
    userInput.disabled = !enabled;
    sendBtn.disabled = !enabled;

    if (enabled) {
        sendBtn.style.opacity = '1';
    } else {
        sendBtn.style.opacity = '0.5';
    }
}

function scrollToBottom() {
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 100);
}

function showEmergencyBanner(level) {
    emergencyBanner.classList.remove('hidden');

    // Update banner text based on level
    const emergencyText = emergencyBanner.querySelector('.emergency-text p');
    if (level === 'critical') {
        emergencyText.textContent = '🚨 CALL 911 IMMEDIATELY - This may be a life-threatening emergency';
    } else if (level === 'urgent') {
        emergencyText.textContent = '⚠️ Seek immediate medical attention at an urgent care or emergency room';
    }

    // Auto-scroll to top to see banner
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function resetConversation() {
    if (!confirm('Are you sure you want to start a new consultation? This will clear the current conversation.')) {
        return;
    }

    try {
        // Call reset API
        const response = await fetch(`${API_BASE_URL}/api/reset`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId
            })
        });

        if (!response.ok) {
            throw new Error('Failed to reset conversation');
        }

        const data = await response.json();
        sessionId = data.session_id;

        // Clear chat messages
        chatMessages.innerHTML = '';

        // Hide emergency banner
        emergencyBanner.classList.add('hidden');

        // Clear quick replies
        clearQuickReplies();

        if (carepackContent) {
            carepackContent.textContent = 'Complete a consultation to generate your CarePack.';
        }
        if (saveCarepackBtn) {
            saveCarepackBtn.disabled = true;
        }

        // Show initial greeting
        displayMessage(
            "Welcome back! I'm ready to help with a new consultation.\n\n" +
            "Please type 'hello' or 'hi' to begin.",
            'bot'
        );

        // Focus input
        userInput.focus();

    } catch (error) {
        console.error('Error resetting conversation:', error);
        alert('Failed to reset conversation. Please refresh the page.');
    }
}

// Handle server connection errors gracefully
window.addEventListener('load', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        if (!response.ok) {
            throw new Error('Server not responding');
        }
        console.log('✅ Connected to server successfully');
    } catch (error) {
        console.warn('⚠️ Server connection issue:', error);
        displayMessage(
            "⚠️ Unable to connect to the server. Please ensure the Flask server is running on port 5001.\n\n" +
            "To start the server, run: python app.py",
            'bot',
            true
        );
    }
});
