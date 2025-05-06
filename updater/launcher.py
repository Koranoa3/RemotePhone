import subprocess

def launch_new_app(app_path):
    try:
        subprocess.Popen([app_path], shell=False)
    except Exception as e:
        print(f"[Error] 新アプリ起動失敗: {e}")
