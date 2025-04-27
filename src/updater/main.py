import sys
import os
import requests
import time
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

def download_file(url, dest_path, progress_callback=None):
    response = requests.get(url, stream=True)
    total = int(response.headers.get('content-length', 0))
    downloaded = 0

    with open(dest_path + ".tmp", "wb") as f:
        for data in response.iter_content(chunk_size=4096):
            f.write(data)
            downloaded += len(data)
            if progress_callback:
                progress_callback(downloaded, total)

    # ダウンロード完了後に本番ファイルへリネーム
    os.replace(dest_path + ".tmp", dest_path)

def main():
    # コマンドライン引数受け取り
    if len(sys.argv) < 3:
        messagebox.showerror("エラー", "引数が不足しています。\nurlとdestパスが必要です。")
        sys.exit(1)

    url = sys.argv[1]   # ダウンロードURL
    dest_path = sys.argv[2]  # 保存先ファイルパス (例: RemotePhone.exe)

    # GUIセットアップ
    root = tk.Tk()
    root.title("アップデート中...")
    root.geometry("400x100")
    root.resizable(False, False)

    label = ttk.Label(root, text="ダウンロード中...")
    label.pack(pady=10)

    progress = ttk.Progressbar(root, length=300, mode='determinate')
    progress.pack(pady=5)

    def update_progress(downloaded, total):
        percent = int(downloaded / total * 100)
        progress['value'] = percent
        root.update_idletasks()

    # ダウンロード実行
    try:
        download_file(url, dest_path, progress_callback=update_progress)
    except Exception as e:
        messagebox.showerror("エラー", f"ダウンロード中にエラー発生:\n{str(e)}")
        sys.exit(1)

    # ダウンロード完了
    label.config(text="インストール完了！起動します...")

    # アプリ起動
    try:
        subprocess.Popen([dest_path])
    except Exception as e:
        messagebox.showerror("エラー", f"起動に失敗しました:\n{str(e)}")
        sys.exit(1)

    time.sleep(1)
    root.destroy()
    sys.exit(0)

if __name__ == "__main__":
    main()
