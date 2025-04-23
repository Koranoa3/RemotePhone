from win10toast import ToastNotifier
import threading

toaster = ToastNotifier()
toast_lock = threading.Lock()
toast_timer = None

def notify(message, title="RemotePhone", duration=2):
    global toast_timer

    def _show():
        with toast_lock:
            toaster.show_toast(title, message, duration=duration, threaded=True)

    with toast_lock:
        if toast_timer and toast_timer.is_alive():
            toast_timer.cancel()

        toast_timer = threading.Timer(0.1, _show)
        toast_timer.start()
