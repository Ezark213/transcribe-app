"""
ショートカット作成スクリプト
アプリのショートカットを作成
"""

import os
import sys


def create_shortcut(target_folder="."):
    """
    ショートカットを作成

    Args:
        target_folder: ショートカットを作成するフォルダ
    """
    try:
        import win32com.client
    except ImportError:
        print("[ERROR] pywin32 not installed")
        print("Run: pip install pywin32")
        return False

    try:
        shell = win32com.client.Dispatch("WScript.Shell")

        # ショートカットのパス
        shortcut_path = os.path.join(target_folder, "文字起こしアプリ.lnk")

        # 実行ファイルのパス
        exe_path = os.path.join(target_folder, "TranscribeApp.exe")
        if not os.path.isabs(exe_path):
            exe_path = os.path.abspath(exe_path)

        # アイコンのパス
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "transcribe_icon.ico")
        if not os.path.isabs(icon_path):
            icon_path = os.path.abspath(icon_path)

        # ショートカットを作成
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = exe_path
        shortcut.WorkingDirectory = os.path.dirname(exe_path)
        shortcut.IconLocation = icon_path
        shortcut.Description = "音声ファイルを文字起こしするアプリ"
        shortcut.save()

        print(f"[OK] Shortcut created: {shortcut_path}")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to create shortcut: {e}")
        return False


if __name__ == "__main__":
    target_folder = sys.argv[1] if len(sys.argv) > 1 else "."
    create_shortcut(target_folder)
