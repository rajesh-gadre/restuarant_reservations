import threading

# Simple in-memory conversation state manager (thread-safe)
class ConversationManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.state = {}  # key: call_sid, value: { 'history': [ {role, content} ], 'status': 'active|done|failed' }

    def start_conversation(self, call_sid, initial_history):
        with self.lock:
            self.state[call_sid] = {'history': initial_history[:], 'status': 'active'}

    def append(self, call_sid, role, content):
        with self.lock:
            if call_sid in self.state:
                self.state[call_sid]['history'].append({'role': role, 'content': content})

    def get_history(self, call_sid):
        with self.lock:
            return self.state.get(call_sid, {}).get('history', [])

    def set_status(self, call_sid, status):
        with self.lock:
            if call_sid in self.state:
                self.state[call_sid]['status'] = status

    def get_status(self, call_sid):
        with self.lock:
            return self.state.get(call_sid, {}).get('status', None)

    def clear(self, call_sid):
        with self.lock:
            if call_sid in self.state:
                del self.state[call_sid]
