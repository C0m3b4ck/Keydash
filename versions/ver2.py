import time
import datetime
import os
import sys

# Cross-platform getch: Windows and Unix
if os.name == 'nt':
    import msvcrt

    def getch():
        ch = msvcrt.getwch()
        # Handle special keys returning two characters (arrow keys, etc.)
        if ch == '\x00' or ch == '\xe0':
            msvcrt.getwch()  # consume the next char
            return ''  # Ignore special keys
        return ch
else:
    import tty
    import termios

    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ord(ch) == 3:  # Ctrl-C
                raise KeyboardInterrupt
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def get_text():
    texts = [
        "The quick brown fox jumps over the lazy dog.",
        "Python is an awesome programming language.",
        "Type as fast and accurately as you can!",
        "Artificial intelligence is the future.",
        "Practice makes perfect in typing speed games."
    ]
    return texts[0]

def calculate_wpm(num_chars, elapsed_seconds):
    words = num_chars / 5  # Standard word length
    minutes = elapsed_seconds / 60
    if minutes == 0:
        return 0
    return words / minutes

def calculate_accuracy(original, typed):
    correct_chars = sum(1 for o, t in zip(original, typed) if o == t)
    accuracy = (correct_chars / len(original)) * 100
    return accuracy

def save_score(wpm, accuracy, time_between_letters):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"score{timestamp}.txt"
    with open(filename, "w") as f:
        f.write(f"WPM: {wpm:.2f}\n")
        f.write(f"Accuracy: {accuracy:.2f}%\n")
        f.write(f"Timestamp: {timestamp}\n")
        if time_between_letters:
            avg_time = sum(time_between_letters) / len(time_between_letters)
            f.write(f"Avg Time Between Letters: {avg_time:.3f} sec\n")
            f.write("Time Between Letters (s): " + ", ".join(f"{t:.3f}" for t in time_between_letters) + "\n")
    print(f"Score saved to {filename}")

def print_with_highlight(original_text, current_index):
    # Clear the line before printing
    print("\r", end="")
    for i, c in enumerate(original_text):
        if i == current_index:
            # Highlight next letter e.g. with underline or color (ANSI escape code)
            print(f"\033[4m{c}\033[0m", end="")  # Underline
        else:
            print(c, end="")
    print("  ", end="", flush=True)  # padding to clear leftovers

def typeracer():
    print("Welcome to Offline TypeRacer with Letter Highlighting!\n")
    text = get_text()
    print("Type the following text as fast and accurately as you can:\n")
    print(text)
    print("\nPress Enter when ready to start...")
    while True:
        ch = getch()
        if ch == '\r' or ch == '\n':
            break

    print("\nStart typing:\n")
    typed = []
    current_index = 0
    time_stamps = []
    start = time.time()
    last_time = start

    print_with_highlight(text, current_index)

    while current_index < len(text):
        ch = getch()

        # Handle backspace
        if ch in ('\b', '\x7f'):
            if typed:
                typed.pop()
                current_index -= 1
                print_with_highlight(text, current_index)
            continue

        # Ignore special keys
        if ch == '':
            continue

        typed.append(ch)
        now = time.time()
        time_stamps.append(now - last_time)
        last_time = now

        current_index += 1
        print_with_highlight(text, current_index)

    end = time.time()
    elapsed = end - start
    typed_str = ''.join(typed)
    wpm = calculate_wpm(len(typed_str), elapsed)
    accuracy = calculate_accuracy(text, typed_str)
    avg_time_between_letters = sum(time_stamps) / len(time_stamps) if time_stamps else 0

    print("\n\n--- Results ---")
    print(f"Time taken: {elapsed:.2f} seconds")
    print(f"WPM: {wpm:.2f}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Average time between letters: {avg_time_between_letters:.3f} seconds")
    print("Time between letters (seconds):")
    print(', '.join(f"{t:.3f}" for t in time_stamps))

    save_score(wpm, accuracy, time_stamps)

if __name__ == "__main__":
    try:
        typeracer()
    except KeyboardInterrupt:
        print("\nTyping test interrupted.")
