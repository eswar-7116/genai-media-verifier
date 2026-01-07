# V.E.R.I.T.A.S

AI-powered deepfake detection for images and videos.

## What is this?

V.E.R.I.T.A.S (Verification Engine for Real-time Image and Text Authenticity Scanning) analyzes media files to detect potential deepfakes and manipulation. Upload an image or video, and get a detailed analysis of authenticity markers.

## Features

- Image and video deepfake detection
- Multiple detection methods (facial analysis, lighting, motion tracking, etc.)
- Real-time analysis with progress tracking
- Educational resources explaining how detection works
- Clean, modern UI

## Tech Stack

**Frontend**
- Next.js 16 with React 19
- TypeScript
- Tailwind CSS
- Three.js for 3D effects
- Framer Motion for animations

**Backend**
- FastAPI (Python)
- PyTorch + HuggingFace Transformers
- OpenCV and MediaPipe for video/image processing

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.10+

### Installation

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Frontend runs on `http://localhost:3000`
Backend runs on `http://localhost:8000`

## Project Structure

```
├── frontend/          # Next.js app
│   ├── app/          # Pages (landing, learn, upload)
│   ├── components/   # React components
│   └── public/       # Static assets
├── backend/
│   ├── main.py       # FastAPI server
│   ├── services/     # Detection logic
│   └── models/       # AI model definitions
```

## How It Works

The system uses 8 different detection methods:

1. **Facial Analysis** - Checks landmarks, symmetry, texture
2. **Motion Tracking** - Identifies unnatural movement in videos
3. **Lighting Analysis** - Evaluates shadow consistency
4. **Audio-Visual Sync** - Checks lip-sync accuracy
5. **Background Examination** - Looks for edge artifacts
6. **Frequency Analysis** - Detects GAN fingerprints
7. **Eye/Blink Patterns** - Analyzes natural eye behavior
8. **Metadata Check** - Examines file properties

Each method contributes to an overall confidence score.

## API

**Analyze Image:**
```bash
POST /analyze-image
Content-Type: multipart/form-data
```

**Analyze Video:**
```bash
POST /analyze-video
Content-Type: multipart/form-data
```

Full API docs available at `/docs` when running the backend.

## Environment Variables

**Frontend** (`.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend** (`.env`):
```
MODEL_CACHE_DIR=./models_cache
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=100000000
```

## Notes

- First run downloads AI models automatically (can take a few minutes)
- Video analysis takes longer than images
- Large files might timeout - adjust `MAX_FILE_SIZE` if needed
- The `models_cache/` and `uploads/` directories are gitignored

## Contributing

PRs welcome. Please test locally before submitting.

## License

MIT