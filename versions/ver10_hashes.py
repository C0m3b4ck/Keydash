import time
import datetime
import os
import sys
import random
import statistics
import hashlib
import hmac

import matplotlib.pyplot as plt

# Secret key used for HMAC signing of stats files
# (In open source, this only raises the bar slightly; change or remove for full transparency)
SECRET_KEY = b"change_this_to_random_secret_key"


# Cross-platform getch: Windows and Unix
if os.name == 'nt':
    import msvcrt

    def getch():
        ch = msvcrt.getwch()
        if ch == '\x00' or ch == '\xe0':  # Special keys
            msvcrt.getwch()  # consume next char
            return ''
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


def detect_machine_input(time_stamps):
    MIN_TIME_THRESHOLD = 0.03  # 30ms minimum between keystrokes suspiciously fast
    MAX_STD_THRESHOLD = 0.005  # very low std dev = very consistent timing

    if not time_stamps:
        return False

    min_time = min(time_stamps)
    std_dev = statistics.stdev(time_stamps) if len(time_stamps) > 1 else 0

    return min_time < MIN_TIME_THRESHOLD and std_dev < MAX_STD_THRESHOLD


def compute_hmac(lines):
    """
    Compute HMAC-SHA256 over concatenated lines, return hex digest string.
    """
    message = "\n".join(lines).encode('utf-8')
    return hmac.new(SECRET_KEY, message, hashlib.sha256).hexdigest()


