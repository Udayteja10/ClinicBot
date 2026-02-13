"""
Chatbot Engine - Core Conversation Logic
Manages conversation state and orchestrates the consultation flow
"""

import re
from symptom_analyzer import SymptomAnalyzer
from safety_layer import SafetyLayer

class ChatbotEngine:
    """Main chatbot engine managing conversation flow"""
    
    # Conversation stages
    STAGE_GREETING = 'greeting'
    STAGE_COLLECTING_INFO = 'collecting_info'
    STAGE_SYMPTOMS = 'symptoms'
    STAGE_FOLLOWUP = 'followup'
    STAGE_ASSESSMENT = 'assessment'
    STAGE_COMPLETE = 'complete'
    
    def __init__(self):
        self.stage = self.STAGE_GREETING
        self.symptom_analyzer = SymptomAnalyzer()
        self.safety_layer = SafetyLayer()
        self.conversation_history = []
        self.pending_age = None
        self.pending_gender = None
        self.followup_count = 0
        self.max_followup = 3
        self.has_basic_info = False
        self.user_name = None  # Track user's name for personalization
    
    def process_message(self, user_message):
        """
        Process user message and generate appropriate response
        Returns: (bot_response, emergency_info)
        """
        # Always check for emergencies first
        is_emergency, emergency_level, emergency_response = self.safety_layer.scan_message(user_message)
        
        if is_emergency:
            return emergency_response, {
                'is_emergency': True,
                'level': emergency_level
            }
        
        # Store message in history
        self.conversation_history.append({
            'role': 'user',
            'message': user_message
        })
        
        # Process based on current stage
        response = self._process_by_stage(user_message)
        
        self.conversation_history.append({
            'role': 'bot',
            'message': response
        })
        
        return response, {'is_emergency': False}
    
    def _process_by_stage(self, message):
        """Route message processing based on conversation stage"""
        
        if self.stage == self.STAGE_GREETING:
            return self._handle_greeting(message)
        
        elif self.stage == self.STAGE_COLLECTING_INFO:
            return self._handle_collecting_info(message)
        
        elif self.stage == self.STAGE_SYMPTOMS:
            return self._handle_symptoms(message)
        
        elif self.stage == self.STAGE_FOLLOWUP:
            return self._handle_followup(message)
        
        elif self.stage == self.STAGE_COMPLETE:
            return self._handle_complete(message)
        
        return "I'm here to help. Could you tell me more about what you're experiencing?"
    
    def _handle_greeting(self, message):
        """Handle initial greeting - more conversational"""
        # Try to extract name from greeting
        self._extract_name(message)
        
        self.stage = self.STAGE_COLLECTING_INFO
        
        greeting = "Hello"
        if self.user_name:
            greeting = f"Hello, {self.user_name}"
        
        return (f"{greeting}! I'm here to help you understand your symptoms and provide guidance. "
                "Think of this as a quick, no-wait triage conversation that helps you decide your next step.\n\n"
                "⚠️ **Quick note**: This is for informational purposes only. If you're experiencing a medical emergency, "
                "please call 911 right away.\n\n"
                "To give you the best advice, I'd like to know a bit about you. Could you tell me your age and gender? "
                "You can say something like: 'I'm a 28-year-old male' or just '28, male'")
    
    def _extract_name(self, message):
        """Extract user's name from message"""
        if self.user_name:
            return  # Already have name
        
        message_lower = message.lower()
        message_stripped = message.strip()
        
        # Don't extract name from age/gender patterns like "20, male" or "20 male"
        age_gender_pattern = r'^\d+\s*,?\s*(male|female|m|f|other)$'
        if re.match(age_gender_pattern, message_stripped, re.IGNORECASE):
            return  # This is age/gender info, not a name
        
        # Common name introduction patterns - case insensitive search but capture original case
        patterns = [
            r"(?:i'm|i am|my name is|this is|call me|name's)\s+([A-Za-z]+)",
            r"^([A-Z][a-z]+)\s+here",
            r"hi,?\s+(?:i'm|i am)\s+([A-Za-z]+)",
            r"hello,?\s+(?:i'm|i am)\s+([A-Za-z]+)",
            r"\bi\s+am\s+([A-Z][a-z]+)",
            r"\bname\s+is\s+([A-Z][a-z]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                name = match.group(1).capitalize()
                # Avoid common words that aren't names
                if name.lower() not in ['hello', 'hi', 'hey', 'good', 'morning', 'evening', 'having', 'feeling', 'years', 'year', 'male', 'female', 'old', 'yes', 'no', 'okay', 'ok']:
                    self.user_name = name
                    return
        
        # If message is a single word and looks like a name (starts with capital or all lowercase)
        # This handles cases where user just types their name after being asked
        if len(message_stripped.split()) == 1 and len(message_stripped) >= 2:
            potential_name = message_stripped.capitalize()
            # Avoid common non-name words and numbers
            if potential_name.lower() not in ['hello', 'hi', 'hey', 'good', 'morning', 'evening', 'night', 'yes', 'no', 'okay', 'ok', 'thanks', 'thank', 'bye', 'the', 'and', 'male', 'female', 'old', 'years', 'year'] and not message_stripped.isdigit():
                self.user_name = potential_name
                return
    
    def _handle_collecting_info(self, message):
        """Intelligently extract age and gender from natural language"""
        message_lower = message.lower()
        
        # Try to extract name if we don't have it
        self._extract_name(message)
        
        # Handle casual conversation intelligently (not just exact matches)
        # Check for greetings and small talk by looking for key words
        
        # "How are you" variations (handles typos and variations)
        if any(word in message_lower for word in ['how are', 'how r', 'how u', 'how\'s it', 'hows it']):
            if self.user_name:
                return (f"I'm doing well, thank you for asking! 😊 Now, let's focus on you.\n\n"
                       f"So {self.user_name}, could you tell me your age and gender? You can say it however feels natural.")
            else:
                return ("I'm doing well, thank you for asking! 😊 But more importantly, how are YOU feeling?\n\n"
                       "To help you better, could you tell me your age and gender? You can say it however feels natural - like '25 male' or 'I'm a 30-year-old woman'")
        
        # Greetings
        if any(word in message_lower for word in ['good morning', 'good evening', 'good afternoon']):
            time_greeting = 'Good morning' if 'morning' in message_lower else 'Good evening' if 'evening' in message_lower else 'Good afternoon'
            if self.user_name:
                return f"{time_greeting}, {self.user_name}! 😊\n\nCould you tell me your age and gender?"
            else:
                return f"{time_greeting}! 😊\n\nTo help you, could you tell me your age and gender?"
        
        # Casual "what's up" or "hey"
        if 'whats up' in message_lower.replace(' ', '') or 'wassup' in message_lower or message_lower.strip() in ['hey', 'sup']:
            return "Not much! Just here to help you out. 😊\n\nCould you tell me your age and gender so I can assist you better?"
        
        # Try to extract age
        age_patterns = [
            r'\b(\d{1,3})\s*(?:years?\s*old|yr|y\.?o\.?)\b',
            r'\bi\s*(?:am|\'m)\s*(\d{1,3})\b',
            r'\b(\d{1,3})\s*(?:male|female|man|woman|boy|girl)',
            r'\b(\d{1,3})\b'
        ]
        
        age = None
        for pattern in age_patterns:
            age_match = re.search(pattern, message_lower)
            if age_match:
                potential_age = int(age_match.group(1))
                if 0 < potential_age < 120:
                    age = potential_age
                    break
        
        # Try to extract gender (word-boundary safe, avoids "male" in "female")
        gender = None
        if re.search(r'\b(female|woman|girl)\b', message_lower) or re.search(r'\b(f)\b', message_lower):
            gender = 'female'
        elif re.search(r'\b(male|man|boy)\b', message_lower) or re.search(r'\b(m)\b', message_lower):
            gender = 'male'
        elif any(word in message_lower for word in ['other', 'non-binary', 'prefer not']):
            gender = 'other'
        
        # Handle what we got
        if age and gender:
            self.pending_age = age
            self.pending_gender = gender
            self.symptom_analyzer.set_demographics(age, gender)
            self.has_basic_info = True
            self.stage = self.STAGE_SYMPTOMS
            
            # If we don't have the name yet, ask for it
            if not self.user_name:
                return (f"Got it  Thanks for sharing that!\n\n"
                       f"And what's your name? (So I can address you properly 😊)")
            
            # If we already have the name, proceed to symptoms
            response = f"Perfect, {self.user_name}! {age}-year-old {gender}."
            
            return (f"{response} Thanks for sharing that!\n\n"
                   f"Now, tell me what's been bothering you. What symptoms are you experiencing? "
                   f"Feel free to describe it naturally - like you're talking to a friend. "
                   f"For example: 'I've had a headache since yesterday' or 'I'm feeling feverish and tired' 😊")
        
        elif age and not gender:
            # If gender was provided earlier, finalize demographics
            if self.pending_gender:
                self.pending_age = age
                self.symptom_analyzer.set_demographics(self.pending_age, self.pending_gender)
                self.has_basic_info = True
                self.stage = self.STAGE_SYMPTOMS

                if not self.user_name:
                    return (f"Perfect! {self.pending_age}-year-old {self.pending_gender}. Thanks for sharing that!\n\n"
                           f"And what's your name? (So I can address you properly 😊)")

                response = f"Perfect, {self.user_name}! {self.pending_age}-year-old {self.pending_gender}."
                return (f"{response} Thanks for sharing that!\n\n"
                       f"Now, tell me what's been bothering you. What symptoms are you experiencing? "
                       f"Feel free to describe it naturally - like you're talking to a friend.")

            self.pending_age = age
            response = f"Thanks! I got your age as {age}."
            if self.user_name:
                response = f"Thanks, {self.user_name}! I got your age as {age}."
            return f"{response} And your gender? (male/female/other)"
        
        elif gender and not age:
            self.pending_gender = gender
            # Check if we already have pending_age from before
            if self.pending_age:
                # We have both now!
                self.symptom_analyzer.set_demographics(self.pending_age, self.pending_gender)
                self.has_basic_info = True
                self.stage = self.STAGE_SYMPTOMS
                
                # If we don't have the name yet, ask for it
                if not self.user_name:
                    return (f"Perfect! {self.pending_age}-year-old {self.pending_gender}. Thanks for sharing that!\n\n"
                           f"And what's your name? (So I can address you properly 😊)")
                
                # If we already have the name, proceed to symptoms
                response = f"Perfect, {self.user_name}! {self.pending_age}-year-old {self.pending_gender}."
                
                return (f"{response} Thanks for sharing that!\n\n"
                       f"Now, tell me what's been bothering you. What symptoms are you experiencing? "
                       f"Feel free to describe it naturally - like you're talking to a friend.")
            else:
                return f"Thanks! And how old are you?"
        
        else:
            # More natural fallback
            if self.user_name:
                return (f"I'd love to help you, {self.user_name}! To give you the best advice, "
                       f"could you tell me your age and gender? Just say it naturally - like '25 male' or 'I'm 30, female'")
            else:
                return ("I didn't quite catch that. Could you tell me your age and gender? "
                       "You can say it however feels natural - like '25 male' or 'I'm a 30-year-old woman'")
    
    def _handle_symptoms(self, message):
        """Process symptom description - very flexible and conversational"""
        
        message_lower = message.lower()
        
        # Handle casual health-related conversation
        if any(phrase in message_lower for phrase in ['how are', 'how r', 'how u']):
            if self.user_name:
                return (f"I'm doing well, {self.user_name}, thank you for asking! 😊\n\n"
                       f"But let's focus on you - what's been bothering you? Tell me about your symptoms.")
            else:
                return ("I'm doing well, thank you! 😊 But more importantly, how are YOU feeling?\n\n"
                       "Tell me what's been bothering you. What symptoms are you experiencing?")
        
        # Handle thanks/appreciation
        if any(word in message_lower for word in ['thanks', 'thank you', 'appreciate']):
            if self.user_name:
                return f"You're welcome, {self.user_name}! 😊 Now, what brings you in today? Tell me about your symptoms."
            else:
                return "You're welcome! 😊 Now, what brings you in today? Tell me about your symptoms."
        
        # Handle general greetings
        if message_lower.strip() in ['hi', 'hello', 'hey', 'good morning', 'good evening']:
            if self.user_name:
                return f"Hello again, {self.user_name}! 😊 So, what symptoms are you experiencing?"
            else:
                return "Hello! 😊 What symptoms are you experiencing today?"
        
        # Extract symptoms and duration BEFORE trying to extract name
        # This prevents treating symptoms as names
        symptoms = self.symptom_analyzer.extract_symptoms(message)
        duration = self.symptom_analyzer.extract_duration(message)
        
        # Extract lifestyle context (sleep, stress, etc.)
        context = self.symptom_analyzer.extract_context(message)
        self.symptom_analyzer.extract_severity(message)
        
        # If we don't have a name yet and user provided symptoms instead of name
        if not self.user_name and symptoms:
            # User skipped providing name and went straight to symptoms - that's okay!
            # Process the symptoms and continue without forcing name collection
            pass  # Continue to symptom processing below
        elif not self.user_name and not symptoms:
            # Try to extract name only if no symptoms were found
            self._extract_name(message)
            
            # If we got a name but no symptoms, acknowledge and ask for symptoms
            if self.user_name:
                return (f"Nice to meet you, {self.user_name}! 😊\n\n"
                       f"So {self.user_name}, what brings you in today? "
                       f"Tell me about any symptoms or discomfort you're experiencing.")
        
        if not symptoms:
            # Be empathetic and helpful
            return ("I want to make sure I understand what you're going through. "
                   "Could you describe how you're feeling? What's bothering you? "
                   "Any pain, discomfort, fever, or other symptoms?\n\n"
                   "Don't worry about using medical terms - just tell me in your own words what's happening.")
        
        # Generate empathetic response
        response = self._generate_empathetic_acknowledgment(symptoms, duration, message)
        
        # Move to follow-up questions
        self.stage = self.STAGE_FOLLOWUP
        followup_questions = self.symptom_analyzer.get_followup_questions(2)
        
        if followup_questions:
            response += "\n\nTo help me understand better, I have a couple of questions:\n\n"
            for i, question in enumerate(followup_questions, 1):
                response += f"{i}. {question}\n"
            response += "\nFeel free to answer in any way that's comfortable for you!"
        else:
            # Skip to assessment if no follow-up needed
            self.stage = self.STAGE_ASSESSMENT
            return self._generate_assessment()
        
        return response
    
    def _generate_empathetic_acknowledgment(self, symptoms, duration, original_message):
        """Generate a natural, empathetic response acknowledging symptoms"""
        responses = []
        
        # Empathetic opening
        if 'headache' in ' '.join(symptoms):
            responses.append("I'm sorry to hear you're dealing with a headache. Those can be really uncomfortable.")
        elif 'fever' in ' '.join(symptoms):
            responses.append("A fever can definitely make you feel miserable. I understand that's tough.")
        elif 'pain' in ' '.join(symptoms):
            responses.append("I'm sorry you're in pain. Let's see if we can figure out what's going on.")
        else:
            responses.append("Thanks for sharing that with me. Let me make sure I understand what you're experiencing.")
        
        # Summarize symptoms naturally (use friendly display names)
        display = [self.symptom_analyzer._display_symptom(symptom) for symptom in symptoms]
        if len(display) == 1:
            responses.append(f"So you're experiencing {display[0]}.")
        elif len(display) == 2:
            responses.append(f"So you're dealing with {display[0]} and {display[1]}.")
        else:
            responses.append(f"So you're experiencing {', '.join(display[:2])}, and a few other symptoms.")
        
        # Acknowledge duration if provided
        if duration:
            if duration == 1:
                responses.append("And this started today.")
            elif duration <= 3:
                responses.append(f"This has been going on for {duration} days now.")
            else:
                responses.append(f"You've been dealing with this for {duration} days - that must be frustrating.")
        
        return " ".join(responses)
    
    def _handle_followup(self, message):
        """Process follow-up responses - very flexible"""
        
        # Always try to extract name if mentioned
        self._extract_name(message)
        
        message_lower = message.lower()
        
        # Handle casual conversation during follow-up
        if any(phrase in message_lower for phrase in ['how are', 'how r', 'how u']):
            if self.user_name:
                return f"I'm doing well, {self.user_name}, thanks for asking! 😊\n\nNow, could you answer the question about your symptoms?"
            else:
                return "I'm doing well, thanks! 😊\n\nCould you answer the question about your symptoms?"
        
        # Handle if they just say thanks
        if message_lower.strip() in ['thanks', 'thank you', 'ok', 'okay']:
            if self.user_name:
                return f"You're welcome, {self.user_name}! 😊\n\nCould you tell me more about your symptoms? Any other details that might help?"
            else:
                return "You're welcome! 😊\n\nCould you tell me more about your symptoms? Any other details that might help?"
        
        # Extract any additional symptoms mentioned
        new_symptoms = self.symptom_analyzer.extract_symptoms(message)
        
        # Extract duration if not already set
        if not self.symptom_analyzer.duration_days:
            self.symptom_analyzer.extract_duration(message)

        # Extract lifestyle context (sleep, stress, hydration)
        self.symptom_analyzer.extract_context(message)
        self.symptom_analyzer.extract_severity(message)
        cough_type = self.symptom_analyzer.extract_cough_type(message)
        meds_found = self.symptom_analyzer.extract_current_meds(message)
        
        self.followup_count += 1
        
        # Acknowledge their response naturally
        if self.user_name:
            acknowledgments = [
                f"I see, {self.user_name}, thanks for clarifying that.",
                f"Got it, {self.user_name}, that's helpful to know.",
                f"Okay, {self.user_name}, I understand.",
                f"Thanks for sharing that detail, {self.user_name}.",
                f"That helps me get a better picture, {self.user_name}."
            ]
        else:
            acknowledgments = [
                "I see, thanks for clarifying that.",
                "Got it, that's helpful to know.",
                "Okay, I understand.",
                "Thanks for sharing that detail.",
                "That helps me get a better picture."
            ]
        
        response = acknowledgments[self.followup_count % len(acknowledgments)]
        
        if new_symptoms:
            display_new = [self.symptom_analyzer._display_symptom(symptom) for symptom in new_symptoms]
            response += f" I also noted you mentioned {', '.join(display_new)}."
        if cough_type:
            response += f" I noted your cough is {cough_type}."
        if meds_found:
            response += f" I noted you're taking: {', '.join([m.title() for m in meds_found])}."
        
        # Decide whether to ask more questions or provide assessment
        if self.followup_count < self.max_followup:
            followup_questions = self.symptom_analyzer.get_followup_questions(1)
            
            if followup_questions:
                response += f"\n\n{followup_questions[0]}"
                return response
        
        # Move to assessment
        if self.user_name:
            response += f"\n\nAlright, {self.user_name}, I think I have enough information to give you my assessment."
        else:
            response += "\n\nAlright, I think I have enough information to give you my assessment."
        self.stage = self.STAGE_ASSESSMENT
        return response + "\n\n" + self._generate_assessment()
    
    def _generate_assessment(self):
        """Generate final medical assessment"""
        self.stage = self.STAGE_COMPLETE
        assessment_response = self.symptom_analyzer.format_assessment_response()
        
        closing = "That's my assessment based on what you've told me."
        if self.user_name:
            closing = f"That's my assessment, {self.user_name}, based on what you've told me."
        
        assessment_response += ("\n\n" + "="*50 + "\n\n"
                               f"{closing} Do you have any questions? "
                               "Or would you like one of these next steps?\n\n"
                               "✨ **CareCompass (Unique Feature)**:\n"
                               "• Reply `plan` for a personalized 24-hour relief plan\n"
                               "• Reply `summary` for a doctor-ready summary you can share at a clinic\n"
                               "• Reply `restart` to start a new consultation")
        
        return assessment_response
    
    def _handle_complete(self, message):
        """Handle post-assessment conversation - very conversational"""
        message_lower = message.lower()

        # Direct responses to red-flag / urgent care queries (with or without '?')
        if any(phrase in message_lower for phrase in ['warning sign', 'red flag', 'urgent care', 'emergency', 'when should']):
            return ("Here are common warning signs that should prompt urgent care:\n\n"
                   "• Trouble breathing or chest pain\n"
                   "• Severe or worsening fever for 3+ days\n"
                   "• Confusion, fainting, or severe weakness\n"
                   "• Persistent vomiting or inability to keep fluids\n"
                   "• New rash with swelling of face/lips\n\n"
                   "If any of these occur, seek urgent medical care immediately.")

        
        # Home-care guidance
        if any(phrase in message_lower for phrase in [
            'manage symptoms at home', 'manage at home', 'home care', 'self care',
            'what should i do at home', 'how should i manage', 'manage symptoms',
            'take care at home', 'care at home'
        ]):
            assessment = self.symptom_analyzer.generate_assessment()
            advice = assessment.get('advice', {})
            tips = advice.get('general', [])
            response = "Here’s a safe at-home care plan based on what you told me:\n\n"
            for item in tips:
                response += f"• {item}\n"

            context_insights = self.symptom_analyzer._get_context_insights()
            if context_insights:
                response += "\nPossible contributors I noticed:\n"
                for insight in context_insights:
                    response += f"• {insight}\n"

            response += f"\n⏰ Next steps: {advice.get('when_to_seek_care', 'If symptoms worsen, seek care.')}\n"
            response += "\nIf you want a structured 24-hour plan, reply `plan`."
            return response

        # Check if user wants to start over
        if message_lower.strip() == '3' or any(word in message_lower for word in ['new', 'start over', 'reset', 'different', 'another', 'restart']):
            self.reset()
            return ("Of course! Let's start fresh.\n\n"
                   "Tell me your age and gender, and then we can talk about what's bothering you.")

        # CareCompass actions
        message_clean = message_lower.strip()
        if message_clean in ['1', 'plan', 'care plan', 'relief plan'] or 'relief plan' in message_lower or 'care plan' in message_lower:
            return self.symptom_analyzer.format_relief_plan_response()

        if message_clean in ['2', 'summary', 'doctor summary', 'clinic summary', 'report'] or 'summary' in message_lower:
            return self.symptom_analyzer.format_doctor_summary_response()

        # General Q&A (tests, causes, duration, home care, meds, diet, contagious)
        general_answer = self._answer_general_question(message)
        if general_answer:
            return general_answer
        
        # Check if user is asking questions
        if '?' in message:
            return ("I can help with home care, medicines, tests, red flags, diet, and what to watch for. "
                   "Tell me which one you want.")
        
        # Check for thanks/goodbye
        if any(word in message_lower for word in ['thank', 'thanks', 'bye', 'goodbye']):
            farewell = "You're very welcome!"
            if self.user_name:
                farewell = f"You're very welcome, {self.user_name}!"
            return (f"{farewell} I hope you feel better soon. Remember to follow the recommendations, "
                   "and don't hesitate to seek professional care if things get worse.\n\n"
                   "Take care! 😊")
        
        # Generic helpful response
        return ("I'm here to help! Feel free to ask any questions about the assessment, "
               "or if you'd like to start a new consultation, just let me know.")

    def _answer_general_question(self, message):
        """Answer common post-assessment questions without deflecting."""
        message_lower = message.lower()
        assessment = self.symptom_analyzer.generate_assessment()
        symptoms = assessment.get('symptoms', [])
        symptom_text = ' '.join(symptoms).lower()
        duration = assessment.get('duration')
        cough_type = assessment.get('cough_type')
        possible = assessment.get('possible_conditions', [])

        # Tests
        if any(phrase in message_lower for phrase in ['test', 'tests', 'testing']):
            response = "Here’s a general guide on tests clinicians may consider:\n\n"
            response += "• Mild symptoms without red flags: often no tests needed.\n"
            if 'fever' in symptom_text or 'body ache' in symptom_text:
                response += "• Fever/body aches: a flu or COVID test may be considered.\n"
            if 'sore throat' in symptom_text:
                response += "• Sore throat: throat exam or rapid strep test can be considered.\n"
            if 'shortness of breath' in symptom_text or 'chest pain' in symptom_text:
                response += "• Breathing issues/chest pain: oxygen check or chest X‑ray may be needed.\n"
            if 'diarrhea' in symptom_text or 'vomiting' in symptom_text:
                response += "• Persistent GI symptoms: stool test or basic labs may be considered.\n"
            if duration and duration >= 14:
                response += "• Symptoms >2 weeks: clinician may consider imaging or spirometry.\n"
            response += "\nIf symptoms worsen or you develop red flags, seek care promptly."
            return response

        # Causes / why
        if any(phrase in message_lower for phrase in ['cause', 'why', 'reason']):
            if possible:
                top_conditions = ", ".join([c['description'].title() for c in possible[:2]])
                return (f"Based on your symptoms, common causes include: {top_conditions}.\n\n"
                        "This isn’t a diagnosis, but it’s a reasonable starting point.")
            if 'cough' in symptom_text:
                return "Common causes of cough include viral infections, allergies, or post‑nasal drip."
            if 'fever' in symptom_text:
                return "Fever is most often caused by viral infections; hydration and rest help recovery."
            if 'stomach pain' in symptom_text or 'abdominal pain' in symptom_text:
                return "Stomach pain is often due to indigestion, gastritis, or a mild stomach bug."
            return "Symptoms like these are commonly caused by minor viral infections or lifestyle triggers."

        # Duration / how long
        if any(phrase in message_lower for phrase in ['how long', 'duration', 'when will', 'how many days']):
            response = "Typical symptom durations (if no red flags):\n\n"
            if 'cough' in symptom_text:
                response += "• Cough: 1–2 weeks is common.\n"
            if 'fever' in symptom_text:
                response += "• Fever: 2–3 days is common for viral illness.\n"
            if 'sore throat' in symptom_text:
                response += "• Sore throat: 3–5 days.\n"
            if 'diarrhea' in symptom_text or 'vomiting' in symptom_text:
                response += "• Stomach bug: 1–3 days.\n"
            response += "\nIf symptoms persist beyond a week or worsen, seek care."
            return response

        # Home care
        if any(phrase in message_lower for phrase in ['manage symptoms at home', 'manage at home', 'home care', 'self care', 'what should i do at home', 'how should i manage', 'manage symptoms', 'care at home']):
            advice = assessment.get('advice', {})
            tips = advice.get('general', [])
            response = "Here’s a safe at‑home care plan based on what you told me:\n\n"
            for item in tips:
                response += f"• {item}\n"
            if 'cough' in symptom_text:
                response += "• Warm fluids and honey (if over 1 year old) can soothe cough.\n"
            response += f"\n⏰ Next steps: {advice.get('when_to_seek_care', 'If symptoms worsen, seek care.')}\n"
            return response

        # Medications / tablets / dosage
        if any(phrase in message_lower for phrase in ['medicine', 'medication', 'tablet', 'tablets', 'dosage', 'dose', 'safe to take']):
            meds = self.symptom_analyzer._get_medication_recommendations(assessment.get('possible_conditions', []))
            if meds:
                response = "Here are common OTC options used for these symptoms:\n\n"
                for i, med in enumerate(meds[:2], 1):
                    response += f"{i}. {med['name']} — {med['timing']}\n"
                if 'cough' in symptom_text and cough_type:
                    response += f"\nCough type noted: {cough_type.title()}.\n"
                response += "\nIf you have allergies, ulcers, kidney disease, or are on other meds, check with a clinician."
                return response
            return "For safety, I can suggest OTC options once I know your specific symptom details."

        # Medication interaction checks
        if any(phrase in message_lower for phrase in ['interaction', 'interactions', 'together', 'mix', 'combine']):
            meds_found = self.symptom_analyzer.extract_current_meds(message)
            if not meds_found and not self.symptom_analyzer.current_meds:
                return "Tell me the medicines you’re taking (e.g., ibuprofen + aspirin), and I’ll check interactions."
            interactions = self.symptom_analyzer.check_med_interactions()
            if interactions:
                response = "Here’s a basic interaction check:\n\n"
                for item in interactions:
                    response += f"• {item['message']} (Meds: {', '.join([m.title() for m in item['meds']])})\n"
                response += "\nThis is a basic check only — confirm with a clinician or pharmacist."
                return response
            return "No major interactions found in this basic check. If you’re on prescriptions, confirm with a clinician."

        # Diet / food
        if any(phrase in message_lower for phrase in ['diet', 'food', 'eat', 'eating']):
            if 'diarrhea' in symptom_text or 'vomiting' in symptom_text or 'nausea' in symptom_text:
                return "Stick to bland foods (rice, toast, bananas) and small sips of fluids. Avoid spicy/fatty foods."
            if 'cough' in symptom_text or 'sore throat' in symptom_text:
                return "Warm fluids and soups can help. Avoid very cold drinks if they trigger coughing."
            return "Eat light, balanced meals and stay hydrated."

        # Contagious
        if any(phrase in message_lower for phrase in ['contagious', 'spread', 'infectious']):
            if 'cough' in symptom_text or 'fever' in symptom_text or 'sore throat' in symptom_text:
                return "It may be contagious if caused by a viral infection. Wash hands often and avoid close contact if possible."
            return "Some conditions are contagious, others aren’t — it depends on the cause."

        return None
    
    def reset(self):
        """Reset conversation state"""
        self.stage = self.STAGE_GREETING
        self.symptom_analyzer.reset()
        self.safety_layer.reset()
        self.conversation_history = []
        self.pending_age = None
        self.pending_gender = None
        self.followup_count = 0
        self.has_basic_info = False
        self.user_name = None
    
    def get_state(self):
        """Get current conversation state"""
        return {
            'stage': self.stage,
            'symptoms': self.symptom_analyzer.reported_symptoms,
            'age': self.pending_age,
            'gender': self.pending_gender,
            'emergency_status': self.safety_layer.get_status(),
            'assessment': self.symptom_analyzer.last_assessment
        }
