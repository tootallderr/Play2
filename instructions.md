# LLM Media Player & Library Manager
## Overview
This project is an AI-powered media center that combines the functionality of a media player with intelligent, personality-based captions and smart playback features. It automatically monitors your media libraries, processes subtitles using LLMs into various "modes," and delivers a deeply customized watching experience.
## Features
* ✅ Auto-scans specified folders for new media
* ✅ Organizes TV shows, movies, and videos
* ✅ Retrieves metadata, posters, and descriptions (via TMDB API)
* ✅ Detects available subtitles (SRT/VTT) or extracts from video
* ✅ Caches everything locally for speed
* ✅ Transforms captions with real-time or batch processing using LLMs

* ✅ Full monitoring of libraries
* ✅ Comprehensive feature set
* ✅ Real-time or cached caption transformation using LLMs
* ✅ Personality-driven “modes”
* ✅ TiVo-style playback tools
* ✅ Auto-discovery, metadata fetching, and UI interaction

Here’s your full markdown file for use in **VS Code Agent Mode**, or just standard project bootstrapping.

---

```markdown
# 🎥 LLM Media Player & Library Manager

An AI-powered media center like Plex — but with a twist: intelligent, personality-based captions and smart playback features. Automatically monitors your media libraries, processes subtitles using LLMs into “modes” like *Weed Mode*, *Theo Von Commentary*, or *Fact-Checker Mode*, and delivers a deeply customized watching experience.

---

## 🧩 Features

### 🗂 Media Library Management
- Auto-scans specified folders for new media
- Organizes TV shows, movies, and videos
- Retrieves metadata, posters, and descriptions (via TMDB API)
- Detects available subtitles (SRT/VTT) or extracts from video
- Caches everything locally for speed

### 🎭 LLM Caption Modes
Transform captions with real-time or batch processing using LLMs:

| Mode             | Description |
|------------------|-------------|
| 🥦 **Weed Mode** | Converts captions to chill, slangy, stoner-friendly tone |
| 🎣 **Theo Von** | Retells scenes in Theo’s absurd Southern metaphors |
| 🥩 **Joey Diaz** | Explosive Bronx-style storytelling about each scene |
| 🧠 **Fact-Check** | Adds quick fact-checks to statements in captions |
| 🧾 **Trivia Mode** | Sprinkles in fun facts about people/places/topics |

### ⏯️ TiVo-style Playback
- Smart Skip (intros, ads, recaps)
- Resume from last watched position
- Instant replay ("go back 15s")
- Auto-chaptering for long media
- Voice assistant support (coming soon)

---

## 🛠️ Tech Stack

- **Frontend**: Next.js + TailwindCSS + video.js
- **Backend**: FastAPI (Python)
- **LLM**: OpenAI GPT-4, Claude, or local LLM (via API)
- **Subtitles**: `pysrt`, `ffmpeg`, `webvtt`
- **Database**: SQLite / PostgreSQL
- **File Watcher**: `watchdog` (Python)
- **Media Info**: `ffprobe`, `tmdbsimple`

---

## 📁 Project Structure

```

llm-media-player/
├── backend/
│   ├── api/                # FastAPI endpoints
│   ├── caption\_modes/      # Prompt templates + transformation logic
│   ├── media\_scanner/      # Directory monitoring, metadata fetching
│   ├── subtitle\_engine/    # Parser, LLM integration, caching
│   └── main.py             # Entrypoint
│
├── frontend/
│   ├── components/         # React/Next.js UI
│   ├── pages/              # Video player, library views
│   └── App.tsx
│
├── data/
│   ├── cache/              # Transformed subtitles
│   └── media\_library.json  # Scanned library data
│
├── requirements.txt
├── .env
└── README.md

````

---

## 📦 Setup Instructions (VS Code Agent Mode Ready)

### 1. Prerequisites

- Python 3.9+
- Node.js 18+
- `ffmpeg` and `ffprobe` installed
- OpenAI API key (or other LLM provider)
- VS Code + Dev Container support

---

### 2. Clone + Start in Dev Container

```bash
git clone https://github.com/yourname/llm-media-player
cd llm-media-player
code .  # Open in VS Code
````

Use **"Reopen in Container"** if prompted.

---

### 3. Create `.env` File

```env
OPENAI_API_KEY=your_openai_key_here
TMDB_API_KEY=your_tmdb_key
CAPTION_MODE_CACHE_DIR=./data/cache
WATCHED_DIRS=/mnt/media/movies,/mnt/media/tvshows
LLM_MODEL=gpt-4
```

---

### 4. Install Dependencies

**Backend:**

```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**

```bash
cd frontend
npm install
```

---

### 5. Run the App

Open 2 terminals:

**Backend:**

```bash
cd backend
uvicorn main:app --reload
```

**Frontend:**

```bash
cd frontend
npm run dev
```

Visit `http://localhost:3000`

---

## 🔁 How Caption Transformation Works

1. Detect subtitle file (or extract with ffmpeg)
2. Split into blocks (2–5s)
3. Feed blocks into LLM with selected mode prompt
4. Rebuild subtitle file (resynced or original timestamps)
5. Cache results and serve via UI

---

## ✨ Sample Caption Prompts

**Weed Mode Prompt:**

```text
Make this caption sound like a stoner is talking. Keep it chill, use slang, and remove complex words. Think Cheech and Chong watching a movie.
```

**Theo Von Prompt:**

```text
Retell this scene like Theo Von. Use southern metaphors, absurd analogies, weird personal stories. Stay funny, but vaguely make sense.
```

**Fact-Check Prompt:**

```text
For each sentence, add a short correction or confirmation of any claim. If something is historically or factually questionable, briefly clarify.
```

---

## 🧠 Caption Mode Creation Guide

To add your own mode:

1. Create a new file in `backend/caption_modes/your_mode.py`
2. Define:

```python
def transform_caption(text: str) -> str:
    prompt = f"...your instruction here..."
    return call_llm(prompt + text)
```

3. Register it in `main.py`

---

## 📈 Planned Features

* [ ] Auto-download subtitles if missing
* [ ] Narrator Audio Mode (AI voiceover of captions)
* [ ] Multi-user support w/ watch history
* [ ] Voice Commands: “Summarize scene in Joey Diaz mode”
* [ ] Companion mobile app

---

## 🧪 Developer Tips

* Use `watchdog` to rescan media folders automatically.
* Use `ffprobe` to get media metadata without loading the video.
* Cache caption mode results with timestamped hash keys.
* Use `websockets` to push progress updates to frontend in real time.

---

## 🤝 Acknowledgments

* Inspired by: Plex, Jellyfin, TiVo, Cheech & Chong, Theo Von, Joey Diaz
* Powered by: OpenAI, Python, Next.js, ffmpeg
* Made for: People who want their media player to have a personality.

---

## 📜 License

MIT License. Modify, remix, or go wild with it.

```

---
