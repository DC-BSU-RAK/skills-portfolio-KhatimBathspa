import tkinter as tk
from tkinter import messagebox, Toplevel
import random
import threading
import os
from PIL import Image, ImageTk
import pygame

AUDIO_FILE = "quizaudio.mp3"
BG_IMAGE_FILE = "background1.jpg"

# Absolute Paths 
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_FILE_PATH = os.path.join(SCRIPT_DIR, AUDIO_FILE)
BG_IMAGE_PATH = os.path.join(SCRIPT_DIR, BG_IMAGE_FILE)

if not os.path.exists(AUDIO_FILE_PATH):
    print(f"Warning: Audio file not found at: {AUDIO_FILE_PATH}")
    AUDIO_FILE_PATH = None

if not os.path.exists(BG_IMAGE_PATH):
    print(f"Warning: Background image not found at: {BG_IMAGE_PATH}")
    BG_IMAGE_PATH = None

# Global Variables 
SCORE = 0
QUESTION_COUNT = 0
MAX_QUESTIONS = 10
DIFFICULTY = 0
CURRENT_ANSWER = 0
ATTEMPTS_LEFT = 2
PROBLEM_STRING = ""
USER_NAME = ""
INSTITUTION = ""
answer_entry = None
feedback_label = None
CURRENT_HINT = ""
BG_LABEL = None
ORIGINAL_BG_IMAGE = None
BG_PHOTO = None

#  Colors 
COLOR_PALETTE = {
    "BG_PRIMARY": "#FFE6EB",      # soft rose background
    "BG_SECONDARY": "#FFF8FA",    # creamy pink card
    "FG_PRIMARY": "#4A2E2E",      # dark brown text
    "FG_SECONDARY": "#B38B8B",    # muted rose
    "ACCENT_PRIMARY": "#FF8FB1",  # pastel pink
    "ACCENT_SUCCESS": "#A1E3A1",  # mint green
    "ACCENT_FAIL": "#FF6B81",     # coral pink
    "ENTRY_BG": "#FFE9EE",        # light blush
    "ACCENT_BLACK": "#3E2723"     # deep brown
}

# Difficulty Map 
DIFFICULTY_MAP = {
    1: (0, 9, "Single-Digit (0-9)"),
    2: (10, 99, "Double-Digit (10-99)"),
    3: (1000, 9999, "Four-Digit (1000-9999)")
}

# Audio 
USE_PYGAME = False

def init_audio():
    global USE_PYGAME
    if not AUDIO_FILE_PATH:
        return
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        USE_PYGAME = True
        print("Audio initialized with pygame.")
    except Exception as e:
        print("Pygame audio initialization failed:", e)
        USE_PYGAME = False

def play_background_music():
    if not AUDIO_FILE_PATH or not USE_PYGAME:
        return
    try:
        pygame.mixer.music.load(AUDIO_FILE_PATH)
        pygame.mixer.music.set_volume(0.25)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print("Error playing audio:", e)

def start_music():
    threading.Thread(target=play_background_music, daemon=True).start()

# Utility 
def clear_frame(frame):
    for widget in frame.winfo_children():
        if widget != BG_LABEL:
            widget.destroy()

def randomInt(min_val, max_val):
    return random.randint(min_val, max_val)

def decideOperation():
    return random.choice(['+', '-'])

def get_rank(final_score):
    if final_score >= 90: return "A+"
    elif final_score >= 80: return "A"
    elif final_score >= 70: return "B"
    elif final_score >= 60: return "C"
    else: return "D"

def get_hint(num1, num2, operation):
    return "Hint: Addition problem." if operation=='+' else "Hint: Subtraction problem."

def generateProblem():
    global CURRENT_ANSWER, PROBLEM_STRING, ATTEMPTS_LEFT
    min_val, max_val, _ = DIFFICULTY_MAP.get(DIFFICULTY, (0,9,""))
    num1 = randomInt(min_val, max_val)
    num2 = randomInt(min_val, max_val)
    operation = decideOperation()
    CURRENT_ANSWER = num1+num2 if operation=='+' else num1-num2
    PROBLEM_STRING = f"{num1} {operation} {num2} ="
    ATTEMPTS_LEFT = 2
    return PROBLEM_STRING, num1, num2, operation

def isCorrect(user_answer, current_answer):
    try:
        return int(user_answer) == current_answer
    except:
        return False

def quitQuizEarly():
    if messagebox.askyesno("Exit Quiz", "Are you sure you want to quit?"):
        if USE_PYGAME:
            pygame.mixer.music.stop()
        window.quit()

