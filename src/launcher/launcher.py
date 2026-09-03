import os
import sys
import time
import subprocess
import requests
import tkinter as tk
from tkinter import messagebox


# Finding the application directories

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable) # Running as a PyInstaller executable
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Running as normal Python script

SERVER = os.path.join(BASE_DIR, "deadlock-live-events.exe")

PREDICTOR = os.path.join(BASE_DIR, "predictor", "live_predictor", "live_predictor.exe")

OVERLAY = os.path.join(BASE_DIR, "overlay.exe")

#--------------------------

server_process = None
predictor_process = None
overlay_process = None

def wait_for_server(timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            requests.get("http://localhost:3000", timeout=1)
            return True
        except requests.RequestException:
            time.sleep(0.5)
    return False



def cleanup():
    global server_process
    global predictor_process
    global overlay_process
    stop_process(overlay_process, "overlay.exe")
    stop_process(predictor_process, "live_predictor.exe")
    stop_process(server_process, "deadlock-live-events.exe")
    overlay_process = None
    predictor_process = None
    server_process = None



def stop_process(process):
    if process is not None:
        try:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=1)
        except Exception:
            pass
        try: #If still alive kill all tree
            if process.poll() is None:
                subprocess.run(
                    [
                        "taskkill",
                        "/PID",
                        str(process.pid),
                        "/T",
                        "/F"
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
        except Exception:
            pass



def stop_prediction():
    global server_process
    global predictor_process
    global overlay_process

    print("Stopping prediction...")

    stop_process(overlay_process, "overlay.exe")
    stop_process(predictor_process, "live_predictor.exe")
    stop_process(server_process, "deadlock-live-events.exe")

    overlay_process = None
    predictor_process = None
    server_process = None

    match_entry.config(state="normal")

    start_button.config(text="Start Prediction", state="normal",command=start_clicked)

    match_label.config(text="")

    print("Prediction stopped.")



def start_application(match_id):

    global server_process
    global predictor_process
    global overlay_process

    try:

        required_files = {
            "Live Events Server": SERVER,
            "Predictor": PREDICTOR,
            "Overlay": OVERLAY,
        }

        missing = []

        for name, path in required_files.items():
            if not os.path.exists(path):
                missing.append(f"{name}:\n{path}")
        if missing:
            messagebox.showerror("Deadlock Predictor", "The following files are missing:\n\n" + "\n\n".join(missing))
            return

        #Server

        server_process = subprocess.Popen([SERVER], cwd=os.path.dirname(SERVER), creationflags=subprocess.CREATE_NO_WINDOW)

        start_button.config(text="Starting server...", state="disabled")

        root.update()

        if not wait_for_server():
            messagebox.showerror("Deadlock Predictor", "Could not start the live-events server.")
            cleanup()
            return

        #Predictor

        predictor_process = subprocess.Popen([PREDICTOR, "--match", str(match_id)], cwd=os.path.dirname(PREDICTOR))

        #Overlay

        overlay_process = subprocess.Popen([OVERLAY], cwd=os.path.dirname(OVERLAY))


        match_label.config(text=f"Prediction running\nMatch: {match_id}")

        start_button.config(text="Stop Prediction", state="normal", command=stop_prediction)

        match_entry.config(state="disabled")

        monitor()

    except Exception as e:
        messagebox.showerror("Deadlock Predictor", f"Failed to start application:\n\n{e}")
        cleanup()



def monitor():
    global predictor_process
    if predictor_process is None:
        return

    if predictor_process.poll() is not None:
        cleanup()
        match_entry.config(state="normal")
        start_button.config(text="Start Prediction", state="normal", command=start_clicked)
        match_label.config(text="")
        return

    root.after(1000, monitor)



def start_clicked():
    match_id = match_entry.get().strip()
    if not match_id:
        messagebox.showwarning("Deadlock Predictor", "Please enter a match ID.")
        return

    if not match_id.isdigit():
        messagebox.showwarning("Deadlock Predictor", "Match ID must contain only numbers.")
        return

    start_application(match_id)



def on_close():
    cleanup()
    root.destroy()


root = tk.Tk()

root.title("Deadlock Predictor")

root.geometry("450x250")
root.resizable(False, False)

root.protocol("WM_DELETE_WINDOW", on_close)

title = tk.Label(root, text="Deadlock Predictor", font=("Arial", 22, "bold"))

title.pack(pady=(25, 20))

label = tk.Label(root, text="Match ID")

label.pack()

match_entry = tk.Entry(root, width=30, font=("Arial", 14), justify="center")

match_entry.pack(pady=10)

match_label = tk.Label(root, text="", font=("Arial", 10))

match_label.pack()


start_button = tk.Button(root, text="Start Prediction", font=("Arial", 12, "bold"), width=20, command=start_clicked)

start_button.pack(pady=15)


root.mainloop()