"""
FastAPI application for AI Recruitment System.
Provides endpoints for resume-to-jobs and job-to-candidates matching.
"""
import json
import os
from pathlib import Path
from typing import List, Optional
import numpy as np

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment variables only")

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.pipeline import MatchingPipeline
from core.reports import generate_match_summary, generate_candidate_feedback
from core.preprocessing import clean_text
from core.skills import extract_skills
from core.embeddings import EmbeddingGenerator

app = FastAPI(
    title="AI Recruitment System API",
    description="Intelligent job-resume matching using BERT/RoBERTa embeddings",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline
pipeline = MatchingPipeline()
embedding_generator = EmbeddingGenerator()

# Load data
DATA_DIR = Path(__file__).parent / "data"
JOBS_FILE = DATA_DIR / "jobs.json"
RESUMES_FILE = DATA_DIR / "resumes.json"

jobs_data: List[dict] = []
resumes_data: List[dict] = []


def load_data():
    """Load jobs and resumes data from JSON files."""
    global jobs_data, resumes_data
    
    try:
        if JOBS_FILE.exists():
            with open(JOBS_FILE, 'r', encoding='utf-8') as f:
                jobs_data = json.load(f)
            print(f"Loaded {len(jobs_data)} jobs from {JOBS_FILE}")
        else:
            print(f"Warning: {JOBS_FILE} not found. Please extract data from notebook.")
        
        if RESUMES_FILE.exists():
            with open(RESUMES_FILE, 'r', encoding='utf-8') as f:
                resumes_data = json.load(f)
            print(f"Loaded {len(resumes_data)} resumes from {RESUMES_FILE}")
        else:
            print(f"Warning: {RESUMES_FILE} not found. Please extract data from notebook.")
    
    except Exception as e:
        print(f"Error loading data: {e}")


# Load data on startup
@app.on_event("startup")
async def startup_event():
    load_data()


class MatchResponse(BaseModel):
    """Response model for match results."""
    rank: int
    similarity_score: float
    alignment_level: str
    recommendation: str
    why_fit: str
    matching_skills: List[str]
    missing_skills: List[str]
    extra_skills: List[str]
    skill_match_ratio: float
    gaps: str
    ai_summary: Optional[str] = None  # AI-generated match summary
    job_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    job_full_text: Optional[str] = None  # Full job description
    resume_id: Optional[str] = None
    category: Optional[str] = None
    resume_text: Optional[str] = None
    resume_full_text: Optional[str] = None  # Full resume text


class MatchesResponse(BaseModel):
    """Response model for matches endpoint."""
    matches: List[MatchResponse]
    model_used: str
    total_matches: int


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Recruitment System API",
        "version": "1.0.0",
        "endpoints": {
            "/resume-to-jobs": "POST - Match resume PDF to jobs",
            "/job-to-candidates": "POST - Match job PDF to candidates",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "jobs_loaded": len(jobs_data),
        "resumes_loaded": len(resumes_data),
        "models_available": {
            "bert": embedding_generator.bert_loaded,
            "roberta": embedding_generator.roberta_loaded
        }
    }


@app.post("/resume-to-jobs", response_model=MatchesResponse)
async def resume_to_jobs(
    file: UploadFile = File(...),
    model: str = Query("bert", regex="^(bert|roberta)$"),
    top_n: int = Query(10, ge=1, le=50)
):
    """
    Match a resume PDF against all jobs and return top N matches with summaries.
    
    Args:
        file: PDF file containing resume
        model: Embedding model to use ('bert' or 'roberta')
        top_n: Number of top matches to return
    
    Returns:
        JSON response with ranked matches and full summaries
    """
    if not jobs_data:
        raise HTTPException(status_code=503, detail="Jobs data not loaded. Please extract data from notebook.")
    
    try:
        # Process resume PDF
        resume_data = pipeline.process_resume_pdf(file)
        
        # Ensure Skills field is properly set (extract_skills returns 'skills' lowercase)
        if 'Skills' not in resume_data:
            resume_data['Skills'] = resume_data.get('skills', [])
        
        # Regenerate embedding with specified model if needed
        if model.lower() == 'roberta':
            resume_data['embedding'] = embedding_generator.generate_roberta_embedding(resume_data['clean_text'])
        else:
            resume_data['embedding'] = embedding_generator.generate_bert_embedding(resume_data['clean_text'])
        
        # Match resume to jobs (embeddings generated on-the-fly in pipeline)
        matches = pipeline.match_resume_to_jobs(resume_data, jobs_data, model, top_n)
        
        # Generate summaries for each match
        match_responses = []
        for match in matches:
            job = match['job_data']
            
            # Ensure resume_data has Skills for comparison
            if 'Skills' not in resume_data or not resume_data.get('Skills'):
                resume_data['Skills'] = resume_data.get('skills', [])
            
            # Generate match summary
            summary = generate_match_summary(
                job=job,
                resume=resume_data,
                similarity_score=match['similarity_score'],
                model_type=model,
                threshold=0.6
            )
            
            match_response = MatchResponse(
                rank=match['rank'],
                similarity_score=summary['similarity_score'],
                alignment_level=summary['alignment_level'],
                recommendation=summary['recommendation'],
                why_fit=summary['why_fit'],
                matching_skills=summary['matching_skills'],
                missing_skills=summary['missing_skills'],
                extra_skills=summary['extra_skills'],
                skill_match_ratio=summary['skill_match_ratio'],
                gaps=summary['gaps'],
                ai_summary=summary.get('ai_summary'),
                job_title=match.get('job_title'),
                company=match.get('company'),
                location=match.get('location'),
                description=match.get('description'),
                job_full_text=job.get('CombinedText') or job.get('JobDescription', '')  # Add full job text with all fields
            )
            match_responses.append(match_response)
        
        return MatchesResponse(
            matches=match_responses,
            model_used=model,
            total_matches=len(match_responses)
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/job-to-candidates", response_model=MatchesResponse)
async def job_to_candidates(
    file: UploadFile = File(...),
    model: str = Query("bert", regex="^(bert|roberta)$"),
    top_n: int = Query(10, ge=1, le=50)
):
    """
    Match a job posting PDF against all resumes and return top N matches with summaries.
    
    Args:
        file: PDF file containing job posting
        model: Embedding model to use ('bert' or 'roberta')
        top_n: Number of top matches to return
    
    Returns:
        JSON response with ranked matches and full summaries
    """
    if not resumes_data:
        raise HTTPException(status_code=503, detail="Resumes data not loaded. Please extract data from notebook.")
    
    try:
        # Process job PDF
        job_data = pipeline.process_job_pdf(file)
        
        # Ensure Skills field is properly set
        if 'Skills' not in job_data:
            job_data['Skills'] = job_data.get('skills', [])
        
        # Regenerate embedding with specified model if needed
        if model.lower() == 'roberta':
            job_data['embedding'] = embedding_generator.generate_roberta_embedding(job_data['clean_text'])
        else:
            job_data['embedding'] = embedding_generator.generate_bert_embedding(job_data['clean_text'])
        
        # Match job to resumes (embeddings generated on-the-fly in pipeline)
        matches = pipeline.match_job_to_candidates(job_data, resumes_data, model, top_n)
        
        # Debug: Log similarity scores (model-based only)
        print(f"=" * 60)
        print(f"JOB ANALYSIS (Model: {model.upper()}):")
        print(f"  Clean text length: {len(job_data['clean_text'])} chars")
        print(f"  Text preview: {job_data['clean_text'][:200]}...")
        print(f"  Job skills extracted: {len(job_data.get('skills', []))} skills")
        if job_data.get('skills'):
            print(f"  Job skills sample: {job_data['skills'][:10]}")
        print(f"=" * 60)
        if matches:
            print(f"RESULTS (Pure {model.upper()} similarity):")
            print(f"  Total matches: {len(matches)}")
            print(f"  Top match similarity: {matches[0]['similarity_score']}")
            print(f"  Top match category: {matches[0]['resume_data'].get('Category', 'N/A')}")
            print(f"  Top match skills: {matches[0]['resume_data'].get('Skills', [])[:5]}")
            print(f"  Category distribution: {[m['resume_data'].get('Category', 'N/A') for m in matches[:5]]}")
        
        # Generate summaries for each match
        match_responses = []
        for match in matches:
            resume = match['resume_data']
            
            # Ensure job_data has Skills for comparison
            if 'Skills' not in job_data or not job_data.get('Skills'):
                job_data['Skills'] = job_data.get('skills', [])
            
            # Ensure resume has Skills for comparison
            if 'Skills' not in resume or not resume.get('Skills'):
                resume['Skills'] = resume.get('Skills', [])
            
            # Generate match summary
            summary = generate_match_summary(
                job=job_data,
                resume=resume,
                similarity_score=match['similarity_score'],
                model_type=model,
                threshold=0.6
            )
            
            match_response = MatchResponse(
                rank=match['rank'],
                similarity_score=summary['similarity_score'],
                alignment_level=summary['alignment_level'],
                recommendation=summary['recommendation'],
                why_fit=summary['why_fit'],
                matching_skills=summary['matching_skills'],
                missing_skills=summary['missing_skills'],
                extra_skills=summary['extra_skills'],
                skill_match_ratio=summary['skill_match_ratio'],
                gaps=summary['gaps'],
                ai_summary=summary.get('ai_summary'),
                resume_id=match.get('resume_id'),
                category=match.get('category'),
                resume_text=resume.get('Resume_str', '')[:200] + '...' if resume.get('Resume_str') else None,
                resume_full_text=resume.get('Resume_str', ''),  # Full resume text
                job_full_text=job_data.get('CombinedText') or job_data.get('JobDescription', '')  # Full job text with all fields
            )
            match_responses.append(match_response)
        
        return MatchesResponse(
            matches=match_responses,
            model_used=model,
            total_matches=len(match_responses)
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