# Background Image
def resize_background(event):
    global ORIGINAL_BG_IMAGE, BG_PHOTO, BG_LABEL
    if ORIGINAL_BG_IMAGE and BG_LABEL:
        new_width = event.width
        new_height = event.height
        resized_image = ORIGINAL_BG_IMAGE.resize((new_width, new_height), Image.Resampling.LANCZOS)
        BG_PHOTO = ImageTk.PhotoImage(resized_image)
        BG_LABEL.config(image=BG_PHOTO)
        BG_LABEL.image = BG_PHOTO

def set_background(frame):
    global ORIGINAL_BG_IMAGE, BG_LABEL
    if not BG_IMAGE_PATH:
        return
    if ORIGINAL_BG_IMAGE is None:
        ORIGINAL_BG_IMAGE = Image.open(BG_IMAGE_PATH)
    if BG_LABEL is None:
        BG_LABEL = tk.Label(frame)
        BG_LABEL.place(x=0,y=0,relwidth=1,relheight=1)
        BG_LABEL.lower()
        frame.bind('<Configure>', resize_background)
    class DummyEvent:
        def __init__(self, width, height):
            self.width = width
            self.height = height
    resize_background(DummyEvent(frame.winfo_width(), frame.winfo_height()))

# GUI Screens
def displayWelcomeScreen():
    clear_frame(main_frame)
    window.title("Ultimate Math Challenge")
    main_frame.config(bg=COLOR_PALETTE["BG_PRIMARY"])
    set_background(main_frame)
    
    card = tk.Frame(main_frame, bg=COLOR_PALETTE["BG_SECONDARY"], padx=40,pady=40)
    card.pack(pady=70,padx=20)
    tk.Label(card,text="🎯 Ultimate Arithmetic Quiz 🎯", font=('Inter',22,'bold'),
             fg=COLOR_PALETTE["ACCENT_PRIMARY"], bg=COLOR_PALETTE["BG_SECONDARY"]).pack(pady=(10,20))
    tk.Label(card,text="Test your addition and subtraction skills across three difficulty levels!",
             font=('Inter',12), fg=COLOR_PALETTE["FG_PRIMARY"], bg=COLOR_PALETTE["BG_SECONDARY"], wraplength=380, justify='center').pack(pady=20)
    tk.Button(card,text="Start Registration", command=displayStartScreen, font=('Inter',14,'bold'),
              bg=COLOR_PALETTE["ACCENT_PRIMARY"], fg="white", relief='flat', padx=20, pady=10, width=20).pack(pady=10)

def displayStartScreen():
    clear_frame(main_frame)
    window.title("Quiz Registration")
    main_frame.config(bg=COLOR_PALETTE["BG_PRIMARY"])
    set_background(main_frame)
    
    card = tk.Frame(main_frame, bg=COLOR_PALETTE["BG_SECONDARY"], padx=40,pady=40)
    card.pack(pady=70,padx=20)
    
    tk.Label(card,text="Math Quiz Registration", font=('Inter',20,'bold'), fg=COLOR_PALETTE["ACCENT_PRIMARY"], bg=COLOR_PALETTE["BG_SECONDARY"]).pack(pady=15)
    
    tk.Label(card,text="Your Name:", anchor='w', font=('Inter',12), fg=COLOR_PALETTE["FG_PRIMARY"], bg=COLOR_PALETTE["BG_SECONDARY"]).pack(fill='x', pady=(15,5))
    global name_entry
    name_entry = tk.Entry(card, font=('Inter',14), width=30, bd=1, relief='solid', fg=COLOR_PALETTE["FG_PRIMARY"], bg=COLOR_PALETTE["ENTRY_BG"], insertbackground=COLOR_PALETTE["FG_PRIMARY"])
    name_entry.pack(pady=(0,15))
    
    tk.Label(card,text="Institution:", anchor='w', font=('Inter',12), fg=COLOR_PALETTE["FG_PRIMARY"], bg=COLOR_PALETTE["BG_SECONDARY"]).pack(fill='x', pady=(15,5))
    global inst_entry
    inst_entry = tk.Entry(card, font=('Inter',14), width=30, bd=1, relief='solid', fg=COLOR_PALETTE["FG_PRIMARY"], bg=COLOR_PALETTE["ENTRY_BG"], insertbackground=COLOR_PALETTE["FG_PRIMARY"])
    inst_entry.pack(pady=(0,30))
    
    tk.Button(card,text="Start Quiz", command=processStartDetails, font=('Inter',14,'bold'),
              bg=COLOR_PALETTE["ACCENT_SUCCESS"], fg=COLOR_PALETTE["FG_PRIMARY"], relief='flat', padx=20, pady=10, width=20).pack(pady=10)

