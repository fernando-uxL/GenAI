====================================================
📘 AI FILE ORGANIZER (GEMINI API)
====================================================

🧠 OVERVIEW
------------
This program uses Google’s Gemini API to automatically:
- Summarize PDF or TXT documents.
- Suggest a folder name based on the document content.
- Move the file into that suggested folder.
- Record extracted keywords in a log file.
- Display results through a clean Tkinter interface (with HTML formatting).

----------------------------------------------------
⚙️ SYSTEM REQUIREMENTS
----------------------------------------------------
- Python 3.9 or newer
- Internet connection (for Gemini API)
- A valid Gemini API key

----------------------------------------------------
🧩 1. CREATE A PYTHON ENVIRONMENT
----------------------------------------------------

Option A — Using Conda (recommended)
------------------------------------
conda create -n AIOrganizer python=3.10
conda activate AIOrganizer

Option B — Using venv (if you don’t use Conda)
-----------------------------------------------
python -m venv AIOrganizer
AIOrganizer\Scripts\activate

You should now see (AIOrganizer) before your terminal prompt.

----------------------------------------------------
📦 2. INSTALL REQUIRED LIBRARIES
----------------------------------------------------
Run this command while your environment is active:

pip install google-generativeai fastapi uvicorn requests
