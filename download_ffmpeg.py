"""
ffmpegをダウンロードしてプロジェクトに含めるスクリプト
"""

import os
import urllib.request
import zipfile
import shutil


def download_ffmpeg():
    """ffmpegをダウンロード"""
    print("=" * 60)
    print(" ffmpeg ダウンロードスクリプト")
    print("=" * 60)
    print()

    # 出力ディレクトリ
    ffmpeg_dir = "ffmpeg_bin"
    if os.path.exists(ffmpeg_dir):
        print(f"[INFO] {ffmpeg_dir} already exists, skipping download")
        return True

    os.makedirs(ffmpeg_dir, exist_ok=True)

    # ffmpeg essentials build URLをダウンロード
    # 軽量版を使用（約100MB）
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    zip_path = "ffmpeg.zip"

    print(f"[INFO] Downloading ffmpeg from: {url}")
    print("[INFO] This may take a few minutes...")
    print()

    try:
        # ダウンロード
        urllib.request.urlretrieve(url, zip_path)
        print("[OK] Download complete")

        # 解凍
        print("[INFO] Extracting ffmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("temp_ffmpeg")

        # 必要なファイル（ffmpeg.exe, ffprobe.exe）を移動
        for root, dirs, files in os.walk("temp_ffmpeg"):
            for file in files:
                if file in ["ffmpeg.exe", "ffprobe.exe"]:
                    src = os.path.join(root, file)
                    dst = os.path.join(ffmpeg_dir, file)
                    shutil.copy2(src, dst)
                    print(f"[OK] Copied: {file}")

        # クリーンアップ
        os.remove(zip_path)
        shutil.rmtree("temp_ffmpeg")

        print()
        print("=" * 60)
        print(f"[OK] ffmpeg downloaded to: {ffmpeg_dir}/")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"[ERROR] Failed to download ffmpeg: {e}")
        print()
        print("Manual download:")
        print("1. Download from: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip")
        print("2. Extract ffmpeg.exe and ffprobe.exe")
        print(f"3. Place them in: {ffmpeg_dir}/")
        return False


if __name__ == "__main__":
    download_ffmpeg()
