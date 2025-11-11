# 音声文字起こしアプリ

OpenAI Whisperを使用した、モダンなUIの音声文字起こしアプリケーションです。

## 特徴

- 🎙️ **高精度な文字起こし**: OpenAI Whisperを使用
- 🎨 **モダンなUI**: Fletによるマテリアルデザイン
- ⏱️ **長時間録音対応**: 30分以上の音声を自動的にチャンク分割して処理
- 💾 **自動保存**: デスクトップに結果を自動保存
- 🔄 **リアルタイム進捗表示**: 処理状況をリアルタイムで表示

## 対応フォーマット

- MP3
- WAV
- M4A
- FLAC
- OGG
- MP4（音声トラック）

## インストール

### 必要な依存関係

```bash
pip install -r requirements.txt
```

### ffmpegのインストール

長時間録音対応機能を使用する場合、ffmpegが必要です：
- Windows: https://ffmpeg.org/download.html
- Chocolatey: `choco install ffmpeg`

## 使い方

### 開発モードで実行

```bash
python app.py
```

### アプリケーションをビルド

```bash
python build.py
```

ビルドが完了すると、`dist/TranscribeApp.exe` が生成されます。

### 配布用パッケージを作成

```bash
python build.py
```

ビルド後、配布フォルダ作成を選択すると、`TranscribeApp_Dist/` フォルダが作成されます。
このフォルダにはショートカット付きの実行ファイルが含まれています。

## 使用技術

- **Flet**: モダンなクロスプラットフォームGUIフレームワーク
- **OpenAI Whisper**: 最先端の音声認識AI
- **pydub**: 音声ファイル処理
- **PyInstaller**: Pythonアプリケーションのビルド

## ライセンス

MIT License

## 作者

Y-IWAO

## リポジトリ

https://github.com/Ezark213/transcribe-app
