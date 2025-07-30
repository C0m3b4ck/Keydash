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
SECRET_KEY = b"change_this_to_random_secret_key"

STATS_FOLDER = "stats"

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


def verify_hmac(filepath):
    """
    Verify that the HMAC line in stats[timestamp].txt matches the content.
    Returns True if valid or not cheat file, False if tampered or missing.
    """
    try:
        with open(filepath, "r", encoding='utf-8') as f:
            lines = f.read().splitlines()
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

        idx = lines.index(hmac_line)
        lines_to_verify = lines[:idx]

        calc_hmac = compute_hmac(lines_to_verify)
        return hmac.compare_digest(calc_hmac, hmac_value)
    except Exception:
        return False


def rebuild_cumulative_stats():
    """
    Scans individual stat files in the stats folder, verifies HMAC,
    and writes a fresh cumulative stats.txt including only valid entries.
    """
    os.makedirs(STATS_FOLDER, exist_ok=True)
    stats_filename = os.path.join(STATS_FOLDER, "stats.txt")

    valid_entries = []

    for entry in os.listdir(STATS_FOLDER):
        if entry.startswith("stats") and entry.endswith(".txt") and entry != "stats.txt":
            full_path = os.path.join(STATS_FOLDER, entry)
            if verify_hmac(full_path):
                try:
                    with open(full_path, "r", encoding='utf-8') as f:
                        lines = f.read().splitlines()
                    # Extract minimal aggregate info (timestamp, wpm, time, acc, avg_time)
                    # i.e. lines start like:
                    # WPM: xx.xx
                    # Accuracy: xx.xx%
                    # Timestamp: yyyymmdd_hhmmss
                    # Avg Time Between Letters: xx.xxx sec
                    # Extract these details to rebuild aggregate line:
                    wpm_line = next((l for l in lines if l.startswith("WPM: ")), None)
                    acc_line = next((l for l in lines if l.startswith("Accuracy: ")), None)
                    ts_line = next((l for l in lines if l.startswith("Timestamp: ")), None)
                    avg_time_line = next((l for l in lines if l.startswith("Avg Time Between Letters: ")), None)
                    if None in (wpm_line, acc_line, ts_line, avg_time_line):
                        continue

                    timestamp = ts_line[len("Timestamp: "):].strip()
                    wpm = float(wpm_line[len("WPM: "):].strip())
                    acc = float(acc_line[len("Accuracy: "):-1].strip())  # strip % sign
                    avg_time_sec = float(avg_time_line[len("Avg Time Between Letters: "):-4].strip())  # strip " sec"
                    # Here we don't track elapsed time per file, so put 0.0 or skip or parse time between letters total maybe
                    # For now, time = 0.0 in aggregate for simplicity
                    valid_entries.append(f"{timestamp}, WPM: {wpm:.2f}, Time: 0.00s, Accuracy: {acc:.2f}%, AvgTimeBetweenLetters: {avg_time_sec:.3f}s")
                except Exception:
                    pass

    # Write fresh cumulative stats.txt
    with open(stats_filename, "w", encoding='utf-8') as sf:
        for entry in sorted(valid_entries):
            sf.write(entry + "\n")


def save_score(wpm, accuracy, time_between_letters, sentence, is_cheating):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(STATS_FOLDER, exist_ok=True)
    score_filename = os.path.join(STATS_FOLDER, f"stats{timestamp}.txt")

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
    else:
        avg_time = sum(time_between_letters) / len(time_between_letters) if time_between_letters else 0.0
        lines_to_sign = [
            f"WPM: {wpm:.2f}",
            f"Accuracy: {accuracy:.2f}%",
            f"Timestamp: {timestamp}",
            f"Avg Time Between Letters: {avg_time:.3f} sec",
            f"Sentence: {sentence}"
        ]
        with open(score_filename, "w", encoding='utf-8') as f:
            for line in lines_to_sign:
                f.write(line + "\n")
            if time_between_letters:
                f.write("Time Between Letters (s): " + ", ".join(f"{t:.3f}" for t in time_between_letters) + "\n")
            hmac_value = compute_hmac(lines_to_sign)
            f.write(f"HMAC: {hmac_value}\n")
        print(f"Score saved to {score_filename}")

    # Now rebuild cumulative stats.txt from all valid files
    rebuild_cumulative_stats()


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


def plot_stats():
    stats_filename = os.path.join(STATS_FOLDER, "stats.txt")
    if not os.path.isfile(stats_filename):
        print("No stats file found. Please complete at least one typing test first.")
        return

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
                t = float(parts[2].split(": ")[1].replace("s", ""))
                acc = float(parts[3].split(": ")[1].replace("%", ""))
                avg_t = float(parts[4].split(": ")[1].replace("s", ""))
            except (IndexError, ValueError):
                continue
            wpms.append(wpm)
            times_.append(t)
            accuracies.append(acc)
            avg_times_btwn_letters.append(avg_t)

    if not wpms:
        print("No valid stats data found to plot.")
        return

    x_vals = list(range(1, len(wpms) + 1))

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


def typing_test():
    global elapsed  # For access in save_score
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


def main_menu():
    while True:
        print("\nKeyDash Main Menu:")
        print("1. Start Typing Test")
        print("2. View Performance Stats")
        print("3. Exit")

        choice = input("Enter option (1-3): ").strip()
        if choice == "1":
            typing_test()
        elif choice == "2":
            rebuild_cumulative_stats()  # Refresh stats file from verified individual stats
            plot_stats()
        elif choice == "3":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid option, please enter 1, 2, or 3.")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nTyping test interrupted.")
