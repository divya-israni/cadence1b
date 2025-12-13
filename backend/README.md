# AI Recruitment System - FastAPI Backend

Production-ready FastAPI backend for intelligent job-resume matching using BERT/RoBERTa embeddings.

## Features

- **PDF Parsing**: Extract text from resume and job posting PDFs
- **Intelligent Matching**: BERT and RoBERTa semantic embeddings for accurate matching
- **Skill Extraction**: Automatic skill identification using spaCy NLP
- **Match Summaries**: Comprehensive reports with alignment levels, skill overlap, and recommendations
- **Bidirectional Matching**: 
  - Resume → Jobs: Find best jobs for a candidate
  - Job → Candidates: Find best candidates for a job

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

### 3. Extract Data from Notebook

The data files (`data/jobs.json` and `data/resumes.json`) should be extracted from the notebook cache. 

**Option 1: Run the extraction script (recommended)**

From the project root directory, run:

```bash
cd backend
python extract_data.py
```

**Option 2: Run from notebook**

Add this cell to your notebook and run it:

```python
import sys
sys.path.append('backend')
from extract_data import extract_data
extract_data()
```

**Option 3: Manual extraction**

If the script doesn't work, manually extract from notebook:

```python
import pandas as pd
import json
from pathlib import Path

# Load from notebook cache
df_jobs = pd.read_pickle('cache/df_jobs_clean.pkl')
df_resumes = pd.read_pickle('cache/df_resumes_clean.pkl')

# Convert to JSON
jobs_json = df_jobs.to_dict('records')
resumes_json = df_resumes.to_dict('records')

# Save to backend/data
Path('backend/data').mkdir(parents=True, exist_ok=True)
json.dump(jobs_json, open('backend/data/jobs.json', 'w'), indent=2, default=str)
json.dump(resumes_json, open('backend/data/resumes.json', 'w'), indent=2, default=str)
```

### 4. Run the Server

```bash
cd backend
python app.py
```

Or using uvicorn directly:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check

```bash
GET /health
```

Returns system status and data loading information.

### Resume to Jobs

```bash
POST /resume-to-jobs
```

**Parameters:**
- `file`: PDF file (multipart/form-data)
- `model`: Query parameter - 'bert' or 'roberta' (default: 'bert')
- `top_n`: Query parameter - Number of matches (default: 10, max: 50)

**Example:**
```bash
curl -X POST "http://localhost:8000/resume-to-jobs?model=bert&top_n=10" \
  -F "file=@resume.pdf"
```

**Response:**
```json
{
  "matches": [
    {
      "rank": 1,
      "similarity_score": 0.823,
      "alignment_level": "Excellent Match",
      "recommendation": "Strongly Recommended",
      "why_fit": "Candidate demonstrates 82.3% semantic alignment...",
      "matching_skills": ["python", "machine learning"],
      "missing_skills": ["docker"],
      "extra_skills": ["javascript"],
      "skill_match_ratio": 0.75,
      "gaps": "Missing 1 key skills: docker",
      "job_title": "Software Engineer",
      "company": "Tech Corp",
      "location": "San Francisco, CA",
      "description": "We are looking for..."
    }
  ],
  "model_used": "bert",
  "total_matches": 10
}
```

### Job to Candidates

```bash
POST /job-to-candidates
```

**Parameters:**
- `file`: PDF file (multipart/form-data)
- `model`: Query parameter - 'bert' or 'roberta' (default: 'bert')
- `top_n`: Query parameter - Number of matches (default: 10, max: 50)

**Example:**
```bash
curl -X POST "http://localhost:8000/job-to-candidates?model=roberta&top_n=10" \
  -F "file=@job_posting.pdf"
```

**Response:**
```json
{
  "matches": [
    {
      "rank": 1,
      "similarity_score": 0.856,
      "alignment_level": "Excellent Match",
      "recommendation": "Strongly Recommended",
      "why_fit": "Candidate demonstrates 85.6% semantic alignment...",
      "matching_skills": ["python", "machine learning", "tensorflow"],
      "missing_skills": [],
      "extra_skills": ["javascript", "react"],
      "skill_match_ratio": 0.9,
      "gaps": "No significant skill gaps identified.",
      "resume_id": "12345",
      "category": "IT",
      "resume_text": "Experienced software engineer with..."
    }
  ],
  "model_used": "roberta",
  "total_matches": 10
}
```

## Project Structure

```
backend/
├── app.py                 # FastAPI main application
├── requirements.txt       # Python dependencies
├── core/
│   ├── pdf_parser.py     # PDF text extraction
│   ├── preprocessing.py   # Text cleaning and normalization
│   ├── skills.py          # Skill extraction
│   ├── embeddings.py      # BERT/RoBERTa embedding generation
│   ├── similarity.py      # Cosine similarity calculation
│   ├── pipeline.py        # End-to-end processing pipeline
│   └── reports.py         # Match summary and feedback generation
└── data/
    ├── jobs.json          # Job postings data
    └── resumes.json       # Resumes data
```

## Alignment Levels

The system uses the following thresholds (matching notebook logic):

- **Excellent Match**: similarity_score >= 0.75 AND skill_match_ratio >= 0.7
- **Good Match**: similarity_score >= 0.65 AND skill_match_ratio >= 0.5
- **Moderate Match**: similarity_score >= 0.6 AND skill_match_ratio >= 0.3
- **Weak Match**: Otherwise

## Model Information

- **BERT**: `all-MiniLM-L6-v2` (384 dimensions)
- **RoBERTa**: `all-distilroberta-v1` (768 dimensions)

Models are lazy-loaded on first use to improve startup time.

## Error Handling

- **400 Bad Request**: Invalid PDF file or malformed request
- **503 Service Unavailable**: Data not loaded or models unavailable
- **500 Internal Server Error**: Processing errors

## Performance Notes

- Models are cached after first load
- Embeddings are generated in batches for efficiency
- Consider using GPU for faster embedding generation in production

## Development

To run with auto-reload:

```bash
uvicorn app:app --reload
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

