from  import voice

def main():
    recognizer = voice()
    recognizer.recognize(duration=10)

if __name__ == "__main__":
    main()