def save_score(wpm, accuracy, time_between_letters, sentence, is_cheating):
    # Ensure stats folder exists
    stats_folder = "stats"
    os.makedirs(stats_folder, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    score_filename = os.path.join(stats_folder, f"stats{timestamp}.txt")
    stats_filename = os.path.join(stats_folder, "stats.txt")

    if is_cheating:
        cheat_string = f"{wpm:.2f}{accuracy:.2f}{timestamp}"
        cheat_hash = hashlib.sha256(cheat_string.encode('utf-8')).hexdigest()
        cheat_content = (
            f"CHEAT DETECTED\n"
            f"Hash: {cheat_hash}\n"
            "This session's stats are invalid due to detected macro or automated input.\n"
            "HMAC: INVALID\n"
        )
        with open(score_filename, "w", encoding='utf-8') as f:
            f.write(cheat_content)
        print(f"Cheating detected! Invalid stats saved to {score_filename}")

        with open(stats_filename, "a", encoding='utf-8') as sf:
            sf.write(f"{timestamp}, CHEAT DETECTED, WPM: 0.00, Time: 0.00s, Accuracy: 0.00%, AvgTimeBetweenLetters: 0.000s\n")

    else:
        avg_time = sum(time_between_letters) / len(time_between_letters) if time_between_letters else 0.0
        # Prepare lines to write and sign
        lines_to_sign = [
            f"WPM: {wpm:.2f}",
            f"Accuracy: {accuracy:.2f}%",
            f"Timestamp: {timestamp}",
            f"Avg Time Between Letters: {avg_time:.3f} sec",
            f"Sentence: {sentence}"
        ]

        # Write detailed stat file with sentence and HMAC
        with open(score_filename, "w", encoding='utf-8') as f:
            for line in lines_to_sign:
                f.write(line + "\n")
            # Write timings line
            if time_between_letters:
                f.write("Time Between Letters (s): " + ", ".join(f"{t:.3f}" for t in time_between_letters) + "\n")
            # Write HMAC line
            hmac_value = compute_hmac(lines_to_sign)
            f.write(f"HMAC: {hmac_value}\n")
        print(f"Score saved to {score_filename}")

        # Append minimal aggregate stats (WITHOUT sentence) to cumulative stats.txt
        elapsed_global = elapsed if 'elapsed' in globals() else 0.0
        with open(stats_filename, "a", encoding='utf-8') as sf:
            sf.write(f"{timestamp}, WPM: {wpm:.2f}, Time: {elapsed_global:.2f}s, Accuracy: {accuracy:.2f}%, AvgTimeBetweenLetters: {avg_time:.3f}s\n")


class Colors:
    RED = "\033[31m"
    GREEN = "\033[32m"
    CYAN = "\033[36m"
    RESET = "\033[0m"
    UNDERLINE = "\033[4m"


def print_with_highlight(original_text, current_index):
    print("\r", end="")
    for i, c in enumerate(original_text):
        if i == current_index:
            print(f"{Colors.CYAN}{Colors.UNDERLINE}{c}{Colors.RESET}", end="")
        else:
            print(c, end="")
    print("  ", end="", flush=True)


def verify_hmac(filepath):
    """
    Verify that the HMAC line in stats[timestamp].txt matches the content.
    Returns True if valid or not cheat file, False if tampered or missing.
    """
    try:
        with open(filepath, "r", encoding='utf-8') as f:
            lines = f.read().splitlines()
        # Extract lines except HMAC line and cheat lines
        # Locate HMAC line
        hmac_line = None
        for line in reversed(lines):
            if line.startswith("HMAC: "):
                hmac_line = line
                break

        if hmac_line is None:
            return False  # No HMAC line means invalid

        hmac_value = hmac_line[len("HMAC: "):].strip()
        if hmac_value == "INVALID":
            return False  # invalid cheat file

        # Collect lines for signing (those that the HMAC covers)
        # We signed all lines before the HMAC line
        idx = lines.index(hmac_line)
        lines_to_verify = lines[:idx]

        calc_hmac = compute_hmac(lines_to_verify)
        return hmac.compare_digest(calc_hmac, hmac_value)
    except Exception:
        return False


def plot_stats():
    stats_folder = "stats"
    stats_filename = os.path.join(stats_folder, "stats.txt")
    if not os.path.isfile(stats_filename):
        print("No stats file found. Please complete at least one typing test first.")
        return

    # To get timestamps with verified correct individual stat files:
    verified_timestamps = []
    with os.scandir(stats_folder) as it:
        for entry in it:
            if entry.is_file() and entry.name.startswith("stats") and entry.name.endswith(".txt"):
                if entry.name == "stats.txt":
                    continue  # skip cumulative file
                fullpath = os.path.join(stats_folder, entry.name)
                if verify_hmac(fullpath):
                    timestamp_part = entry.name[len("stats"):-len(".txt")]
                    verified_timestamps.append(timestamp_part)
                else:
                    # Tampered or cheat file ignored in graph
                    continue

    timestamps, wpms, times_, accuracies, avg_times_btwn_letters = [], [], [], [], []

    with open(stats_filename, "r", encoding='utf-8') as sf:
        for line in sf:
            parts = line.strip().split(", ")
            if len(parts) < 5:
                continue
            if "CHEAT DETECTED" in parts[1]:
                continue
            timestamps.append(parts[0])
            try:
                wpm = float(parts[1].split(": ")[1])
                t = float(parts[2].split(": ")[1].replace('s', ''))
                acc = float(parts[3].split(": ")[1].replace('%', ''))
                avg_t = float(parts[4].split(": ")[1].replace('s', ''))
            except (IndexError, ValueError):
                continue
            wpms.append(wpm)
            times_.append(t)
            accuracies.append(acc)
            avg_times_btwn_letters.append(avg_t)

    if not wpms:
        print("No valid stats data found to plot.")
        return

    x_vals = list(range(1, len(wpms)+1))

    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    axs[0, 0].plot(x_vals, wpms, marker="o", color="blue")
    axs[0, 0].set_title("WPM over Runs")
    axs[0, 0].set_xlabel("Run Number")
    axs[0, 0].set_ylabel("WPM")

    axs[0, 1].plot(x_vals, accuracies, marker="o", color="green")
    axs[0, 1].set_title("Accuracy (%) over Runs")
    axs[0, 1].set_xlabel("Run Number")
    axs[0, 1].set_ylabel("Accuracy (%)")

    axs[1, 0].plot(x_vals, times_, marker="o", color="red")
    axs[1, 0].set_title("Time Taken (seconds) over Runs")
    axs[1, 0].set_xlabel("Run Number")
    axs[1, 0].set_ylabel("Time (s)")

    axs[1, 1].plot(x_vals, avg_times_btwn_letters, marker="o", color="purple")
    axs[1, 1].set_title("Avg Time Between Letters (seconds) over Runs")
    axs[1, 1].set_xlabel("Run Number")
    axs[1, 1].set_ylabel("Avg Time Between Letters (s)")

    plt.tight_layout()

    def on_key(event):
        if event.key.lower() == "c":
            plt.close(event.canvas.figure)

    fig.canvas.mpl_connect("key_press_event", on_key)
    plt.show()


def keydash():
    global elapsed  # For access in save_score
    while True:
        print("Welcome to Offline KeyDash with Letter Highlighting and Stats!\n")
        text = get_text()
        print("\nType the following text as fast and accurately as you can:\n")
        print(text)
        print("\nPress Enter when ready to start...")
        while True:
            ch = getch()
            if ch in ("\r", "\n"):
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
            if ch in ("\b", "\x7f"):
                if typed:
                    typed.pop()
                    current_index -= 1
                    print_with_highlight(text, current_index)
                continue

            if ch == "":
                continue

            expected_char = text[current_index]
            if ch != expected_char:
                print(f"\n{Colors.RED}Incorrect letter '{ch}'. Please type '{expected_char}'.{Colors.RESET}")
                continue

            typed.append(ch)
            now = time.time()
            time_stamps.append(now - last_time)
            last_time = now

            current_index += 1
            print_with_highlight(text, current_index)

        end = time.time()
        elapsed = end - start
        typed_str = "".join(typed)
        wpm = calculate_wpm(len(typed_str), elapsed)
        accuracy = calculate_accuracy(text, typed_str)
        avg_time_between_letters = sum(time_stamps) / len(time_stamps) if time_stamps else 0

        is_cheating = detect_machine_input(time_stamps)
        if is_cheating:
            print(
                f"\n{Colors.RED}[Anti-Cheat] Warning: Detected unnaturally consistent and rapid keypresses."
            )
            print("This may indicate use of automated input or macros.{Colors.RESET}\n")

        print("\n\n--- Results ---")
        print(f"Time taken: {elapsed:.2f} seconds")
        print(f"WPM: {wpm:.2f}")
        print(f"Accuracy: {accuracy:.2f}%")
        print(f"Average time between letters: {avg_time_between_letters:.3f} seconds")
        print("Time between letters (seconds):")
        print(", ".join(f"{t:.3f}" for t in time_stamps))

        save_score(wpm, accuracy, time_stamps, sentence=text, is_cheating=is_cheating)

        print("\nWhat would you like to do next?")
        print("1. Play again")
        print("2. View performance graph")
        print("3. Exit")

        while True:
            choice = input("Enter choice (1-3): ").strip()
            if choice == "1":
                print("\nStarting new game...\n")
                break
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
