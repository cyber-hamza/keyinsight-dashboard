import tkinter as tk
from tkinter import ttk
import sqlite3
from collections import Counter
from datetime import datetime
import time
import matplotlib.pyplot as plt

# ---------------- DATABASE ----------------
conn = sqlite3.connect("keys.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT,
    key TEXT
)
""")
conn.commit()

# ---------------- DATA ----------------
counter = Counter()
running = False
start_time = time.time()

# ---------------- COLORS (UI STYLE) ----------------
BG = "#0d1117"
FG = "#00ff9f"
BTN_BG = "#161b22"

# ---------------- CHART ----------------
def show_chart():
    if not counter:
        return

    keys = list(counter.keys())
    values = list(counter.values())

    plt.figure(figsize=(8, 4))
    plt.bar(keys, values, color="#00ff9f")

    plt.title("Keyboard Usage Analytics")
    plt.xlabel("Keys")
    plt.ylabel("Count")

    plt.tight_layout()
    plt.show()

# ---------------- DATABASE SAFE WRITE ----------------
def save_to_db(key):
    conn_local = sqlite3.connect("keys.db")
    cursor_local = conn_local.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor_local.execute(
        "INSERT INTO logs (time, key) VALUES (?, ?)",
        (now, key)
    )

    conn_local.commit()
    conn_local.close()

# ---------------- STATS ----------------
def update_stats():
    total = sum(counter.values())
    elapsed = time.time() - start_time
    kps = total / elapsed if elapsed > 0 else 0

    stats_label.config(text=f"Total: {total} | KPS: {kps:.2f}")

# ---------------- TABLE ----------------
def refresh_table():
    tree.delete(*tree.get_children())

    conn_local = sqlite3.connect("keys.db")
    cursor_local = conn_local.cursor()

    cursor_local.execute("SELECT time, key FROM logs ORDER BY id DESC LIMIT 50")
    rows = cursor_local.fetchall()

    conn_local.close()

    for r in rows:
        tree.insert("", "end", values=r)

# ---------------- KEY HANDLER ----------------
def on_press(key):
    global running
    if not running:
        return

    if hasattr(key, 'char') and key.char is not None:
        k = key.char
    else:
        k = str(key).replace("Key.", "")

    counter[k] += 1

    save_to_db(k)
    update_stats()
    refresh_table()

# ---------------- CONTROLS ----------------
def start():
    global running, start_time
    running = True
    start_time = time.time()
    status.config(text="RUNNING", fg=FG)

def stop():
    global running
    running = False
    status.config(text="STOPPED", fg="red")

def reset():
    counter.clear()

    conn_local = sqlite3.connect("keys.db")
    cursor_local = conn_local.cursor()
    cursor_local.execute("DELETE FROM logs")
    conn_local.commit()
    conn_local.close()

    refresh_table()
    status.config(text="RESET", fg="yellow")
    stats_label.config(text="Total: 0 | KPS: 0")

def exit_app():
    listener.stop()
    app.destroy()

# ---------------- LISTENER ----------------
from pynput import keyboard
listener = keyboard.Listener(on_press=on_press)
listener.start()

# ---------------- UI ----------------
app = tk.Tk()
app.title("Cyber Keyboard Dashboard PRO")
app.geometry("900x600")
app.configure(bg=BG)

# TITLE
title = tk.Label(
    app,
    text="KEYBOARD ANALYTICS DASHBOARD",
    bg=BG,
    fg=FG,
    font=("Consolas", 18, "bold")
)
title.pack(pady=10)

# BUTTONS FRAME
frame = tk.Frame(app, bg=BG)
frame.pack()

btn_style = {
    "bg": BTN_BG,
    "fg": FG,
    "width": 12,
    "activebackground": "#21262d"
}

tk.Button(frame, text="Start", command=start, **btn_style).grid(row=0, column=0, padx=5)
tk.Button(frame, text="Stop", command=stop, **btn_style).grid(row=0, column=1, padx=5)
tk.Button(frame, text="Reset", command=reset, **btn_style).grid(row=0, column=2, padx=5)
tk.Button(frame, text="Chart", command=show_chart, **btn_style).grid(row=0, column=3, padx=5)
tk.Button(frame, text="Exit", command=exit_app, **btn_style).grid(row=0, column=4, padx=5)

# STATUS
status = tk.Label(app, text="STOPPED", bg=BG, fg="red", font=("Consolas", 12))
status.pack(pady=5)

# STATS
stats_label = tk.Label(
    app,
    text="Total: 0 | KPS: 0",
    bg=BG,
    fg="white",
    font=("Consolas", 12)
)
stats_label.pack()

# TABLE
frame2 = tk.Frame(app)
frame2.pack(pady=10)

columns = ("Time", "Key")

tree = ttk.Treeview(frame2, columns=columns, show="headings", height=18)
tree.heading("Time", text="Time")
tree.heading("Key", text="Key")

tree.column("Time", width=250)
tree.column("Key", width=100)

tree.pack()

refresh_table()

app.mainloop()
