from collections import defaultdict

class MemoryStore:
    def __init__(self):
        self.sessions = defaultdict(list)

    def get(self, session_id: str) -> str:
        return "\n".join(self.sessions[session_id])

    def append(self, session_id: str, message: str):
        self.sessions[session_id].append(message)

    def clear(self, session_id: str):
        self.sessions[session_id] = []
