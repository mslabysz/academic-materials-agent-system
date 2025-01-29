from dataclasses import dataclass, field
from time import time
from typing import List, Dict, Any

@dataclass
class Message:
    from_agent: str
    to_agent: str
    content: Dict[str, Any]
    timestamp: float = field(default_factory=time)

class AgentState:
    """
    Stan agenta zaimplementowany jako słownik z dodatkową funkcjonalnością.
    """
    def __init__(self, **kwargs):
        self._state = {
            "transcript": "",
            "notes": "",
            "feedback": "",
            "target_language": "polski",
            "note_type": "summary",
            "status": "started",
            "decision": "",
            "messages": [],
            "memory": {}
        }
        self._state.update(kwargs)

    def __getitem__(self, key):
        return self._state[key]

    def __setitem__(self, key, value):
        self._state[key] = value

    def get(self, key, default=None):
        return self._state.get(key, default)

    def add_message(self, from_agent: str, to_agent: str, content: Dict[str, Any]):
        """Dodaje nową wiadomość do historii komunikacji"""
        if "messages" not in self._state:
            self._state["messages"] = []
        
        self._state["messages"].append({
            "from_agent": from_agent,
            "to_agent": to_agent,
            "content": content,
            "timestamp": time()
        })

    def get_messages_for(self, agent_name: str) -> List[Dict]:
        """Zwraca wszystkie wiadomości dla danego agenta"""
        return [
            msg for msg in self._state.get("messages", [])
            if msg["to_agent"] == agent_name
        ]

    def update_memory(self, agent_name: str, key: str, value: Any):
        """Aktualizuje pamięć agenta"""
        if "memory" not in self._state:
            self._state["memory"] = {}
        if agent_name not in self._state["memory"]:
            self._state["memory"][agent_name] = {}
        self._state["memory"][agent_name][key] = value

    def get_memory(self, agent_name: str, key: str) -> Any:
        """Pobiera wartość z pamięci agenta"""
        return self._state.get("memory", {}).get(agent_name, {}).get(key)

    def to_dict(self) -> Dict:
        """Zwraca stan jako słownik"""
        return self._state

    def update(self, other: Dict):
        """Aktualizuje stan na podstawie innego słownika"""
        self._state.update(other) 