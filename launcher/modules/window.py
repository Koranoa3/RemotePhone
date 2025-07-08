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

    def run(self):
        self.root.mainloop()

    def set_status(self, text):
        self.root.after(0, lambda: self.label.config(text=text))

    def close(self):
        self.root.after(0, self.root.destroy)

if __name__ == "__main__":
    window = UpdaterWindow()
    
    def long_task(window):
        import time
        window.set_status("Starting long task...")
        time.sleep(3)
        print("Task completed!")
        window.set_status("Task completed!")
        time.sleep(1)
        window.close()
    
    threading.Thread(target=long_task, args=(window,)).start()
    window.run()