def processStartDetails():
    global USER_NAME, INSTITUTION
    name = name_entry.get().strip()
    institution = inst_entry.get().strip()
    if not name or not institution:
        messagebox.showerror("Input Error","Please enter both Name and Institution.")
        return
    USER_NAME = name
    INSTITUTION = institution
    displayMenu()

def displayMenu():
    clear_frame(main_frame)
    window.title("Math Quiz | Select Difficulty")
    main_frame.config(bg=COLOR_PALETTE["BG_PRIMARY"])
    set_background(main_frame)
    
    card = tk.Frame(main_frame, bg=COLOR_PALETTE["BG_SECONDARY"], padx=40,pady=40)
    card.pack(pady=70,padx=20)
    tk.Label(card,text="Select Difficulty", font=('Inter',20,'bold'), fg=COLOR_PALETTE["ACCENT_PRIMARY"], bg=COLOR_PALETTE["BG_SECONDARY"]).pack(pady=15)
    
    for level, (_,_,desc) in DIFFICULTY_MAP.items():
        tk.Button(card,text=f"{level}. {desc}", command=lambda l=level: startQuiz(l), width=25,
                  font=('Inter',14), bg=COLOR_PALETTE["ACCENT_PRIMARY"], fg="white").pack(pady=10)

def startQuiz(level):
    global DIFFICULTY, SCORE, QUESTION_COUNT
    DIFFICULTY = level
    SCORE = 0
    QUESTION_COUNT = 0
    start_music()
    displayProblem()

# ----------------- MODIFIED FUNCTION -----------------
def displayProblem():
    global QUESTION_COUNT, answer_entry, feedback_label, CURRENT_HINT
    clear_frame(main_frame)
    window.title(f"Math Quiz | Question {QUESTION_COUNT+1}")
    main_frame.config(bg=COLOR_PALETTE["BG_PRIMARY"])
    set_background(main_frame)
    
    problem_card = tk.Frame(main_frame, bg=COLOR_PALETTE["BG_SECONDARY"], padx=30,pady=30)
    problem_card.pack(pady=40) 
    
    # --- Header frame inside the problem_card ---
    header_frame = tk.Frame(problem_card, bg=COLOR_PALETTE["BG_SECONDARY"])
    header_frame.pack(fill='x', expand=True, pady=(0, 15))
              
    # --- Score label ---
    tk.Label(header_frame,text=f"Score: {SCORE} | Question: {QUESTION_COUNT+1} of {MAX_QUESTIONS}",
             bg=COLOR_PALETTE["BG_SECONDARY"], 
             fg=COLOR_PALETTE["FG_PRIMARY"]).pack(side=tk.LEFT)
    # --- End of header ---

    problem_text, num1, num2, operation = generateProblem()
    CURRENT_HINT = get_hint(num1,num2,operation)
    
    tk.Label(problem_card,text=problem_text, font=('Inter',40,'bold'), bg=COLOR_PALETTE["BG_SECONDARY"], fg=COLOR_PALETTE["FG_PRIMARY"]).pack(pady=20)
    
    answer_entry = tk.Entry(problem_card, font=('Inter',20), width=15, justify='center', bd=2, relief='solid', bg=COLOR_PALETTE["ENTRY_BG"], fg=COLOR_PALETTE["FG_PRIMARY"], insertbackground=COLOR_PALETTE["FG_PRIMARY"])
    answer_entry.pack(pady=15)
    answer_entry.focus_set()
    
    # --- Feedback label moved inside the card ---
    feedback_label = tk.Label(problem_card,text="", font=('Inter',14), bg=COLOR_PALETTE["BG_SECONDARY"])
    feedback_label.pack(pady=(10,0)) # Packed inside problem_card
    
    tk.Button(problem_card,text="Submit Answer", command=submitAnswer, bg=COLOR_PALETTE["ACCENT_PRIMARY"], fg="white").pack(pady=20)
    
    # --- Quit button ---
    tk.Button(problem_card,text="❌ Quit Test", command=quitQuizEarly, 
              bg=COLOR_PALETTE["ACCENT_FAIL"], fg="white").pack(pady=(5, 10))
# ----------------- END OF MODIFIED FUNCTION -----------------

