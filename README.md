# PlanRead

PlanRead is a web application that helps students read and understand construction plan drawings. Users upload a drawing, and the app detects text and symbols, then explains construction terms using retrieval-augmented LLM responses. An optional Vision module uses GPT-4o to analyze selected drawing regions.

## Features

- **OCR Text Detection** — Finds and reads text labels using PaddleOCR
- **Circle/Symbol Detection** — Identifies circled callouts and reference symbols using OpenCV
- **AI Explanations** — Sends detected text to GPT-4o for plain-language explanations
- **RAG Dictionary Lookup** — Matches terms against the RSMeans Illustrated Construction Dictionary for definitions and images
- **Visual Analysis (Vision, optional)** — Uses GPT-4o Vision to analyze full or partial drawings
- **Activity Logging** — Records user interactions for research/troubleshooting

## Project Structure

```
PlanRead/
├── launcher.py                  # Main entry point — starts backend + opens browser
├── backend/                     # Python FastAPI server
│   ├── app.py                   # FastAPI app setup, routes, static file serving
│   ├── requirements.txt         # Python dependencies
│   ├── routes/
│   │   ├── detect.py            # OCR + circle detection endpoint
│   │   ├── llm.py               # LLM explanation endpoint
│   │   ├── llm_images.py        # LLM with image search endpoint
│   │   ├── vlm.py               # GPT-4o Vision analysis endpoint
│   │   ├── auth.py              # Login / session management
│   │   ├── regions_detect.py    # Region-specific detection
│   │   └── activity_log.py      # Activity logging endpoint
│   └── services/
│       ├── rag_service.py       # RAG dictionary lookup
│       └── google_images.py     # Google image search service
├── app/                         # React + Vite frontend
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx              # Main application component
│       ├── main.jsx             # React entry point
│       ├── config.js            # API base URL config
│       ├── components/
│       │   ├── ImageCanvas.jsx  # Canvas for drawing interaction
│       │   ├── ImageUploader.jsx
│       │   ├── Loginform.jsx
│       │   ├── Page.jsx         # Page navigation component
│       │   ├── Popup.jsx        # Term explanation popup
│       │   ├── ShapeOverlay.jsx # Detected shape rendering
│       │   ├── VLMPanel.jsx     # Vision analysis panel
│       │   └── ZoomControls.jsx
│       ├── hooks/               # Custom React hooks
│       ├── styles/              # CSS stylesheets
│       └── utils/
│           └── activityLogger.js
├── packages/                    # Reusable Python packages
│   ├── construction_ocr/                  # PaddleOCR text detection pipeline
│   ├── construction_circle_detector/      # OpenCV circle detection
│   ├── construction_llm_explainer/        # LLM explanation logic
│   ├── construction_plan_rag/             # RAG + dictionary term lookup
│   └── construction_vlm_analyzer/         # GPT-4o Vision analysis
├── data/                        # Reference data (not in repo, see below)
│   ├── Construction-Vocabulary.pdf
│   ├── RSMeans Illustrated Construction Dictionary.pdf
│   └── RSMeans_Illustrated_Construction_Dictionary/
│       ├── terms.json           # Extracted dictionary terms
│       └── images/              # Extracted page images
├── docs/                        # Local documentation (not in repo)
├── samples/                     # Bundled 4-sheet sample plan set (see samples/README.md)
├── CONTRIBUTORS.md              # Non-author contributor credits
├── DOCKER_SETUP.md              # Docker deployment/setup guide
└── LICENSE                      # Project license (MIT)
```

> **Note:** The `data/` and `docs/` folders are not included in the GitHub repo, except for the small sample term dictionary described below. See the Data Setup section for details.

## Prerequisites

Make sure you have these installed:

- **Python 3.10+** — Check with `python --version`
- **Node.js 18+** — Check with `node --version`
- **Git** — For cloning the repository

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/ssai-lab/PlanRead.git
cd PlanRead
```

### 2. Set Up the Python Backend

Create a virtual environment and install dependencies.

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r backend/requirements.txt
```

