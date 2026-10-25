from agent.logger import setup_logging
from agent.loop import SYSTEM, MODEL, chat, trim_history

MAX_INPUT = 1000


def main():
    setup_logging()
    messages = [{"role": "system", "content": SYSTEM}]
    print(f"Power Agent ready (model: {MODEL}). Type 'exit' to quit, 'reset' to clear history.")

    while True:
        try:
            text = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if text.lower() in ("exit", "quit"):
            break
        if text.lower() == "reset":
            messages = [{"role": "system", "content": SYSTEM}]
            print("History cleared.")
            continue
        if not text:
            continue
        if len(text) > MAX_INPUT:                       # input validation
            print(f"Message too long (max {MAX_INPUT} characters).")
            continue

        messages = trim_history(messages)
        print("Agent:", chat(messages, text))


if __name__ == "__main__":
    main()