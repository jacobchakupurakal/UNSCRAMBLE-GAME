import random
import time
import tkinter as tk

MAX_TIME = 30
leaderboard_file = "leaderboard.txt"
word_file = "words.txt"


def load_words():
    try:
        with open(word_file, "r") as file:
            return [word.strip().lower() for word in file if word.strip()]
    except:
        print(f"Could not read '{word_file}'.")
        return []


def load_leaderboard():
    scores = {}
    try:
        with open(leaderboard_file, "r") as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    name, score = parts
                    scores[name] = float(score)
    except:
        pass
    return scores


def save_leaderboard(scores):
    with open(leaderboard_file, "w") as file:
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        for name, score in sorted_scores:
            file.write(f"{name},{score}\n")


def show_leaderboard(scores):
    leaderboard_text.delete('1.0', tk.END)
    leaderboard_text.insert(tk.END, "Final Leaderboard:\n")
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    position = 1
    for name, score in sorted_scores:
        leaderboard_text.insert(tk.END, f"{position} {name} - {score} point(s)\n")
        position += 1


def play_multiplayer_game():
    global all_words, players, scores, current_round, total_rounds, current_player_idx, current_word, start_time

    all_words = load_words()
    if not all_words:
        leaderboard_text.insert(tk.END, "No words loaded. Exiting game.\n")
        return

    scores = {}
    try:
        num_players = int(num_players_entry.get())
        if num_players <= 0:
            leaderboard_text.insert(tk.END, "Invalid number of players.\n")
            return
    except ValueError:
        leaderboard_text.insert(tk.END, "Invalid number of players.\n")
        return

    players.clear()
    if len(player_entries) < num_players:
        leaderboard_text.insert(tk.END, "Please enter all player names first.\n")
        return

    for i in range(num_players):
        name = player_entries[i].get().strip()
        if not name:
            leaderboard_text.insert(tk.END, f"Player {i+1} name is missing.\n")
            return
        players.append(name)
        scores[name] = 0.0

    try:
        total_rounds = int(rounds_entry.get())
    except:
        leaderboard_text.insert(tk.END, "Invalid number of rounds.\n")
        return

    current_round = 1
    current_player_idx = 0
    leaderboard_text.delete('1.0', tk.END)
    game_frame.pack()
    next_turn()


def next_turn():
    global current_word, start_time, current_player_idx, current_round

    if current_player_idx >= len(players):
        current_player_idx = 0
        current_round += 1

    if current_round > total_rounds:
        save_leaderboard(scores)
        show_leaderboard(scores)
        game_frame.pack_forget()
        return

    player = players[current_player_idx]
    word = random.choice(all_words)
    shuffled = list(word)
    attempts = 0
    while True:
        random.shuffle(shuffled)
        if ''.join(shuffled) != word or attempts >= 5:
            break
        attempts += 1

    current_word = word
    word_label.config(text=f"{player}'s Turn: Unscramble → {''.join(shuffled)}")
    guess_entry.delete(0, tk.END)
    start_time = time.time()


def submit_guess():
    global current_player_idx

    guess = guess_entry.get().strip().lower()
    elapsed = time.time() - start_time
    player = players[current_player_idx]

    if elapsed > MAX_TIME:
        leaderboard_text.insert(tk.END, f"{player} took {round(elapsed, 2)}s. Time's up! No points.\n")
    elif guess == current_word:
        points = max(30 - round(elapsed), 1)
        scores[player] += points
        leaderboard_text.insert(tk.END, f"{player} guessed correctly in {round(elapsed, 2)}s! +{points} points.\n")
    else:
        leaderboard_text.insert(tk.END, f"{player} guessed wrong. Word was: {current_word}\n")

    current_player_idx += 1
    next_turn()


root = tk.Tk()
root.title("Word Game")
root.configure(bg="#1e1e1e")

style_settings = {
    "bg": "#1e1e1e",
    "fg": "#f0f0f0",
    "font": ("Helvetica", 12),
    "padx": 10,
    "pady": 5,
}

# Main frame (everything except leaderboard)
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Bottom frame (for leaderboard only)
bottom_frame = tk.Frame(root)
bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)

# Global variables
player_entries = []
players = []
scores = {}
all_words = []
current_round = 1
total_rounds = 1
current_player_idx = 0
current_word = ""
start_time = 0


def show_player_name_entry(index=0):
    if index >= expected_num_players:
        # All names entered, show rounds entry
        rounds_label.pack()
        rounds_entry.pack()
        start_button.pack()
        return

    label = tk.Label(player_frame, text=f"Player {index+1} name:")
    label.pack()
    entry = tk.Entry(player_frame)
    entry.pack()
    player_entries.append(entry)

    def on_return(event):
        if entry.get().strip() == "":
            leaderboard_text.insert(tk.END, "Please enter a name before continuing.\n")
            return
        show_player_name_entry(index + 1)

    entry.bind("<Return>", on_return)
    entry.focus_set()


def proceed_to_names():
    global expected_num_players

    try:
        expected_num_players = int(num_players_entry.get())
        if expected_num_players <= 0 or expected_num_players > 10:
            raise ValueError
    except ValueError:
        leaderboard_text.insert(tk.END, "Invalid number of players.\n")
        return

    num_players_label.pack_forget()
    num_players_entry.pack_forget()
    num_players_button.pack_forget()

    show_player_name_entry(0)


num_players_label = tk.Label(main_frame, text="Enter number of players:", **style_settings)
num_players_label.pack()

num_players_entry = tk.Entry(main_frame, font=("Helvetica", 12), width=30)
num_players_entry.pack(pady=5)
num_players_entry.bind("<Return>", lambda event: proceed_to_names())

num_players_button = tk.Button(
    main_frame, text="Next", command=proceed_to_names,
    bg="#4CAF50", fg="white", font=("Helvetica", 12), padx=10, pady=5
)
num_players_button.pack(pady=10)

# Step 2: Player Names
player_frame = tk.Frame(main_frame)
player_frame.pack()

# Step 3: Rounds & Start
rounds_label = tk.Label(main_frame, text="Enter number of rounds:")
rounds_entry = tk.Entry(main_frame)
rounds_entry.bind("<Return>", lambda event: play_multiplayer_game())

start_button = tk.Button(main_frame, text="Start Game", command=play_multiplayer_game)

# Game Area
game_frame = tk.Frame(main_frame)
word_label = tk.Label(game_frame, text="", font=('Arial', 14))
word_label.pack()
guess_entry = tk.Entry(game_frame)
guess_entry.pack()
guess_entry.bind("<Return>", lambda event: submit_guess())
submit_button = tk.Button(game_frame, text="Submit Guess", command=submit_guess)
submit_button.pack()

leaderboard_text = tk.Text(bottom_frame, height=10, bg="#121212", fg="lime", font=("Courier", 11))
leaderboard_text.pack(fill=tk.X, padx=10, pady=5)

root.mainloop()
