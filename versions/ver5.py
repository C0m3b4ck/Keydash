import time
import datetime
import os
import sys
import random

import matplotlib.pyplot as plt

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
        "Practice makes perfect in typing speed games.",
        "OpenAI develops powerful AI models.",
        "Consistency is key to mastery.",
        "Always challenge yourself to improve.",
        "Debugging is twice as hard as writing code.",
        "A journey of a thousand miles begins with a single step."
    ]
    print("Choose a sentence to type:")
    for i, sentence in enumerate(texts, 1):
        print(f"{i}. {sentence}")
    print(f"{len(texts)+1}. Random sentence")

    while True:
        choice = input(f"Enter choice (1-{len(texts)+1}): ").strip()
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(texts):
                return texts[choice_num - 1]
            elif choice_num == len(texts) + 1:
                return random.choice(texts)
        print("Invalid choice. Please try again.")

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
    score_filename = f"score{timestamp}.txt"
    stats_filename = "stats.txt"
    
    # Save individual score file
    with open(score_filename, "w") as f:
        f.write(f"WPM: {wpm:.2f}\n")
        f.write(f"Accuracy: {accuracy:.2f}%\n")
        f.write(f"Timestamp: {timestamp}\n")
        if time_between_letters:
            avg_time = sum(time_between_letters) / len(time_between_letters)
            f.write(f"Avg Time Between Letters: {avg_time:.3f} sec\n")
            f.write("Time Between Letters (s): " + ", ".join(f"{t:.3f}" for t in time_between_letters) + "\n")
    print(f"Score saved to {score_filename}")

    # Append data to cumulative stats file
    avg_time = sum(time_between_letters) / len(time_between_letters) if time_between_letters else 0
    with open(stats_filename, "a") as sf:
        sf.write(f"{timestamp}, WPM: {wpm:.2f}, Time: {elapsed:.2f}s, Accuracy: {accuracy:.2f}%, AvgTimeBetweenLetters: {avg_time:.3f}s\n")

# ANSI color codes for color highlighting in terminal
class Colors:
    RED = "\033[31m"
    GREEN = "\033[32m"
    CYAN = "\033[36m"
    RESET = "\033[0m"
    UNDERLINE = "\033[4m"

def print_with_highlight(original_text, current_index):
    # Clear the line before printing
    print("\r", end="")
    for i, c in enumerate(original_text):
        if i == current_index:
            # Highlight current letter with cyan color and underline
            print(f"{Colors.CYAN}{Colors.UNDERLINE}{c}{Colors.RESET}", end="")
        else:
            print(c, end="")
    print("  ", end="", flush=True)  # padding to clear leftovers

def plot_stats():
    stats_filename = "stats.txt"
    if not os.path.isfile(stats_filename):
        print("No stats file found. Please complete at least one typing test first.")
        return
    
    timestamps = []
    wpms = []
    times = []
    accuracies = []
    avg_times_btwn_letters = []

    with open(stats_filename, "r") as sf:
        for line in sf:
            # Expected format:
            # timestamp, WPM: xx.xx, Time: xx.xx s, Accuracy: xx.xx %, AvgTimeBetweenLetters: xx.xxx s
            parts = line.strip().split(", ")
            if len(parts) < 5:
                continue
            timestamps.append(parts[0])
            try:
                wpm = float(parts[1].split(": ")[1])
                t = float(parts[2].split(": ")[1].replace('s',''))
                acc = float(parts[3].split(": ")[1].replace('%',''))
                avg_t = float(parts[4].split(": ")[1].replace('s',''))
            except (IndexError, ValueError):
                continue
            wpms.append(wpm)
            times.append(t)
            accuracies.append(acc)
            avg_times_btwn_letters.append(avg_t)

    if not wpms:
        print("No valid stats data found to plot.")
        return

    x_vals = list(range(1, len(wpms)+1))

    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    axs[0, 0].plot(x_vals, wpms, marker='o', color='blue')
    axs[0, 0].set_title('WPM over Runs')
    axs[0, 0].set_xlabel('Run Number')
    axs[0, 0].set_ylabel('WPM')

    axs[0, 1].plot(x_vals, accuracies, marker='o', color='green')
    axs[0, 1].set_title('Accuracy (%) over Runs')
    axs[0, 1].set_xlabel('Run Number')
    axs[0, 1].set_ylabel('Accuracy (%)')

    axs[1, 0].plot(x_vals, times, marker='o', color='red')
    axs[1, 0].set_title('Time Taken (seconds) over Runs')
    axs[1, 0].set_xlabel('Run Number')
    axs[1, 0].set_ylabel('Time (s)')

    axs[1, 1].plot(x_vals, avg_times_btwn_letters, marker='o', color='purple')
    axs[1, 1].set_title('Avg Time Between Letters (seconds) over Runs')
    axs[1, 1].set_xlabel('Run Number')
    axs[1, 1].set_ylabel('Avg Time Between Letters (s)')

    plt.tight_layout()

    # Add event to close graph when 'c' or 'C' pressed
    def on_key(event):
        if event.key.lower() == 'c':
            plt.close(event.canvas.figure)
            print("C pressed. Closing graph...")

    fig.canvas.mpl_connect('key_press_event', on_key)
    plt.show()

def keydash():
    global elapsed  # To make accessible by save_score
    while True:
        print("Welcome to KeyDash with Letter Highlighting and Stats!\n")
        text = get_text()
        print("\nType the following text as fast and accurately as you can:\n")
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

        # Ask if user wants to play again or see stats graph
        print("\nWhat would you like to do next?")
        print("1. Play again")
        print("2. View performance graph")
        print("3. Exit")

        while True:
            choice = input("Enter choice (1-3): ").strip()
            if choice == "1":
                print("\nStarting new game...\n")
                break  # loop again to play
            elif choice == "2":
                print("\nLoading performance graph...\n")
                plot_stats()
                print("\nWhat would you like to do next?")
                print("1. Play again")
                print("2. View performance graph")
                print("3. Exit")
            elif choice == "3":
                print("Goodbye!")
                return
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    try:
        keydash()
    except KeyboardInterrupt:
        print("\nTyping test interrupted.")
