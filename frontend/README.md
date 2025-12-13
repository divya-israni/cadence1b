# AI Recruitment System - Frontend

A modern, responsive frontend for the AI Recruitment System built with Next.js, React, and Tailwind CSS.

## Features

- 🎨 Modern, clean UI with Tailwind CSS
- 📄 PDF file upload with drag-and-drop support
- 🔍 Two matching modes:
  - Resume to Jobs: Find best job matches for a resume
  - Job to Candidates: Find best candidate matches for a job
- 🤖 Model selection: Choose between BERT and RoBERTa
- 📊 Detailed match results with:
  - Similarity scores
  - Alignment levels
  - Matching/missing/extra skills
  - Recommendations
  - Skill match ratios

## Setup

1. Install dependencies:
```bash
npm install
```

2. Make sure the FastAPI backend is running on `http://localhost:8000`

3. (Optional) Set custom API URL via environment variable:
```bash
export NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Run the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Main page
│   └── globals.css          # Global styles
├── components/
│   ├── FileUpload.tsx      # File upload component
│   ├── MatchCard.tsx       # Match result card
│   └── ModelSelector.tsx   # Model selection component
├── lib/
│   └── api.ts              # API client
└── public/                 # Static assets
```

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000` by default. The API endpoints used are:

- `POST /resume-to-jobs` - Match resume to jobs
- `POST /job-to-candidates` - Match job to candidates
- `GET /health` - Health check

## Technologies

- **Next.js 14** - React framework
- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Lucide React** - Icons

