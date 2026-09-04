import sys
from agent import run_agent

def main():
    print("[🤖]: 你好呀！我是你的智能助手，你可以向我询问天气或者新闻～")
    while True:
        try:
            line = input("[你]: ").strip()
        except (EOFError, KeyboardInterrupt):   # Ctrl-D / Ctrl-C
            print("[🤖]: 再见!\n")
            sys.exit(0)
        if not line:
            continue
        if line.lower() in ("quit", "exit", "q"):
            print("[🤖]: 再见!\n")
            break

        print(f"[🤖]: 思考中...请稍候")
        msg = run_agent(line)
        print(f"[🤖]: {msg}\n")

if __name__ == "__main__":
    main()
