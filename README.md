# Keydash
An open-source, decentralized version of Typeracer coded in Python. Currently just offline.
# Contributors
Started on July 30th, 2025 by C0m3b4ck. Right now, there are no other contributors.
# Requirements
Is coded to support Windows and Linux, tested on Ubuntu Linux.
Tested on Python 3.13, required libraries in requirements.txt
# Controls
* Sentence Selection:
    Upon launching the program, you will be presented with a list of predefined sentences and an option to select a random sentence.      Enter the corresponding number and press Enter to choose.

* Starting the Game:
    After selecting the sentence, press Enter when you are ready to start typing.

* Typing:
    Type the sentence shown on the screen. The next character to type is highlighted with cyan color and underline.

* Backspace:
    Use the Backspace key to delete the previous character and correct mistakes.

* Error Handling:
    If you type an incorrect character, typing will pause and display a message about the typo. You must type the correct letter to proceed.

* Finishing:
    After completing the sentence correctly, your typing statistics will be displayed, and your score will be saved.

* Menu:
At the beginning of the script and after competing a game:

        * Play again (shows the sentence selection)

        * View performance graph (using pyplotlib, press C or c in the graph window to close it)

        * Exit the program (closes the program)

# Features

* Offline Typing Test:
    No internet connection required; runs entirely in the console.

* Sentence Selection:
    Choose from 10 predefined sentences or let the program generate one randomly.

* Per-Character Highlighting:
    The current letter to type is highlighted using colored text and underlining to improve focus.

* Precise Timing:
    Measures time taken per individual keystroke, total typing time, calculates words per minute (WPM) and time between keypresses.

* Accuracy Calculation:
    Compares your input against the original sentence, computing character-level accuracy.

* Backspace Support:
    Allows correction of mistakes before finalizing input.

* Anti-Cheat Detection:
    Flags suspiciously consistent and rapid keypress patterns indicative of macros or automated input. If cheats are detected, stats from that session are cleared

* Error Blocking:
    Prevents progressing past a mistyped character until corrected, encouraging accurate typing.

* Score Persistence:
    Saves each test's detailed stats to timestamped files in a dedicated stats folder.

* Cumulative Stats Tracking:
    Maintains a stats.txt log with all session data, excluding flagged cheating attempts. Used to show stat graphs for the user.

* Performance Visualization:
    Displays graphs of WPM, accuracy, total time, and average time between letters over all previous sessions using matplotlib.

* Graph Interaction:
    Close performance graphs by pressing C or c.

# Roadmap

* Polish offline anticheat (will release test cheat client archival versions)
* Peer-to-peer games (between to players, who are both the server and the client, scores compare between them) - potential problem would be modifying packets to spoof scores (cheat modifies data in packet before sending it to other player)
* Ability to host Keydash servers - hosts will be able to manage MOTD, player whitelist, custom sentences, custom server-side anticheat



