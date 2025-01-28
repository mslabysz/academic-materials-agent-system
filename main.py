import os
from dotenv import load_dotenv
from ui import build_interface

def main():
    load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

    demo = build_interface()
    demo.launch()

if __name__ == "__main__":
    main()
