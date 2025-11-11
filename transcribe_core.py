"""
文字起こしコアモジュール
Whisperを使用した音声文字起こし機能を提供
"""

import os
from datetime import timedelta
from audio_processor import (
    get_audio_duration,
    split_audio_file,
    format_time,
    get_file_size_mb,
    cleanup_temp_files
)


class TranscribeEngine:
    """文字起こしエンジンクラス"""

    def __init__(self, model_name="medium"):
        """
        Args:
            model_name: Whisperモデル名 (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self.model = None
        self.whisper = None

    def load_model(self, progress_callback=None):
        """Whisperモデルを読み込み"""
        try:
            import whisper
            self.whisper = whisper

            if progress_callback:
                progress_callback(f"Whisperモデル「{self.model_name}」を読み込んでいます...")

            self.model = whisper.load_model(self.model_name)

            if progress_callback:
                progress_callback("✓ モデルの読み込みが完了しました")

            return True, "モデルの読み込みに成功"

        except ImportError:
            error_msg = "Whisperライブラリがインストールされていません"
            if progress_callback:
                progress_callback(f"❌ {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"モデルの読み込みに失敗: {e}"
            if progress_callback:
                progress_callback(f"❌ {error_msg}")
            return False, error_msg

    def transcribe(self, audio_file, output_dir=None, use_chunking=None,
                   chunk_length_minutes=30, progress_callback=None):
        """
        音声ファイルを文字起こし

        Args:
            audio_file: 音声ファイルパス
            output_dir: 出力ディレクトリ（Noneの場合はデスクトップ）
            use_chunking: チャンク処理を使用するか（None=自動判定）
            chunk_length_minutes: チャンクの長さ（分）
            progress_callback: 進捗コールバック関数

        Returns:
            (success, message, output_file) のタプル
        """

        # ファイル存在確認
        if not os.path.exists(audio_file):
            return False, f"ファイルが見つかりません: {audio_file}", None

        # モデルロード
        if self.model is None:
            success, message = self.load_model(progress_callback)
            if not success:
                return False, message, None

        # ファイル情報表示
        file_size = get_file_size_mb(audio_file)
        if progress_callback:
            progress_callback(f"✓ 音声ファイル: {os.path.basename(audio_file)}")
            progress_callback(f"  ファイルサイズ: {file_size:.2f} MB")

        # 音声の長さを取得
        duration = get_audio_duration(audio_file)
        if duration:
            duration_str = format_time(duration)
            if progress_callback:
                progress_callback(f"  音声の長さ: {duration_str}")

            # 自動的にチャンク処理を判定（30分以上）
            if use_chunking is None:
                use_chunking = duration > chunk_length_minutes * 60

        # 出力先の決定（デスクトップ）
        if output_dir is None:
            output_dir = os.path.join(os.path.expanduser("~"), "Desktop")

        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        output_file = os.path.join(output_dir, f"{base_name}_文字起こし.txt")

        # チャンク処理
        chunks_to_cleanup = None

        try:
            if use_chunking:
                chunks, temp_dir = split_audio_file(
                    audio_file,
                    chunk_length_minutes,
                    progress_callback
                )

                if chunks is None:
                    if progress_callback:
                        progress_callback("通常の処理にフォールバックします...")
                    use_chunking = False
                else:
                    chunks_to_cleanup = temp_dir

            # 文字起こし実行
            if use_chunking:
                if progress_callback:
                    progress_callback(f"文字起こしを開始します（{len(chunks)}個のチャンク）...")

                combined_result = self._transcribe_chunks(chunks, progress_callback)

            else:
                if progress_callback:
                    progress_callback("文字起こしを開始します...")

                combined_result = self.model.transcribe(
                    audio_file,
                    language="ja",
                    verbose=False,
                    fp16=False
                )

                if progress_callback:
                    progress_callback("✓ 文字起こしが完了しました")

            # 結果を保存
            self._save_result(
                combined_result,
                output_file,
                audio_file,
                duration,
                use_chunking,
                chunk_length_minutes
            )

            if progress_callback:
                progress_callback(f"✓ 文字起こし結果を保存しました: {output_file}")

            return True, "文字起こしが完了しました", output_file

        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"文字起こし中にエラーが発生: {e}", None

        finally:
            # 一時ファイルのクリーンアップ
            if chunks_to_cleanup:
                success, message = cleanup_temp_files(chunks_to_cleanup)
                if progress_callback and message:
                    progress_callback(message)

    def _transcribe_chunks(self, chunks, progress_callback=None):
        """チャンクを文字起こし"""
        all_segments = []
        full_text = []

        for idx, (chunk_file, start_time, end_time) in enumerate(chunks):
            if progress_callback:
                progress_callback(
                    f"チャンク {idx+1}/{len(chunks)} を処理中 "
                    f"({format_time(start_time)} - {format_time(end_time)})"
                )

            # チャンクを文字起こし
            result = self.model.transcribe(
                chunk_file,
                language="ja",
                verbose=False,
                fp16=False,
                condition_on_previous_text=True
            )

            # タイムスタンプを調整
            for segment in result["segments"]:
                segment["start"] += start_time
                segment["end"] += start_time
                all_segments.append(segment)

            full_text.append(result["text"])

            if progress_callback:
                progress_callback(f"✓ チャンク {idx+1} 完了")

        if progress_callback:
            progress_callback("✓ すべてのチャンクの文字起こしが完了しました")

        return {
            "text": " ".join(full_text),
            "segments": all_segments
        }

    def _save_result(self, result, output_file, audio_file, duration,
                     use_chunking, chunk_length_minutes):
        """結果をファイルに保存"""
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write(" 音声文字起こし結果\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"元ファイル: {audio_file}\n")
            f.write(f"使用モデル: {self.model_name}\n")
            if duration:
                f.write(f"音声の長さ: {format_time(duration)}\n")
            if use_chunking:
                f.write(f"処理方法: チャンク分割処理（{chunk_length_minutes}分ごと）\n")
            f.write("\n")
            f.write("=" * 60 + "\n")
            f.write(" 文字起こしテキスト\n")
            f.write("=" * 60 + "\n\n")
            f.write(result["text"])
            f.write("\n\n")
            f.write("=" * 60 + "\n")
            f.write(" タイムスタンプ付きセグメント\n")
            f.write("=" * 60 + "\n\n")

            for segment in result["segments"]:
                start = int(segment["start"])
                end = int(segment["end"])
                text = segment["text"].strip()

                start_min = start // 60
                start_sec = start % 60
                end_min = end // 60
                end_sec = end % 60

                f.write(f"[{start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d}] {text}\n")

    def get_transcribed_text(self, output_file, max_chars=10000):
        """保存した文字起こし結果を読み込み"""
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()

            # テキスト部分を抽出
            start_marker = "=" * 60 + "\n 文字起こしテキスト\n" + "=" * 60 + "\n\n"
            end_marker = "\n\n" + "=" * 60

            start_idx = content.find(start_marker)
            if start_idx != -1:
                start_idx += len(start_marker)
                end_idx = content.find(end_marker, start_idx)
                if end_idx != -1:
                    text = content[start_idx:end_idx]
                else:
                    text = content[start_idx:]

                # 文字数制限
                if len(text) > max_chars:
                    return text[:max_chars], True, len(text)
                else:
                    return text, False, len(text)

            return content, False, len(content)

        except Exception as e:
            return f"ファイルの読み込みに失敗: {e}", False, 0
