import customtkinter as ctk
import threading
from tkinter import filedialog
from app.main import run_pipeline

# app/gui/gui.py

# ---------
# APP SETUP
# ---------

app = ctk.CTk()
app.title("Silence Cutter")
# make it fullscreen window?
app.geometry("600x400")

# ---------
# STATE
# ---------

selected_file = None
file_label_name = ctk.StringVar(value="No file selected")

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


def start_cutting():
    if not selected_file:
        return

    print(f"Starting cutting process for: {selected_file}")

    # disable buttons during processing
    select_file_button.configure(state="disabled")
    start_button.configure(state="disabled")

    # start pipeline thread
    progress.set(0.1)  # 10%

    def worker():
        try:
            output_path = run_pipeline(selected_file)
            print(f"Pipeline completed. Output: {output_path}")
        except Exception as e:
            print(f"Error during pipeline execution thread: {e}")
        finally:
            # re-enable buttons after processing
            select_file_button.configure(state="normal")
            start_button.configure(state="normal")

    threading.Thread(target=worker, daemon=True).start()


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
    app, text="Select Video File", command=select_video)
select_file_button.pack(pady=10)

# start button disabled
start_button = ctk.CTkButton(
    app, text="Start Cutting", state="disabled", command=start_cutting)
start_button.pack(pady=10)

progress = ctk.CTkProgressBar(app, width=400)
progress.pack(pady=20)
progress.set(0)  # start at 0%

# -----------
# RUN APP
# -----------
app.mainloop()
