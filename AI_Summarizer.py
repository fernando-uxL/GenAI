import os
import sys
import io
import json
import time
import shutil
import threading
import requests
import tkinter as tk
from tkinter import filedialog, messagebox
from fastapi import FastAPI, UploadFile
import uvicorn
import google.generativeai as genai
from PyPDF2 import PdfReader
from tkhtmlview import HTMLLabel  # 👈 HTML rendering support

# ======================
# CONFIGURATION
# ======================
APP_TITLE = "AI File Organizer (Gemini API)"
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}/upload"
CONFIG_FILENAME = "config.txt"

# --------------------- Load API Key ---------------------
def load_api_key():
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key
    try:
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        cfg_path = os.path.join(base_dir, CONFIG_FILENAME)
        if os.path.exists(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip() and not line.startswith("#") and "GEMINI_API_KEY=" in line:
                        return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return ""

API_KEY = load_api_key()
if not API_KEY:
    tk.Tk().withdraw()
    messagebox.showerror(
        APP_TITLE,
        "Missing Gemini API key.\n\nPlease set GEMINI_API_KEY in your environment, "
        "or create a 'config.txt' file with:\n\nGEMINI_API_KEY=your_api_key_here"
    )
    sys.exit(1)

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# ======================
# FASTAPI BACKEND
# ======================
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
        pass
    return text.strip()

@app.post("/upload")
async def upload(file: UploadFile):
    content = await file.read()
    text = ""
    if file.filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf_bytes(content)
    else:
        try:
            text = content.decode("utf-8", errors="ignore")
        except Exception:
            text = ""

    if not text:
        return {"result": "❌ Could not extract text (maybe scanned image-PDF?)."}

    chunk = text[:12000]
    prompt = (
        "Analyze this document and return JSON only.\n"
        'Format: {"summary":"...", "suggested_folder":"...", "keywords":["...","...","..."]}\n\n'
        f"{chunk}"
    )

    try:
        response = model.generate_content(prompt)
        return {"result": response.text}
    except Exception as e:
        return {"result": f"Error calling Gemini API: {e}"}

def start_backend():
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT, log_level="error")

# ======================
# GUI FRONTEND
# ======================
def run_gui():
    # ---------- Main Window ----------
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry("420x200")
    root.configure(bg="#f2f2f2")

    def process_file():
        path = filedialog.askopenfilename(
            title="Select a PDF or TXT file",
            filetypes=[("PDF files", "*.pdf"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "rb") as f:
                r = requests.post(SERVER_URL, files={"file": f})
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Failed to contact backend.\n\n{e}")
            return

        if r.status_code != 200:
            messagebox.showerror(APP_TITLE, f"Server returned HTTP {r.status_code}")
            return

        result = r.json().get("result", "")

        # --- Clean up model output for safe JSON parsing ---
        cleaned = result.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json", "", 1).strip()
        cleaned = cleaned.replace("```", "").strip()

        try:
            data = json.loads(cleaned)
        except Exception:
            try:
                start = cleaned.find("{")
                end = cleaned.rfind("}")
                if start != -1 and end != -1:
                    repaired = cleaned[start:end+1]
                    data = json.loads(repaired)
                else:
                    raise ValueError("No JSON object found")
            except Exception:
                messagebox.showerror(APP_TITLE, f"AI did not return valid JSON even after cleaning:\n\n{cleaned}")
                return

        summary = data.get("summary", "No summary.")
        folder_name = data.get("suggested_folder", "Unsorted")
        keywords = data.get("keywords", [])

        # ---------- Move File ----------
        base_dir = os.path.dirname(path)
        new_folder = os.path.join(base_dir, folder_name)
        os.makedirs(new_folder, exist_ok=True)
        new_path = os.path.join(new_folder, os.path.basename(path))
        shutil.move(path, new_path)

        # ---------- Write to TXT Log ----------
        log_path = os.path.join(base_dir, "AI_Organized_Log.txt")
        with open(log_path, "a", encoding="utf-8") as log:
            log.write(f"File: {os.path.basename(path)}\n")
            log.write(f"Path: {new_path}\n")
            log.write(f"Keywords: {', '.join(keywords)}\n")
            log.write("-" * 40 + "\n")

        # ---------- Display Result (HTML rendering) ----------
        top = tk.Toplevel(root)
        top.title("AI Summary and Folder Suggestion")

        html_display = f"""
        <body style='font-family:Segoe UI; background-color:#f9f9f9; color:#333; padding:15px;'>
        <h2>📄 Summary</h2>
        <p>{summary}</p>
        <h3>📁 Suggested Folder:</h3>
        <p><b>{folder_name}</b></p>
        <h3>🔑 Keywords:</h3>
        <ul>{"".join(f"<li>{k}</li>" for k in keywords)}</ul>
        <p style='color:green;'>✅ File moved to: {new_path}</p>
        </body>
        """

        html_label = HTMLLabel(top, html=html_display, width=90, background="#f9f9f9")
        html_label.pack(padx=15, pady=15, fill="both", expand=True)

    # ---------- UI Layout ----------
    lbl = tk.Label(
        root,
        text="📄 Select a PDF or TXT file to summarize & auto-organize",
        bg="#f2f2f2",
        fg="#222",
        font=("Segoe UI", 10)
    )
    lbl.pack(pady=(25, 10))

    btn = tk.Button(
        root,
        text="Choose File…",
        command=process_file,
        bg="#0078D7",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        width=20,
        height=1
    )
    btn.pack(pady=5)

    note = tk.Label(
        root,
        text="AI will summarize, suggest a folder, and log keywords.",
        bg="#f2f2f2",
        fg="#555",
        font=("Segoe UI", 8)
    )
    note.pack(pady=(15, 10))

    root.mainloop()

# ======================
# MAIN
# ======================
if __name__ == "__main__":
    print("Starting AI File Organizer...")
    t = threading.Thread(target=start_backend, daemon=True)
    t.start()
    time.sleep(1.5)
    print("Launching GUI...")
    run_gui()
