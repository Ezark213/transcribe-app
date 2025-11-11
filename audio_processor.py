"""
音声処理モジュール
音声ファイルの分割、長さ取得などの機能を提供
"""

import os
import sys
from datetime import timedelta


def get_ffmpeg_path():
    """実行環境に応じたffmpegのパスを取得"""
    # PyInstallerでビルドされた場合
    if getattr(sys, 'frozen', False):
        # 実行ファイルと同じディレクトリ
        bundle_dir = sys._MEIPASS
        ffmpeg_path = os.path.join(bundle_dir, 'ffmpeg.exe')
        if os.path.exists(ffmpeg_path):
            return ffmpeg_path

    # 開発環境の場合
    ffmpeg_dir = os.path.join(os.path.dirname(__file__), "ffmpeg_bin")
    ffmpeg_path = os.path.join(ffmpeg_dir, "ffmpeg.exe")
    if os.path.exists(ffmpeg_path):
        return ffmpeg_path

    # システムのPATHから探す
    return "ffmpeg"


def setup_pydub_ffmpeg():
    """pydubにffmpegのパスを設定"""
    try:
        from pydub import AudioSegment
        ffmpeg_path = get_ffmpeg_path()
        if ffmpeg_path != "ffmpeg":
            AudioSegment.converter = ffmpeg_path
            # ffprobeも同様に設定
            ffprobe_path = ffmpeg_path.replace("ffmpeg.exe", "ffprobe.exe")
            if os.path.exists(ffprobe_path):
                AudioSegment.ffprobe = ffprobe_path
    except ImportError:
        pass


def get_audio_duration(audio_file):
    """音声ファイルの長さを取得（秒）"""
    try:
        setup_pydub_ffmpeg()  # ffmpegパスを設定
        from pydub import AudioSegment
        audio = AudioSegment.from_file(audio_file)
        return len(audio) / 1000  # ミリ秒を秒に変換
    except ImportError:
        print("⚠ pydubがインストールされていないため、音声長さを自動検出できません")
        return None
    except Exception as e:
        print(f"⚠ 音声長さの取得に失敗: {e}")
        return None


def split_audio_file(audio_file, chunk_length_minutes=30, progress_callback=None):
    """
    音声ファイルをチャンクに分割

    Args:
        audio_file: 音声ファイルパス
        chunk_length_minutes: チャンクの長さ（分）
        progress_callback: 進捗コールバック関数

    Returns:
        (chunks, temp_dir) のタプル、失敗時は (None, None)
    """
    try:
        setup_pydub_ffmpeg()  # ffmpegパスを設定
        from pydub import AudioSegment

        if progress_callback:
            progress_callback(f"音声ファイルを{chunk_length_minutes}分ごとに分割しています...")

        audio = AudioSegment.from_file(audio_file)
        chunk_length_ms = chunk_length_minutes * 60 * 1000

        chunks = []
        total_chunks = len(audio) // chunk_length_ms + (1 if len(audio) % chunk_length_ms else 0)

        for i, start_ms in enumerate(range(0, len(audio), chunk_length_ms)):
            end_ms = min(start_ms + chunk_length_ms, len(audio))
            chunk = audio[start_ms:end_ms]

            # 一時ファイルとして保存
            temp_dir = os.path.join(os.path.dirname(audio_file), "temp_chunks")
            os.makedirs(temp_dir, exist_ok=True)

            base_name = os.path.splitext(os.path.basename(audio_file))[0]
            chunk_file = os.path.join(temp_dir, f"{base_name}_chunk_{i+1:03d}.wav")

            chunk.export(chunk_file, format="wav")
            chunks.append((chunk_file, start_ms / 1000, end_ms / 1000))

            if progress_callback:
                progress_callback(f"チャンク {i+1}/{total_chunks} を作成")

        if progress_callback:
            progress_callback(f"✓ {len(chunks)}個のチャンクに分割しました")

        return chunks, temp_dir

    except ImportError:
        error_msg = "長時間音声の処理にはpydubとffmpegが必要です"
        if progress_callback:
            progress_callback(f"❌ {error_msg}")
        return None, None
    except Exception as e:
        error_msg = f"音声ファイルの分割に失敗: {e}"
        if progress_callback:
            progress_callback(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return None, None


def format_time(seconds):
    """秒数を時間文字列にフォーマット"""
    return str(timedelta(seconds=int(seconds)))


def get_file_size_mb(file_path):
    """ファイルサイズをMB単位で取得"""
    return os.path.getsize(file_path) / 1024 / 1024


def cleanup_temp_files(temp_dir):
    """一時ファイルをクリーンアップ"""
    if temp_dir and os.path.exists(temp_dir):
        try:
            import shutil
            shutil.rmtree(temp_dir)
            return True, f"✓ 一時ファイルを削除しました"
        except Exception as e:
            return False, f"⚠ 一時ファイルの削除に失敗: {e}"
    return True, ""
