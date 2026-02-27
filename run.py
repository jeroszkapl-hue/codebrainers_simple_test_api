import threading
import webbrowser
import tkinter as tk
import uvicorn
from main import app

APP_URL = "http://127.0.0.1:8000"

def start_server():
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_config=None   # dalej potrzebne przy buildzie bez konsoli
    )

def open_browser():
    webbrowser.open(APP_URL)

def show_splash():
    root = tk.Tk()
    root.title("Employee Manager")
    root.geometry("320x140")
    root.resizable(False, False)

    tk.Label(root, text="Uruchamianie aplikacji...", font=("Segoe UI", 11)).pack(pady=25)
    tk.Button(root, text="Otwórz aplikację", command=open_browser).pack(pady=5)
    tk.Label(root, text=APP_URL, font=("Segoe UI", 9)).pack(pady=5)

    root.after(5000, root.destroy)
    root.mainloop()

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    show_splash()