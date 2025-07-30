import time
import datetime

def get_text():
    # Example sentences to type - you can add more!
    texts = [
        "The quick brown fox jumps over the lazy dog.",
        "Python is an awesome programming language.",
        "Type as fast and accurately as you can!",
        "Artificial intelligence is the future.",
        "Practice makes perfect in typing speed games."
    ]
    # For simplicity, just pick the first text.
    # You can randomize or choose more dynamically.
    return texts[0]

def calculate_wpm(num_chars, elapsed_seconds):
    words = num_chars / 5  # Standard word length for typing tests
    minutes = elapsed_seconds / 60
    if minutes == 0:
        return 0
    return words / minutes

def calculate_accuracy(original, typed):
    correct_chars = sum(1 for o, t in zip(original, typed) if o == t)
    accuracy = (correct_chars / len(original)) * 100
    return accuracy

def save_score(wpm, accuracy):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"score{timestamp}.txt"
    with open(filename, "w") as f:
        f.write(f"WPM: {wpm:.2f}\n")
        f.write(f"Accuracy: {accuracy:.2f}%\n")
        f.write(f"Timestamp: {timestamp}\n")
    print(f"Score saved to {filename}")

def typeracer():
    print("Welcome to Offline TypeRacer!")
    text = get_text()
    print("\nType the following text as fast and accurately as you can:\n")
    print(text)
    input("Press Enter when ready to start...")

    start = time.time()
    typed = input()
    end = time.time()
    elapsed = end - start

    wpm = calculate_wpm(len(typed), elapsed)
    accuracy = calculate_accuracy(text, typed)

    print(f"\nTime: {elapsed:.2f} seconds")
    print(f"WPM: {wpm:.2f}")
    print(f"Accuracy: {accuracy:.2f}%")

    save_score(wpm, accuracy)

if __name__ == "__main__":
    typeracer()
