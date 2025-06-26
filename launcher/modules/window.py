import tkinter as tk
import threading

class UpdaterWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("RemotePhone Launcher")
        self.root.iconbitmap(default="app.ico")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)

        # Set custom background and text color
        self.root.configure(bg="#313842")
        
        self.label = tk.Label(
            self.root,
            text="Initializing...",
            font=("Arial", 16),
            bg="#313842",
            fg="#eeeeee"
        )
        self.label.pack(expand=True)

    def set_status(self, text):
        self.label.config(text=text)
        self.root.update()

    def run_in_thread(self):
        threading.Thread(target=self.root.mainloop, daemon=True).start()

    def close(self):
        self.root.destroy()

if __name__ == "__main__":
    window = UpdaterWindow()
    window.run_in_thread()
    window.set_status("Updater is running...")
    window.root.mainloop()