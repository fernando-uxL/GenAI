
AI Summarizer (Windows) — Text-based PDFs Only
==============================================

This package builds a single-file Windows executable (.exe) that summarizes text-based PDFs (and .txt files)
using Google's Gemini API. It does NOT include OCR — scanned image PDFs won't be readable.

Files in this folder:
- AI_Summarizer.py     -> Combined GUI (Tkinter) + local backend (FastAPI)
- requirements.txt     -> Python dependencies
- config.txt           -> Put your Gemini API key here (or set GEMINI_API_KEY env var)
- icon.ico             -> App icon
- build_windows.bat    -> One-click build script (creates dist/AI_Summarizer.exe)

Quick Start (Run from Source)
-----------------------------
1) Install Python 3.10+
2) Open a terminal in this folder and run:
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
3) Edit config.txt and set your API key on the GEMINI_API_KEY line.
4) Run:
   python AI_Summarizer.py

Build Single Executable (.exe)
------------------------------
1) Open a terminal in this folder and run:
   build_windows.bat
2) Your EXE will be in the "dist" folder:
   dist\AI_Summarizer.exe

Usage
-----
- Launch the app, click "Choose File…", pick a text-based PDF or .txt file.
- The app sends the extracted text (first ~12k chars) to Gemini for a concise summary
  and a suggested folder path. The response is shown in a window.

API Key
-------
- Preferred: set the environment variable GEMINI_API_KEY
- Or: open config.txt and set GEMINI_API_KEY=YOUR_API_KEY_HERE
