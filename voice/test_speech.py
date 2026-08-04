from __future__ import annotations

# Simple test to verify whether Windows speech can speak at all.

def main() -> None:
    try:
        import win32com.client

        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Speak("Hello. This is a voice test.")
        print("Speech test completed.")
    except Exception as exc:
        print(f"Speech test failed: {exc}")


if __name__ == "__main__":
    main()