**Mac / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
```

Install the local packages in editable mode:
```bash
pip install -e packages/construction_ocr
pip install -e packages/construction_circle_detector
pip install -e packages/construction_llm_explainer
pip install -e packages/construction_plan_rag
pip install -e packages/construction_vlm_analyzer
```

> **Mac users:** If you run into issues with `opencv-python`, try `brew install opencv` first.

### 3. Set Up the React Frontend

```bash
cd app
npm ci
npm run build
cd ..
```

This creates a `dist/` folder inside `app/` that the backend serves automatically.

> If `npm ci` doesn't work, try deleting `node_modules/` and running `npm install` followed by `npm run build`.

### 4. Data Setup

The full `data/` folder is not included in the repo: the files are large and the
dictionary is licensed third-party material.

**Works out of the box.** A small sample dictionary of 24 common plan-reading terms
ships with the repo at `data/RSMeans_Illustrated_Construction_Dictionary/terms.json`,
so the retrieval-augmented explanation path works immediately after a fresh clone.
The sample contains only definitions written for this project.

A project-authored sample glossary, `data/PlanRead-Sample-Glossary.pdf`, also ships
so the vector-search tier has a corpus to ingest on first use. It is a three-page
document written for this project (MIT licensed), not the RSMeans dictionary: it
gives the RAG pipeline real text to chunk and embed, so retrieval can be exercised
without the licensed source. Delete it once you install the full dictionary if you
prefer to index only that.

**To use the full dictionary instead:**

1. Create a `data/` folder in the project root if it does not already exist
2. Place the following files in it:
   - `Construction-Vocabulary.pdf`
   - `RSMeans Illustrated Construction Dictionary.pdf`
3. Replace `data/RSMeans_Illustrated_Construction_Dictionary/terms.json` with the full
   term list and add:
   - `images/` — Extracted page images organized by page number

> Ask a team member for these files or generate them from the source PDFs. Both
> `terms.json` and `images/` are gitignored, so replacing the sample will not affect
> the repository.

A four-sheet sample plan set ships in `samples/plan-set/` for the upload and
detection paths — see `samples/README.md` for the sheet list and the note on its
third-party licence.

### 5. API Keys

Create a `.env` file in the **project root** (recommended) with your API keys:

```ini
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_CSE_API_KEY=your_google_custom_search_api_key_here
GOOGLE_CSE_CX=your_google_custom_search_engine_id_here
```

- The recommended place for `.env` is the project root.
- The launcher will also check `backend/.env` if not found in the root, so both work (root takes precedence).
- Supported key names (do not change):
  - `OPENAI_API_KEY`
  - `GOOGLE_CSE_API_KEY`
  - `GOOGLE_CSE_CX`
  - `GROQ_API_KEY` (optional fallback)

You'll need:
- An **OpenAI API key** from [platform.openai.com](https://platform.openai.com) — used for GPT-4o text explanations and Vision analysis
- A **Google Custom Search API key + Search Engine ID** from [Google Cloud Console](https://console.cloud.google.com) — used for image search

Do **not** commit any `.env` file to Git.

## Running the App

Make sure your virtual environment is activated, then:

**Windows:**
```powershell
python launcher.py
```

**Mac / Linux:**
```bash
python3 launcher.py
```

The launcher will:
1. Check that all dependencies and API keys are set up
2. Start the backend server at `http://[IP_ADDRESS]:8001`
3. Open the app in your default browser

## How It Works

When you upload a construction drawing:

1. The **frontend** sends the image to the backend
2. **PaddleOCR** detects all readable text on the drawing
3. **OpenCV** finds circled callout symbols
4. Detected items are shown as clickable overlays on the image
5. Clicking a text label sends it to **GPT-4o**, which explains the term using construction domain knowledge
6. The **RAG service** searches the construction dictionary for matching terms and images
7. You can also select a region and run **GPT-4o Vision analysis** for a detailed breakdown of that area

## Troubleshooting

| Problem | Solution |
|---|---|
| "No text detected" | Make sure PaddleOCR is installed properly. First run may be slow (downloading models). |
| "Module not found" | Activate your virtual environment first. Make sure packages are installed with `pip install -e`. |
| "Missing API keys" | Check your `.env` file exists in the project root (preferred) or `backend/`, and has all required keys. |
| OpenCV errors on Mac | Run `brew install opencv`. |
| Slow on M1/M2/M3 Mac | PaddleOCR uses CPU mode by default. This is normal. |
