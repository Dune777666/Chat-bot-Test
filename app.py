import spacy
import tensorflow as tf
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from googletrans import Translator
import numpy as np
import os
from simple_salesforce import Salesforce

app = Flask(__name__, static_folder='static')
CORS(app)  # Allow requests from your React frontend

# Load spaCy model for NLP
nlp = spacy.load('en_core_web_sm')

# Placeholder: Define intents and a simple TensorFlow model for demonstration
intents = ['greeting', 'goodbye', 'order_status', 'escalate']

# Dummy model: Replace with a real trained model for production
class DummyIntentModel:
    def predict(self, X):
        # Simple keyword-based intent detection for demo
        text = X[0].lower()
        if 'order' in text:
            return [[0, 0, 1, 0]]  # order_status
        if 'help' in text or 'agent' in text:
            return [[0, 0, 0, 1]]  # escalate
        if 'bye' in text:
            return [[0, 1, 0, 0]]  # goodbye
        return [[1, 0, 0, 0]]  # greeting

model = DummyIntentModel()

# Translator for multi-language support
translator = Translator()

# CRM integration placeholder
class CRMClient:
    def __init__(self):
        self.sf = None
        try:
            self.sf = Salesforce(
                username=os.getenv('SF_USERNAME'),
                password=os.getenv('SF_PASSWORD'),
                security_token=os.getenv('SF_SECURITY_TOKEN'),
                domain=os.getenv('SF_DOMAIN', 'login')
            )
        except Exception as e:
            print(f"Salesforce connection failed: {e}")

    def create_ticket(self, user_message):
        if self.sf:
            try:
                case = self.sf.Case.create({
                    'Subject': 'Chatbot Escalation',
                    'Description': user_message,
                    'Origin': 'Web'
                })
                print(f"Salesforce Case created: {case['id']}")
                return True
            except Exception as e:
                print(f"Failed to create Salesforce Case: {e}")
                return False
        else:
            print(f"CRM not connected. Ticket not created for: {user_message}")
            return False

crm_client = CRMClient()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    # Detect language and translate to English if needed
    detected = translator.detect(user_message)
    lang = detected.lang
    if lang != 'en':
        user_message_en = translator.translate(user_message, dest='en').text
    else:
        user_message_en = user_message
    # NLP processing
    doc = nlp(user_message_en)
    # Intent detection
    intent_probs = model.predict([user_message_en])
    intent_idx = np.argmax(intent_probs)
    intent = intents[intent_idx]
    # Check if user message matches a menu question (fuzzy match)
    for qa in MENU_QA:
        if qa['question'].lower() in user_message_en.lower() or qa['intent'] in user_message_en.lower():
            response_en = qa['answer']
            break
    else:
        # Improved greeting/goodbye logic for Hindi and other languages
        greeting_keywords = ['hello', 'hi', 'नमस्ते', 'नमस्कार', 'hola', 'bonjour', 'hallo', 'مرحبا', '你好']
        goodbye_keywords = ['bye', 'goodbye', 'अलविदा', 'विदा', 'adiós', 'au revoir', 'tschüss', 'وداعا', '再见']
        user_message_lower = user_message.lower()
        # Check for greeting/goodbye in original message (any language)
        if any(word in user_message_lower for word in greeting_keywords):
            response_en = "Hello! How can I assist you today?"
        elif any(word in user_message_lower for word in goodbye_keywords):
            response_en = "Goodbye! Have a great day!"
        elif intent == 'order_status':
            response_en = "Can you provide your order number so I can check the status?"
        elif intent == 'escalate':
            crm_client.create_ticket(user_message_en)
            response_en = "I've escalated your request to a human agent. Someone will contact you soon."
        else:
            response_en = "I'm not sure how to help with that. Would you like to speak to a human agent?"
    # Translate response back to user's detected language if needed
    if lang != 'en':
        response = translator.translate(response_en, dest=lang).text
    else:
        response = response_en
    return jsonify({'response': response})

