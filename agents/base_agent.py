from openai import OpenAI

class BaseAgent:
    def __init__(self, name: str, model_name: str = "gpt-4"):
        self.name = name
        self.model_name = model_name
        self.client = OpenAI() if model_name else None

    def __call__(self, state: dict) -> dict:
        """Wrapper dla procesu przetwarzania"""
        print(f"\n[{self.name}] Rozpoczynam przetwarzanie...")
        
        # Sprawdź wiadomości
        messages = state.get("messages", [])
        messages_for_me = [
            msg for msg in messages 
            if msg.get("to_agent") == self.name
        ]
        
        if messages_for_me:
            print(f"[{self.name}] Otrzymano {len(messages_for_me)} nowych wiadomości")
            for msg in messages_for_me:
                print(f"[{self.name}] Wiadomość od {msg['from_agent']}: {msg['content']}")

        # Wykonaj główną logikę
        state = self.process(state)

        print(f"[{self.name}] Zakończono przetwarzanie")
        return state

    def process(self, state: dict) -> dict:
        """Domyślna implementacja procesu - do nadpisania w klasach pochodnych"""
        return state

    def send_message(self, state: dict, to_agent: str, content: dict) -> dict:
        """Wysyła wiadomość do innego agenta"""
        if "messages" not in state:
            state["messages"] = []
            
        state["messages"].append({
            "from_agent": self.name,
            "to_agent": to_agent,
            "content": content
        })
        
        print(f"[{self.name}] Wysłano wiadomość do {to_agent}: {content}")
        return state 