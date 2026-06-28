# Auto-Editing 🎬

Automatic video editing tool for content creators.

## Features ✨
- Auto-trimming silent parts
- Auto-caption generation using Whisper AI
- Background music mixing
- Royalty-free B-roll insertion
- Video format conversion
- Quality optimization

## Tech Stack 🛠️
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Backend:** Python (FastAPI)
- **Video Processing:** FFmpeg, MoviePy
- **AI:** OpenAI Whisper
- **Deployment:** Cloudflare Pages, Docker

## Setup Instructions 🚀

### Prerequisites
- Python 3.9+
- Node.js 16+
- FFmpeg
- Docker (optional)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/auto-editing.git
cd auto-editing
```

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Install FFmpeg:
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

4. Run the backend server:
```bash
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

5. Open frontend in browser:
```bash
cd frontend
# Simply open index.html in browser or use Live Server
```

## Deployment 🌐

### Frontend (Cloudflare Pages)
1. Push code to GitHub
2. Connect repository to Cloudflare Pages
3. Set build output directory: `frontend`
4. Deploy

### Backend (VPS/Docker)
```bash
cd backend
docker build -t auto-editing-backend .
docker run -p 8000:8000 auto-editing-backend
```

## API Documentation 📚
See [docs/API.md](docs/API.md) for complete API documentation.

## License 📄
MIT License - see [LICENSE](LICENSE) file for details.

## Contributing 🤝
Contributions are welcome! Please read [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) first.