# New menu Q&A pairs
MENU_QA = [
    {
        "intent": "reset_password",
        "question": "How do I reset my AD password?",
        "answer": "You can reset your Active Directory password using the Self-Service Portal. If you're locked out, I can initiate a reset—would you like me to do that?"
    },
    {
        "intent": "slow_computer",
        "question": "My system is very slow. What can I do?",
        "answer": "Please close unused applications, run a disk cleanup, and reboot your system. I can also initiate remote diagnostics—should I proceed?"
    },
    {
        "intent": "datacenter_outage",
        "question": "Is there any current outage reported in the Data Center?",
        "answer": "✅ No current outages reported in the data center. 📊 Last incident: Power fluctuation resolved at 10:32 AM."
    },
    {
        "intent": "check_server_status",
        "question": "What’s the status of Core Banking Server CBX-01?",
        "answer": "CBX-01 is operational. 🟢 CPU Load: 42%, Memory: 65%, Last backup: 2:00 AM today. Would you like detailed logs?"
    },
    {
        "intent": "run_health_check",
        "question": "Trigger a health check on branch systems in Region West.",
        "answer": "Initiating health check... ✅ 14 systems OK, ⚠️ 1 system (BR-WST-07) showing high latency. Raise a ticket?"
    },
    {
        "intent": "raise_ticket",
        "question": "Raise a P1 ticket for network outage in Mumbai branch.",
        "answer": "Creating Priority 1 ticket... 📝 Ticket ID: IT-44573, Escalated to Network Team. Want real-time updates?"
    },
    {
        "intent": "open_tickets_infra",
        "question": "Show all open tickets assigned to the Infra Team.",
        "answer": "Open tickets:\n1. IT-44521 – Firewall latency\n2. IT-44518 – Core switch maintenance\n3. IT-44516 – WAN link degraded"
    },
    {
        "intent": "last_access",
        "question": "Who last accessed the SWIFT server?",
        "answer": "Last login: opsadmin-04 at 11:34 PM (5 June) via HQ VPN. Need full audit trail?"
    },
    {
        "intent": "disable_user_access",
        "question": "Temporarily disable access to user john.k@bank.com",
        "answer": "Disabling access... ✅ AD access revoked, VPN credentials disabled. Will require manager approval to reactivate."
    },
    {
        "intent": "scheduled_maintenance",
        "question": "Is there a scheduled maintenance this weekend?",
        "answer": "Yes, maintenance planned: 🛠 Saturday 10:00 PM – Sunday 4:00 AM. Affected: Internet banking, Middleware servers."
    },
    {
        "intent": "deploy_patch",
        "question": "Deploy patch KB5025341 to all Windows 10 VMs.",
        "answer": "Deploying patch KB5025341 to 42 Windows 10 VMs... ⏱ ETA: 2 hours, 📊 Progress: 8%. Pause or exclude any VMs?"
    },
    {
        "intent": "vpn_status",
        "question": "Check VPN connectivity for remote users.",
        "answer": "Monitoring 873 VPN sessions... 🟢 862 active, ⚠️ 11 dropped in the last 30 minutes. Want a log report?"
    },
    {
        "intent": "trace_route",
        "question": "Trace route to payments gateway server.",
        "answer": "Traceroute to pgw.bank.com... 1. 10.0.1.1 – OK, 2. 10.0.2.1 – OK, 3. 192.168.1.14 – High latency. Raise a ticket?"
    },
    {
        "intent": "on_call_engineer",
        "question": "Who is on call for security today?",
        "answer": "🔐 On-call: Sanjay Mehra, 📱 Ext: 2245, 📧 smehra@bank.com. Should I notify them?"
    },
    {
        "intent": "last_dr_drill",
        "question": "When was the last DR drill performed?",
        "answer": "📅 Last DR drill: 12 May 2025, ✅ 100% success, ⏱ Duration: 2h 17m. Next scheduled: August 2025."
    }
]

@app.route('/menu', methods=['GET'])
def menu():
    # Return menu questions for the UI
    return jsonify({
        'menu': [q['question'] for q in MENU_QA]
    })

if __name__ == '__main__':
    app.run(debug=True)
