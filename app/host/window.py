import webview
webview.config.gui = 'cef'

def _create_window():
    """
    Create a webview window.
    """
    window = webview.create_window(
        "RemotePhone", "ui/index.html",
        width=800, height=600,
        resizable=True, min_size=(800, 600), fullscreen=False,
        js_api= {
            
        }
    )
    return window

def run_window():
    """
    Run the webview window.
    
    Args:
        window (webview.Window): The webview window to run.
    """
    webview.start(debug=True, window=_create_window())