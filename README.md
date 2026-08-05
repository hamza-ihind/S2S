# Sheet2Sound — PDF Sheet Music → Audio Converter

Sheet2Sound is a full-stack web application that takes a PDF of piano sheet music, performs Optical Music Recognition (OMR), and outputs playable audio (WAV/MP3) and MIDI files.

---

## 🏗️ Tech Stack

- **Backend**: Python (FastAPI), PyMuPDF, `oemer` (OMR engine), `music21`, FluidSynth + SoundFont (MIDI synthesis).
- **Frontend**: Next.js 14+ (App Router), TypeScript, Tailwind CSS, shadcn/ui components, Lucide icons.
- **Containerization**: Docker & Docker Compose.

---

## ⚡ Pipeline Architecture

```
PDF Upload (Next.js)
   └─► POST /api/upload (FastAPI)
        └─► POST /api/convert/{job_id}
             ├─► PDF → Page Images (PyMuPDF)
             ├─► OMR Parsing (oemer) → MusicXML
             ├─► MusicXML Cleanup (music21: quantize, fix ties)
             ├─► MusicXML → MIDI Conversion
             └─► Synthesis (FluidSynth + GM SoundFont) → WAV/MP3 Audio
```

---

## 🚀 Getting Started

### Prerequisites

- Node.js (v18+) & npm
- Python 3.10+
- FluidSynth (`apt-get install fluidsynth fluid-soundfont-gm` on Linux, or via Homebrew/Chocolatey)

### Option 1: Running with Docker Compose

```bash
docker-compose up --build
```
- Frontend will be live at `http://localhost:3000`
- Backend API docs live at `http://localhost:8000/docs`

### Option 2: Running Locally

#### 1. Backend Setup

```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 📡 API Endpoints

- `POST /api/upload`: Upload PDF file, receive `job_id`.
- `POST /api/convert/{job_id}`: Start processing job (supports `simulate_error` flag for error testing).
- `GET /api/status/{job_id}`: Poll job status (`queued`, `omr`, `synthesis`, `done`, `error`), stage message, and progress %.
- `GET /api/result/{job_id}`: Fetch playable audio URL, MIDI download URL, MusicXML download URL, and score metadata.

---

## ⚠️ Known Constraints & Notes

- OMR accuracy works best on clean, digital single/double-staff piano scores.
- Handwritten scores, complex dense orchestral layouts, or poor scans may reduce accuracy.
- Conversion runs asynchronously; typical processing time ranges from 10s to 2 mins depending on score complexity.
