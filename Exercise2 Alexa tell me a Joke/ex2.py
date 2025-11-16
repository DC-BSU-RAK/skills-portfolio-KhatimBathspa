import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import random
import os
import threading
import queue
import pygame

# Initialize TTS engine
try:
    import pyttsx3
    tts_engine = pyttsx3.init()
except:
    tts_engine = None
    print("pyttsx3 not available, TTS disabled.")

# Queue for thread-safe TTS
tts_queue = queue.Queue()

# TTS worker thread
def tts_worker():
    if not tts_engine:
        return
    while True:
        text = tts_queue.get()
        if text is None:
            break
        try:
            tts_engine.say(text)
            tts_engine.runAndWait()
        except Exception as e:
            print("TTS error:", e)
        tts_queue.task_done()

threading.Thread(target=tts_worker, daemon=True).start()

def speak_text(text):
    if tts_engine:
        tts_queue.put(text)

# Paths and files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JOKES_FILE = os.path.join(BASE_DIR, "randomJokes.txt")
BG_IMAGE_FILE = os.path.join(BASE_DIR, "background.png")
AUDIO_FILE = os.path.join(BASE_DIR, "jokesaudio.mp3")

# Load jokes from file or fallback
def load_jokes():
    jokes = []
    try:
        with open(JOKES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if "?" in line:
                    try:
                        setup, punch = line.split("?", 1)
                        jokes.append((setup.strip() + "?", punch.strip()))
                    except:
                        jokes.append((line, ""))
                else:
                    jokes.append((line, ""))
    except:
        messagebox.showwarning("Missing File", "randomJokes.txt not found. Using fallback jokes.")
    if not jokes:
        jokes = [
            ("Why don't scientists trust atoms?", "Because they make up everything!"),
            ("Why did the scarecrow win an award?", "Because he was outstanding in his field!"),
            ("What do you call fake spaghetti?", "An impasta!"),
        ]
    return jokes

jokes_list = load_jokes()
current_setup = ""
current_punchline = ""

# Tkinter setup
root = tk.Tk()
root.title("Alexa Joke Assistant")
root.resizable(False, False)

# Background
if os.path.exists(BG_IMAGE_FILE):
    bg_img = Image.open(BG_IMAGE_FILE).convert("RGBA")
else:
    bg_img = Image.new("RGBA", (900, 550), (40, 40, 40, 255))

W, H = bg_img.size
root.geometry(f"{W}x{H}")

canvas = tk.Canvas(root, width=W, height=H, highlightthickness=0)
canvas.pack(fill="both", expand=True)
bg_photo = ImageTk.PhotoImage(bg_img)
canvas.create_image(0, 0, anchor="nw", image=bg_photo)

# Create transparent boxes for setup and punchline
def make_box(w, h, radius=20, alpha=180):
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0,0,w,h), radius, fill=(0,0,0,alpha))
    return img

box_w = int(W * 0.78)
box_h_setup = int(H * 0.18)
box_h_punch = int(H * 0.16)
center_x = W // 2
setup_y = int(H * 0.30)
punch_y = int(H * 0.50)

setup_box = ImageTk.PhotoImage(make_box(box_w, box_h_setup))
punch_box = ImageTk.PhotoImage(make_box(box_w, box_h_punch))

canvas.create_image(center_x, setup_y, image=setup_box)
canvas.create_image(center_x, punch_y, image=punch_box)

# Text items for setup and punchline
setup_text_item = canvas.create_text(center_x, setup_y, text="Click 'Tell Me a Joke' to start!",
                                     font=("Arial", 16, "bold"), fill="white",
                                     width=box_w-40, justify="center")
punch_text_item = canvas.create_text(center_x, punch_y, text="",
                                     font=("Arial", 15, "italic"), fill="#ffd6d6",
                                     width=box_w-40, justify="center")

status_var = tk.StringVar(value="Ready")
status_label = tk.Label(root, textvariable=status_var, bg=root.cget("bg"), fg="white")
canvas.create_window(center_x, int(H*0.92), window=status_label)

# Functions for jokes
def tell_joke():
    global current_setup, current_punchline
    current_setup, current_punchline = random.choice(jokes_list)
    canvas.itemconfig(setup_text_item, text=current_setup)
    canvas.itemconfig(punch_text_item, text="")
    status_var.set("Ready")
    punch_btn.config(state=tk.NORMAL)
    speak_text(current_setup)

def show_punchline():
    if not current_punchline:
        messagebox.showinfo("No Joke", "Click 'Tell Me a Joke' first.")
        return
    canvas.itemconfig(punch_text_item, text=current_punchline)
    status_var.set("Ready")
    speak_text(current_punchline)

def next_joke():
    punch_btn.config(state=tk.DISABLED)
    tell_joke()

# Buttons
btn_frame = tk.Frame(root, bg=root.cget("bg"))
canvas.create_window(center_x, int(H*0.78), window=btn_frame)

def make_btn(text, cmd):
    return tk.Button(btn_frame, text=text, width=16,
                     bg="#2e86c1", fg="white", bd=0,
                     font=("Arial", 11, "bold"),
                     activebackground="#1b4f72", cursor="hand2",
                     command=cmd)

tell_btn = make_btn("Tell Me a Joke", tell_joke)
next_btn = make_btn("Next Joke", next_joke)
punch_btn = make_btn("Show Punchline", show_punchline)
quit_btn = make_btn("Quit", lambda: (pygame.mixer.music.stop(), tts_queue.put(None), root.destroy()))
play_pause_btn = make_btn("Pause Music", lambda: toggle_music())

tell_btn.grid(row=0, column=0, padx=8, pady=8)
next_btn.grid(row=0, column=1, padx=8, pady=8)
punch_btn.grid(row=0, column=2, padx=8, pady=8)
play_pause_btn.grid(row=0, column=3, padx=8, pady=8)
quit_btn.grid(row=0, column=4, padx=8, pady=8)

# Background music
pygame.mixer.init()
if os.path.exists(AUDIO_FILE):
    pygame.mixer.music.load(AUDIO_FILE)
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
else:
    print(f"Audio file not found: {AUDIO_FILE}")

# Music toggle
music_playing = True
def toggle_music():
    global music_playing
    if music_playing:
        pygame.mixer.music.pause()
        play_pause_btn.config(text="Play Music")
        music_playing = False
    else:
        pygame.mixer.music.unpause()
        play_pause_btn.config(text="Pause Music")
        music_playing = True

root.mainloop()