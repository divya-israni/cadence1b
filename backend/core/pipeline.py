"""
End-to-end processing pipeline for resume and job matching.
"""
from typing import Dict, List, Optional
import spacy
from fastapi import UploadFile

from .pdf_parser import parse_pdf
from .preprocessing import clean_text as clean_text_func, lemmatize_text, extract_requirements_section
from .skills import extract_skills
from .embeddings import EmbeddingGenerator
from .similarity import find_top_matches
from .category_matcher import infer_job_category


class MatchingPipeline:
    """
    Pipeline for processing PDFs and performing matching operations.
    """
    
    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()
        self.nlp_model = None
        self._load_nlp_model()
    
    def _load_nlp_model(self):
        """Load spaCy model."""
        try:
            self.nlp_model = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Skill extraction will be limited.")
            self.nlp_model = None
    
    def process_resume_pdf(self, pdf_file: UploadFile) -> Dict:
        """
        Process resume PDF: parse, clean, extract skills, generate embedding.
        
        Args:
            pdf_file: Uploaded PDF file
        
        Returns:
            Dictionary with processed data:
            {
                'text': str,
                'clean_text': str,
                'skills': List[str],
                'embedding': np.ndarray
            }
        """
        # Parse PDF
        raw_text = parse_pdf(pdf_file)
        
        # Clean text
        cleaned_text = clean_text_func(raw_text)
        
        # Extract skills
        skills = extract_skills(cleaned_text, self.nlp_model) if self.nlp_model else []
        
        # Generate embedding (default to BERT)
        embedding = self.embedding_generator.generate_bert_embedding(cleaned_text)
        
        return {
            'text': raw_text,
            'clean_text': cleaned_text,
            'skills': skills,
            'embedding': embedding
        }
    
    def process_job_pdf(self, pdf_file: UploadFile) -> Dict:
        """
        Process job posting PDF: parse, clean, extract skills, generate embedding.
        Focuses on requirements section to improve matching with technical candidates.
        
        Args:
            pdf_file: Uploaded PDF file
        
        Returns:
            Dictionary with processed data:
            {
                'text': str,
                'clean_text': str (requirements-focused),
                'full_clean_text': str (full text),
                'skills': List[str],
                'embedding': np.ndarray
            }
        """
        # Parse PDF
        raw_text = parse_pdf(pdf_file)
        
        # Extract requirements section first (before cleaning) to preserve structure
        requirements_text = extract_requirements_section(raw_text)
        
        # Clean text (both full and requirements-focused)
        cleaned_text = clean_text_func(raw_text)
        cleaned_requirements = clean_text_func(requirements_text)
        
        # Use requirements-focused text for embedding (better for technical matching)
        # But keep full text for display
        text_for_embedding = cleaned_requirements if cleaned_requirements and len(cleaned_requirements) > 100 else cleaned_text
        
        # Extract skills from requirements-focused text
        skills = extract_skills(text_for_embedding, self.nlp_model) if self.nlp_model else []
        
        # Generate embedding (default to BERT) - will be regenerated with specified model in endpoint
        embedding = None  # Will be generated in endpoint with specified model
        
        return {
            'text': raw_text,
            'clean_text': text_for_embedding,  # Use requirements-focused text for embedding
            'full_clean_text': cleaned_text,  # Keep full text for reference
            'skills': skills,
            'embedding': embedding
        }
    
    def match_resume_to_jobs(
        self,
        resume_data: Dict,
        jobs_data: List[Dict],
        model: str = 'bert',
        top_n: int = 10
    ) -> List[Dict]:
        """
        Match resume against all jobs and return top N matches.
        
        Args:
            resume_data: Processed resume data with embedding
            jobs_data: List of job dictionaries (embeddings generated on-the-fly)
            model: 'bert' or 'roberta'
            top_n: Number of top matches to return
        
        Returns:
            List of match dictionaries with ranking and scores
        """
        resume_embedding = resume_data['embedding']
        
        # Generate embeddings for all jobs using batch processing (much faster)
        job_texts = []
        for job in jobs_data:
            clean_text = job.get('CleanText', '')
            if not clean_text:
                # Fallback: generate clean text if not present
                combined_text = (
                    str(job.get('Title', '')) + ' ' +
                    str(job.get('JobDescription', '')) + ' ' +
                    str(job.get('JobRequirment', '')) + ' ' +
                    str(job.get('RequiredQual', ''))
                )
                clean_text = clean_text_func(combined_text)
            job_texts.append(clean_text)
        
        # Generate embeddings in batch (much faster than one-by-one)
        print(f"Generating {model.upper()} embeddings for {len(job_texts)} jobs in batch...")
        if model.lower() == 'roberta':
            job_embeddings = self.embedding_generator.generate_roberta_embeddings_batch(job_texts, batch_size=32)
        else:
            job_embeddings = self.embedding_generator.generate_bert_embeddings_batch(job_texts, batch_size=32)
        
        # Find top matches (filter out very poor matches with min_similarity=0.2)
        top_matches = find_top_matches(resume_embedding, job_embeddings, top_n, min_similarity=0.2)
        
        # Build results
        results = []
        for rank, (job_idx, similarity_score) in enumerate(top_matches, 1):
            job = jobs_data[job_idx]
            
            # Ensure job has CleanText and Skills for report generation
            if 'CleanText' not in job or not job.get('CleanText'):
                combined_text = (
                    str(job.get('Title', '')) + ' ' +
                    str(job.get('JobDescription', '')) + ' ' +
                    str(job.get('JobRequirment', '')) + ' ' +
                    str(job.get('RequiredQual', ''))
                )
                job['CleanText'] = clean_text_func(combined_text)
            
            if 'Skills' not in job or not job.get('Skills'):
                job['Skills'] = extract_skills(job.get('CleanText', ''), self.nlp_model) if self.nlp_model else []
            
            results.append({
                'rank': rank,
                'job_index': job_idx,
                'similarity_score': round(similarity_score, 3),
                'job_title': job.get('Title', 'N/A'),
                'company': job.get('Company', 'N/A'),
                'location': job.get('Location', 'N/A'),
                'description': job.get('JobDescription', '')[:200] + '...' if job.get('JobDescription') else 'N/A',
                'job_data': job  # Full job data for report generation
            })
        
        return results
    
    def match_job_to_candidates(
        self,
        job_data: Dict,
        resumes_data: List[Dict],
        model: str = 'bert',
        top_n: int = 10
    ) -> List[Dict]:
        """
        Match job against all resumes and return top N matches.
        NOW WITH CATEGORY FILTERING for better relevance.
        
        Args:
            job_data: Processed job data with embedding
            resumes_data: List of resume dictionaries (embeddings generated on-the-fly)
            model: 'bert' or 'roberta'
            top_n: Number of top matches to return
        
        Returns:
            List of match dictionaries with ranking and scores
        """
        job_embedding = job_data['embedding']
        
        # STEP 1: Infer job category from text
        job_text = job_data.get('clean_text', '') or job_data.get('CombinedText', '')
        inferred_categories = infer_job_category(job_text)
        
        print(f"=" * 60)
        print(f"JOB CATEGORY INFERENCE:")
        print(f"  Inferred categories: {inferred_categories[:3] if inferred_categories else 'None'}")
        print(f"  Job text preview: {job_text[:150]}...")
        print(f"=" * 60)
        
        # STEP 2: Filter resumes by relevant categories (if categories detected)
        if inferred_categories:
            # Get top 2 most relevant categories
            relevant_categories = inferred_categories[:2]
            filtered_resumes = [
                resume for resume in resumes_data 
                if resume.get('Category', '').upper() in [cat.upper() for cat in relevant_categories]
            ]
            
            print(f"CATEGORY FILTERING:")
            print(f"  Total resumes: {len(resumes_data)}")
            print(f"  Filtered to categories {relevant_categories}: {len(filtered_resumes)} resumes")
            
            # If filtering is too restrictive, fall back to all resumes
            if len(filtered_resumes) < 5:
                print(f"  ⚠️ Too few matches ({len(filtered_resumes)}), using all resumes")
                filtered_resumes = resumes_data
        else:
            print(f"  No clear category detected, using all {len(resumes_data)} resumes")
            filtered_resumes = resumes_data
        
        # STEP 3: Generate embeddings for filtered resumes
        resume_categories = []
        resume_texts = []
        resume_indices = []  # Track original indices
        
        print(f"Preparing {len(filtered_resumes)} resumes for {model.upper()} batch embedding...")
        
        for orig_idx, resume in enumerate(resumes_data):
            # Only process filtered resumes
            if resume not in filtered_resumes:
                continue
                
            clean_text = resume.get('CleanText', '')
            if not clean_text:
                # Fallback: generate clean text if not present
                resume_text = resume.get('Resume_str', '')
                clean_text = clean_text_func(resume_text)
            
            resume_texts.append(clean_text)
            resume_categories.append(resume.get('Category', ''))
            resume_indices.append(orig_idx)
        
        # Generate embeddings in batch (much faster than one-by-one)
        print(f"Generating {model.upper()} embeddings in batch (batch_size=32)...")
        if model.lower() == 'roberta':
            resume_embeddings = self.embedding_generator.generate_roberta_embeddings_batch(resume_texts, batch_size=32)
        else:
            resume_embeddings = self.embedding_generator.generate_bert_embeddings_batch(resume_texts, batch_size=32)
        
        print(f"Generated {len(resume_embeddings)} embeddings")
        
        print("Finding top matches using model-based similarity + category filtering...")
        # Model-based similarity on category-filtered candidates
        # Use 0.3 threshold for more selective matching
        top_matches = find_top_matches(job_embedding, resume_embeddings, top_n, min_similarity=0.3)
        
        # Debug logging
        if top_matches:
            print(f"Top {len(top_matches)} matches ({model.upper()} similarity + category filter):")
            for i, (idx, score) in enumerate(top_matches[:5], 1):
                print(f"  {i}. Score: {score:.3f} | Category: {resume_categories[idx]}")
        
        # Build results
        results = []
        for rank, (filtered_idx, similarity_score) in enumerate(top_matches, 1):
            # Map back to original resume index
            orig_resume_idx = resume_indices[filtered_idx]
            resume = resumes_data[orig_resume_idx]
            
            # Ensure resume has CleanText and Skills for report generation
            if 'CleanText' not in resume or not resume.get('CleanText'):
                resume_text = resume.get('Resume_str', '')
                resume['CleanText'] = clean_text_func(resume_text)
            
            if 'Skills' not in resume or not resume.get('Skills'):
                resume['Skills'] = extract_skills(resume.get('CleanText', ''), self.nlp_model) if self.nlp_model else []
            
            results.append({
                'rank': rank,
                'resume_index': orig_resume_idx,
                'similarity_score': round(similarity_score, 3),
                'resume_id': resume.get('ID', 'N/A'),
                'category': resume.get('Category', 'N/A'),
                'resume_text': resume.get('Resume_str', '')[:200] + '...' if resume.get('Resume_str') else 'N/A',
                'resume_data': resume  # Full resume data for report generation
            })
        
        return results

