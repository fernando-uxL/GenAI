
import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import threading
import time
import os
import sys
from fastapi import FastAPI, UploadFile
import uvicorn
import google.generativeai as genai
from PyPDF2 import PdfReader
import io

APP_TITLE = "AI Summarizer (Gemini API)"
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}/upload"
CONFIG_FILENAME = "config.txt"

# --------------------- Config & API key ---------------------
def load_api_key():
    # Priority 1: environment variable
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key
    # Priority 2: config.txt in the same folder as the executable/script
    try:
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        cfg_path = os.path.join(base_dir, CONFIG_FILENAME)
        if os.path.exists(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.upper().startswith("GEMINI_API_KEY="):
                        return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return ""

API_KEY = load_api_key()
if not API_KEY:
    # Show a message and exit gracefully
    tk.Tk().withdraw()
    messagebox.showerror(
        APP_TITLE,
        "Missing Gemini API key.\n\nPlease set GEMINI_API_KEY in your environment, "
        "or create a file named 'config.txt' next to this app with the line:\n\n"
        "GEMINI_API_KEY=your_api_key_here"
    )
    sys.exit(1)

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# --------------------- FastAPI backend ---------------------
app = FastAPI()

def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    text = ""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception:
        # Any PDF read error will just yield empty -> handled upstream
        pass
    return text.strip()

@app.post("/upload")
async def upload(file: UploadFile):
    content = await file.read()
    text = ""
    if file.filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf_bytes(content)
    else:
        # fallback for txt and other simple formats
        try:
            text = content.decode("utf-8", errors="ignore")
        except Exception:
            text = ""

    if not text:
        return {"summary": "❌ Could not extract text from this file (is it a scanned image-PDF?)."}

    # Keep prompt size reasonable for quotas
    chunk = text[:12000]
    prompt = (
        "Summarize this document concisely, then suggest a folder/subfolder name. "
        'Return ONLY valid JSON as: {"summary": "...", "folder": "..."}\n\n'
        f"{chunk}"
    )
    try:
        response = model.generate_content(prompt)
        result_text = response.text or ""
    except Exception as e:
        result_text = f"Error calling Gemini API: {e}"

    return {"summary": result_text}

def start_backend():
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT, log_level="error")

# --------------------- Tkinter GUI ---------------------
def run_gui():
    def summarize_file():
        path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[("PDF files", "*.pdf"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "rb") as f:
                r = requests.post(SERVER_URL, files={"file": f})
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Failed to contact local AI server.\n\n{e}")
            return

        if r.status_code == 200:
            msg = r.json().get("summary", "No summary returned.")
            # Show in a scrollable window if it's long
            top = tk.Toplevel(root)
            top.title("Summary")
            text = tk.Text(top, wrap="word", height=30, width=90)
            text.insert("1.0", msg)
            text.config(state="disabled")
            text.pack(expand=True, fill="both")
        else:
            messagebox.showerror(APP_TITLE, f"Server returned HTTP {r.status_code}")

    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry("420x160")

    lbl = tk.Label(root, text="Select a text-based PDF or TXT file to summarize.")
    lbl.pack(pady=(20,10))

    btn = tk.Button(root, text="Choose File…", command=summarize_file, width=20)
    btn.pack(pady=5)

    note = tk.Label(root, text="Tip: Set GEMINI_API_KEY (env) or edit config.txt", fg="#444")
    note.pack(pady=(10,10))

    root.mainloop()

if __name__ == "__main__":
    # Start backend in background thread
    t = threading.Thread(target=start_backend, daemon=True)
    t.start()
    time.sleep(1.5)
    run_gui()
