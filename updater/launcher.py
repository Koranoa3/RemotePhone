import subprocess

def launch_new_app(app_path):
    try:
        subprocess.Popen([app_path], shell=False)
    except Exception as e:
        print(f"[Error] Failed to launch the new app: {e}")
