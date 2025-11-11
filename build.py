"""
アプリケーションビルドスクリプト
PyInstallerを使用してexeファイルを生成
"""

import os
import subprocess
import sys


def build_app():
    """アプリをビルド"""
    print("=" * 60)
    print(" 文字起こしアプリ - ビルドスクリプト")
    print("=" * 60)
    print()

    # PyInstallerがインストールされているか確認
    try:
        import PyInstaller
        print("[OK] PyInstaller found")
    except ImportError:
        print("[ERROR] PyInstaller not installed")
        print("Run: pip install pyinstaller")
        return False

    # ビルドオプション
    app_name = "TranscribeApp"
    icon_path = "assets/transcribe_icon.ico"

    # PyInstallerコマンドを構築
    command = [
        "pyinstaller",
        "--name", app_name,
        "--onefile",  # 単一のexeファイルを生成
        "--windowed",  # コンソールウィンドウを非表示
        "--icon", icon_path,
        "--add-data", "assets;assets",  # assetsフォルダを含める
        "--hidden-import", "flet",
        "--hidden-import", "whisper",
        "--hidden-import", "torch",
        "--hidden-import", "torchaudio",
        "--hidden-import", "pydub",
        "--collect-all", "flet",
        "--collect-all", "whisper",
        "app.py"
    ]

    print("Building application...")
    print(f"Command: {' '.join(command)}")
    print()

    # ビルド実行
    try:
        result = subprocess.run(command, check=True)

        if result.returncode == 0:
            print()
            print("=" * 60)
            print("[OK] Build successful!")
            print(f"Executable: dist/{app_name}.exe")
            print("=" * 60)
            return True
        else:
            print()
            print("[ERROR] Build failed")
            return False

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Build failed: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False


def create_distribution():
    """配布用のフォルダを作成"""
    import shutil

    print()
    print("Creating distribution folder...")

    dist_folder = "TranscribeApp_Dist"
    if os.path.exists(dist_folder):
        shutil.rmtree(dist_folder)

    os.makedirs(dist_folder)

    # exeファイルをコピー
    exe_path = "dist/TranscribeApp.exe"
    if os.path.exists(exe_path):
        shutil.copy(exe_path, dist_folder)
        print(f"[OK] Copied: {exe_path}")
    else:
        print(f"[ERROR] Executable not found: {exe_path}")
        return False

    # READMEをコピー
    if os.path.exists("README.md"):
        shutil.copy("README.md", dist_folder)
        print("[OK] Copied: README.md")

    # ショートカット作成スクリプトを実行
    print()
    print("Creating shortcut...")
    subprocess.run([sys.executable, "create_shortcut.py", dist_folder])

    print()
    print("=" * 60)
    print(f"[OK] Distribution folder created: {dist_folder}/")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = build_app()

    if success:
        print()
        response = input("Create distribution folder? (y/n): ")
        if response.lower() == 'y':
            create_distribution()
    else:
        sys.exit(1)
