import tkinter as tk
import time

from logging import getLogger
logger = getLogger(__name__)

def show_qrcode_dialog():
    try:
        qr_window = tk.Toplevel()
        qr_window.title("RemotePhone - Connect to Host")
        qr_window.iconbitmap("app.ico")
        qr_window.geometry("354x184")
        qr_window.attributes("-topmost", True)
        qr_window.resizable(False, False)
        qr_window.protocol("WM_DELETE_WINDOW", qr_window.destroy)

        left_frame = tk.Frame(qr_window)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        right_frame = tk.Frame(qr_window)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        qr_image = tk.PhotoImage(file="app/resources/hostsqr.png")
        qr_label = tk.Label(left_frame, image=qr_image)
        qr_label.image = qr_image
        qr_label.pack()

        description_label = tk.Label(
            right_frame, 
            text="Scan the QR code with your smartphone to connect to the host.\n\nCHROME RECOMMENDED", 
            wraplength=150,  # Set wrap length to 150 pixels
            justify="left"   # Align text to the left
        )
        description_label.pack(pady=0)

        close_button = tk.Button(right_frame, text="Close", command=qr_window.destroy)
        close_button.pack(pady=10)
        
    except Exception as e:
        logger.error(f"Error showing QR code dialog: {e}")