def submitAnswer():
    global SCORE, QUESTION_COUNT, ATTEMPTS_LEFT
    user_input = answer_entry.get().strip()
    feedback_label.config(text="") # Clear previous feedback first
    
    if not user_input:
        feedback_label.config(text="Please enter an answer.", fg=COLOR_PALETTE["ACCENT_FAIL"])
        return
        
    if isCorrect(user_input,CURRENT_ANSWER):
        score_awarded = 10 if ATTEMPTS_LEFT==2 else 5
        SCORE += score_awarded
        feedback_label.config(text=f"✅ Correct! (+{score_awarded} points)", fg=COLOR_PALETTE["ACCENT_SUCCESS"])
        QUESTION_COUNT += 1
        answer_entry.delete(0,tk.END)
        window.after(500,nextQuestionOrEnd) # Wait 500ms before next question
    else:
        ATTEMPTS_LEFT -= 1
        if ATTEMPTS_LEFT==1:
            message = f"Incorrect. One attempt left (5 points available)."
            show_feedback_window(message, hint=CURRENT_HINT)
            answer_entry.delete(0,tk.END)
            answer_entry.focus_set()
            return
        elif ATTEMPTS_LEFT==0:
            message = f"Incorrect. The correct answer was: {CURRENT_ANSWER}."
            show_feedback_window(message)
            QUESTION_COUNT += 1
            answer_entry.delete(0,tk.END)
            nextQuestionOrEnd() # Move to next question immediately after showing answer

def show_feedback_window(message, hint=None):
    # This function is for the INCORRECT answer popup.
    # The CORRECT feedback is handled by the feedback_label.
    feedback_window = Toplevel(window)
    feedback_window.title("Feedback")
    feedback_window.geometry("500x300")
    feedback_window.config(bg=COLOR_PALETTE["ACCENT_FAIL"])
    feedback_window.attributes('-topmost', True)
    tk.Label(feedback_window,text=message,font=('Inter',16),bg=COLOR_PALETTE["ACCENT_FAIL"],fg="white").pack(pady=20)
    if hint:
        tk.Label(feedback_window,text=hint,font=('Inter',14),bg=COLOR_PALETTE["ACCENT_FAIL"],fg="white",wraplength=450).pack(pady=10)
    def close_and_unwait():
        feedback_window.destroy()
        window.grab_release()
    tk.Button(feedback_window,text="Continue", command=close_and_unwait, bg="white", fg=COLOR_PALETTE["FG_PRIMARY"]).pack(pady=10)
    feedback_window.grab_set()
    window.wait_window(feedback_window)

def nextQuestionOrEnd():
    if QUESTION_COUNT < MAX_QUESTIONS:
        displayProblem()
    else:
        if USE_PYGAME: # Stop music on quiz completion
            pygame.mixer.music.stop()
        displayResults()

def displayResults():
    clear_frame(main_frame)
    window.title("Math Quiz | Results")
    main_frame.config(bg=COLOR_PALETTE["BG_PRIMARY"])
    set_background(main_frame)
    
    results_card = tk.Frame(main_frame, bg=COLOR_PALETTE["BG_SECONDARY"], padx=40,pady=40)
    results_card.pack(pady=70,padx=20)
    
    final_score_percentage = (SCORE/(MAX_QUESTIONS*10))*100
    rank = get_rank(final_score_percentage)
    
    tk.Label(results_card,text=f"Quiz Complete, {USER_NAME}!", font=('Inter',20,'bold'), fg=COLOR_PALETTE["FG_PRIMARY"], bg=COLOR_PALETTE["BG_SECONDARY"]).pack(pady=10)
    tk.Label(results_card,text=f"Total Score: {SCORE}/{MAX_QUESTIONS*10}", font=('Inter',16), fg=COLOR_PALETTE["ACCENT_PRIMARY"], bg=COLOR_PALETTE["BG_SECONDARY"]).pack(pady=5)
    tk.Label(results_card,text=f"Final Rank: {rank}", font=('Inter',18,'bold'), fg=COLOR_PALETTE["ACCENT_SUCCESS"], bg=COLOR_PALETTE["BG_SECONDARY"]).pack(pady=10)
    
    tk.Button(results_card,text="Replay", command=displayWelcomeScreen, font=('Inter',14), bg=COLOR_PALETTE["ACCENT_PRIMARY"], fg="white", relief='flat', padx=20,pady=10,width=15).pack(pady=15)
    tk.Button(results_card,text="Exit", command=quitQuizEarly, font=('Inter',14), bg=COLOR_PALETTE["ACCENT_FAIL"], fg="white", relief='flat', padx=20,pady=10,width=15).pack(pady=5)

# Main App 
window = tk.Tk()
window.title("Math Quiz")
window.attributes('-fullscreen', True)
window.bind('<Escape>', lambda e: quitQuizEarly())

main_frame = tk.Frame(window, bg=COLOR_PALETTE["BG_PRIMARY"])
main_frame.pack(expand=True, fill='both')

init_audio()
displayWelcomeScreen()
window.mainloop()