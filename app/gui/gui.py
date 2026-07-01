import os
import subprocess

import customtkinter as ctk
from app.utils import resource_path

import threading
import traceback

from tkinter import filedialog
from tkinter import messagebox
from app.main import run_pipeline

# app/gui/gui.py

# ---------
# APP SETUP
# ---------

app = ctk.CTk()
app.title("Silence Cutter")

# temporary debug
print(resource_path("assets/icon.ico"))
print(os.path.exists(resource_path("assets/icon.ico")))

# load icon safely
if os.path.exists(resource_path("assets/icon.ico")):
    app.iconbitmap(resource_path("assets/icon.ico"))

# make it fullscreen window?
app.attributes("-fullscreen", True)
# Exit fullscreen with ESC
app.bind("<Escape>", lambda e: app.attributes("-fullscreen", False))

# ---------
# STATE
# ---------

selected_file = None
file_label_name = ctk.StringVar(value="No file selected")
output_file_path = None

silence_duration_var = ctk.DoubleVar(value=1.0)

# ---------
# UI COMPONENTS
# ---------

# title label
title_label = ctk.CTkLabel(app, text="Silence Cutter",
                           font=ctk.CTkFont(size=20, weight="bold"))
title_label.pack(pady=20)

# file label
file_label = ctk.CTkLabel(app, textvariable=file_label_name)
file_label.pack(pady=10)

# select file button
select_file_button = ctk.CTkButton(
    app, text="Select Video File")
select_file_button.pack(pady=10)


# progress UI
progress = ctk.CTkProgressBar(app, width=400)
progress.pack(pady=20)
progress.set(0)  # start at 0%

status_label = ctk.CTkLabel(app, text="Waiting for input...")
status_label.pack(pady=10)

output_label = ctk.CTkLabel(app, text="")
output_label.pack(pady=10)

open_output_button = ctk.CTkButton(
    app, text="Open Output Folder", state="disabled",
    command=lambda: subprocess.run(["open", os.path.dirname(output_file_path)])
)

open_output_button.pack(pady=10)
open_output_button.pack_forget()  # hide until we have output


# Silence Threshold Functionality

# Update threshold label when slider changes


def update_silence_duration_label(value):
    silence_duration_label.configure(
        text=f"Silence Duration: {float(value):.1f}s")


silence_duration_label = ctk.CTkLabel(app, text="Silence Duration: 1.0s")
silence_duration_label.pack(pady=5)

threshold_slider = ctk.CTkSlider(
    app, from_=0.3, to=3.0, variable=silence_duration_var, command=update_silence_duration_label)
default_slider_duration = 1.0
threshold_slider.set(default_slider_duration)
threshold_slider.pack(pady=5)
# force sync silence duration at start
update_silence_duration_label(default_slider_duration)

# start button UI
start_button = ctk.CTkButton(
    app, text="Start Cutting", state="disabled")
start_button.pack(pady=10)

# --------------
# Thread-safe GUI update function for progress bar
# --------------


def update_progress_gui(value):
    app.after(0, lambda: progress.set(value))


def update_status_gui(text):
    app.after(
        0,
        lambda: status_label.configure(text=text)
    )


def set_buttons_state(state):
    app.after(0, lambda: select_file_button.configure(state=state))
    app.after(0, lambda: start_button.configure(state=state))

# ---------
# UI FUNCTIONS
# ---------


def select_video():
    global selected_file

    filetypes = (
        ("Video files", "*.mp4 *.mov *.avi *.mkv"),
        ("All files", "*.*")
    )

    filename = filedialog.askopenfilename(
        title="Select a video file",
        filetypes=filetypes
    )

    if filename:
        selected_file = filename
        file_label_name.set(f"Selected: {filename}")  # show name
        start_button.configure(state="normal")


def show_done_state():
    status_label.configure(text="Done!")

    output_label.configure(
        text=f"Output: {output_file_path}"
    )

    open_output_button.configure(state="normal")
    open_output_button.pack()


def start_cutting():
    if not selected_file:
        return

    print(f"Starting cutting process for: {selected_file}")

    # disable buttons during processing
    set_buttons_state("disabled")

    # start pipeline thread
    progress.set(0.1)  # 10%

    # get the value of slider before thread starts
    silence_duration = float(silence_duration_var.get())

    def worker():
        global output_file_path

        try:
            output_file_path = run_pipeline(
                selected_file,
                progress_callback=update_progress_gui,
                status_callback=update_status_gui,
                silence_duration=silence_duration
            )

            print(f"Pipeline completed. Output: {output_file_path}")

            app.after(0, show_done_state)

        except Exception as e:
            err = traceback.format_exc()

            print(f"Error during pipeline execution thread:\n{err}")

            def show_error():
                messagebox.showerror(
                    "Error",
                    f"Error encountered: {str(e)}\n\nDetails:\n{err}"
                )

                status_label.configure(
                    text="Error occurred. See details"
                )

            app.after(0, show_error)

        finally:
            # always restore buttons
            set_buttons_state("normal")
    threading.Thread(target=worker, daemon=True).start()


# Connect button commands after defining the functions
select_file_button.configure(command=select_video)
start_button.configure(command=start_cutting)


# -----------
# RUN APP
# -----------
app.mainloop()
