"""
文字起こしアプリ - Fletベース
モダンなマテリアルデザインUIで音声ファイルを文字起こし
"""

import flet as ft
import os
import threading
from transcribe_core import TranscribeEngine


class TranscribeApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "音声文字起こしアプリ"
        self.page.window_width = 900
        self.page.window_height = 700
        self.page.window_resizable = True
        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.LIGHT

        # 状態
        self.selected_file = None
        self.engine = None
        self.is_processing = False

        # UIコンポーネント
        self.build_ui()

    def build_ui(self):
        """UIを構築"""

        # ヘッダー
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.MIC, size=40, color=ft.colors.WHITE),
                    ft.Text(
                        "音声文字起こしアプリ",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.WHITE,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            bgcolor=ft.colors.BLUE_700,
            padding=20,
        )

        # ファイル選択エリア
        self.file_text = ft.Text(
            "音声ファイルを選択してください",
            size=16,
            color=ft.colors.GREY_700,
        )

        file_picker = ft.FilePicker(on_result=self.on_file_picked)
        self.page.overlay.append(file_picker)

        select_button = ft.ElevatedButton(
            "ファイルを選択",
            icon=ft.icons.FOLDER_OPEN,
            on_click=lambda _: file_picker.pick_files(
                allowed_extensions=["mp3", "wav", "m4a", "flac", "ogg", "mp4"],
                dialog_title="音声ファイルを選択",
            ),
            style=ft.ButtonStyle(
                bgcolor=ft.colors.BLUE_600,
                color=ft.colors.WHITE,
            ),
        )

        file_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.icons.AUDIO_FILE, size=64, color=ft.colors.BLUE_400),
                        self.file_text,
                        select_button,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                ),
                padding=30,
            ),
            elevation=2,
        )

        # モデル選択
        self.model_dropdown = ft.Dropdown(
            label="Whisperモデル",
            options=[
                ft.dropdown.Option("tiny", "Tiny - 最速（精度低）"),
                ft.dropdown.Option("base", "Base - 高速（精度中）"),
                ft.dropdown.Option("small", "Small - バランス型"),
                ft.dropdown.Option("medium", "Medium - 高精度（推奨）"),
                ft.dropdown.Option("large", "Large - 最高精度（遅い）"),
            ],
            value="medium",
            width=400,
        )

        # 進捗表示
        self.progress_ring = ft.ProgressRing(visible=False)
        self.progress_text = ft.Text("", size=14, color=ft.colors.GREY_700)

        self.log_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text("処理ログ:", weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Column([], scroll=ft.ScrollMode.AUTO),
                        height=200,
                        border=ft.border.all(1, ft.colors.GREY_400),
                        border_radius=5,
                        padding=10,
                    ),
                ],
                spacing=10,
            ),
            visible=False,
        )

        # 実行ボタン
        self.start_button = ft.ElevatedButton(
            "文字起こしを開始",
            icon=ft.icons.PLAY_ARROW,
            on_click=self.start_transcription,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.GREEN_600,
                color=ft.colors.WHITE,
            ),
            width=200,
            height=50,
            disabled=True,
        )

        # 結果表示エリア
        self.result_text = ft.Text(
            "",
            size=14,
            selectable=True,
        )

        self.result_container = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "文字起こし結果:",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.IconButton(
                                icon=ft.icons.COPY,
                                tooltip="コピー",
                                on_click=self.copy_result,
                            ),
                            ft.IconButton(
                                icon=ft.icons.OPEN_IN_NEW,
                                tooltip="ファイルを開く",
                                on_click=self.open_result_file,
                            ),
                        ],
                    ),
                    ft.Container(
                        content=ft.Column(
                            [self.result_text],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        height=250,
                        border=ft.border.all(1, ft.colors.GREY_400),
                        border_radius=5,
                        padding=15,
                        bgcolor=ft.colors.GREY_50,
                    ),
                ],
                spacing=10,
            ),
            visible=False,
        )

        # メインコンテンツ
        content = ft.Container(
            content=ft.Column(
                [
                    file_card,
                    ft.Divider(height=20),
                    ft.Container(
                        content=ft.Row(
                            [self.model_dropdown],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.symmetric(vertical=10),
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                self.progress_ring,
                                self.start_button,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20,
                        ),
                        padding=ft.padding.symmetric(vertical=10),
                    ),
                    self.progress_text,
                    self.log_container,
                    ft.Divider(height=20),
                    self.result_container,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=20,
            expand=True,
        )

        # ページに追加
        self.page.add(
            ft.Column(
                [
                    header,
                    content,
                ],
                spacing=0,
                expand=True,
            )
        )

    def on_file_picked(self, e: ft.FilePickerResultEvent):
        """ファイルが選択されたときの処理"""
        if e.files:
            self.selected_file = e.files[0].path
            file_name = os.path.basename(self.selected_file)
            file_size = os.path.getsize(self.selected_file) / 1024 / 1024

            self.file_text.value = f"✓ {file_name}\nサイズ: {file_size:.2f} MB"
            self.start_button.disabled = False
            self.page.update()

    def add_log(self, message):
        """ログを追加"""
        log_col = self.log_container.content.controls[1].content
        log_col.controls.append(
            ft.Text(message, size=12, color=ft.colors.GREY_800)
        )
        self.page.update()

    def start_transcription(self, e):
        """文字起こしを開始"""
        if self.is_processing or not self.selected_file:
            return

        self.is_processing = True
        self.start_button.disabled = True
        self.progress_ring.visible = True
        self.log_container.visible = True
        self.result_container.visible = False
        self.result_text.value = ""

        # ログをクリア
        log_col = self.log_container.content.controls[1].content
        log_col.controls.clear()

        self.page.update()

        # バックグラウンドで実行
        thread = threading.Thread(target=self.run_transcription)
        thread.start()

    def run_transcription(self):
        """文字起こしを実行"""
        try:
            # エンジンを初期化
            model_name = self.model_dropdown.value
            self.engine = TranscribeEngine(model_name)

            def progress_callback(message):
                self.progress_text.value = message
                self.add_log(message)

            # 文字起こし実行
            success, message, output_file = self.engine.transcribe(
                self.selected_file,
                progress_callback=progress_callback
            )

            if success:
                # 結果を表示
                text, truncated, total_chars = self.engine.get_transcribed_text(
                    output_file,
                    max_chars=5000
                )

                self.result_text.value = text
                if truncated:
                    self.result_text.value += f"\n\n[長いテキストのため、最初の5000文字のみ表示]"
                    self.result_text.value += f"\n総文字数: {total_chars}文字"
                    self.result_text.value += f"\n\n全文は以下のファイルに保存されています:\n{output_file}"

                self.result_container.visible = True
                self.output_file = output_file

            self.progress_text.value = message
            self.add_log(message)

        except Exception as e:
            error_msg = f"エラー: {e}"
            self.progress_text.value = error_msg
            self.add_log(error_msg)

        finally:
            self.is_processing = False
            self.start_button.disabled = False
            self.progress_ring.visible = False
            self.page.update()

    def copy_result(self, e):
        """結果をクリップボードにコピー"""
        if self.result_text.value:
            self.page.set_clipboard(self.result_text.value)
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("クリップボードにコピーしました"))
            )

    def open_result_file(self, e):
        """結果ファイルを開く"""
        if hasattr(self, 'output_file') and os.path.exists(self.output_file):
            import subprocess
            subprocess.Popen(['notepad', self.output_file])


def main(page: ft.Page):
    TranscribeApp(page)


if __name__ == "__main__":
    ft.app(target=main)
