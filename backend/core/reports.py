"""
Report generation module for match summaries and candidate feedback.
Exact logic from notebook.
"""
from typing import Dict, List, Optional
from .ai_summary import generate_ai_match_summary


def generate_match_summary(
    job: Dict,
    resume: Dict,
    similarity_score: float,
    model_type: str = 'bert',
    threshold: float = 0.6
) -> Dict:
    """
    Generate a comprehensive match summary for hiring managers.
    Enhanced with user-friendly scoring that scales semantic similarity to more intuitive percentages.
    
    Args:
        job: Job dictionary with Skills, Title, Company, etc.
        resume: Resume dictionary with Skills, ID, Category, etc.
        similarity_score: Calculated similarity score (raw BERT/RoBERTa score)
        model_type: Type of model used ('bert', 'roberta', 'tfidf')
        threshold: Minimum score threshold for match (default 0.6)
    
    Returns:
        Dictionary containing match summary components
    """
    # Get skills - handle both list and string formats
    job_skills_raw = job.get('Skills', [])
    if isinstance(job_skills_raw, str):
        job_skills = set(job_skills_raw.split(',')) if job_skills_raw else set()
    elif isinstance(job_skills_raw, list):
        job_skills = set(job_skills_raw) if job_skills_raw else set()
    else:
        job_skills = set()
    
    resume_skills_raw = resume.get('Skills', [])
    if isinstance(resume_skills_raw, str):
        resume_skills = set(resume_skills_raw.split(',')) if resume_skills_raw else set()
    elif isinstance(resume_skills_raw, list):
        resume_skills = set(resume_skills_raw) if resume_skills_raw else set()
    else:
        resume_skills = set()
    
    # Normalize skills to lowercase for comparison
    job_skills = {s.lower().strip() if isinstance(s, str) else str(s).lower().strip() for s in job_skills}
    resume_skills = {s.lower().strip() if isinstance(s, str) else str(s).lower().strip() for s in resume_skills}
    
    # Calculate skill overlap
    matching_skills = job_skills.intersection(resume_skills)
    missing_skills = job_skills - resume_skills
    extra_skills = resume_skills - job_skills
    
    skill_match_ratio = len(matching_skills) / len(job_skills) if job_skills else 0
    
    # Enhanced scoring: Scale raw similarity to user-friendly percentage
    # BERT/RoBERTa scores (0.2-0.7) → User-friendly scores (40-95%)
    # Formula: scaled_score = 40 + (raw_score - 0.2) * 110
    # This makes scores more intuitive while preserving ranking
    raw_score = similarity_score
    if raw_score < 0.2:
        scaled_score = raw_score * 200  # Very low scores stay low (0-40%)
    else:
        # Linear scaling from 0.2-0.7 to 40-95%
        scaled_score = 40 + ((raw_score - 0.2) / 0.5) * 55
    
    # Cap at 98% (perfect match is rare)
    scaled_score = min(scaled_score, 0.98)
    
    # Also factor in skill match ratio for more balanced scoring
    # Combine: 70% semantic similarity + 30% skill overlap
    final_score = (scaled_score * 0.7) + (skill_match_ratio * 0.3)
    
    # Determine alignment level based on final score
    if final_score >= 0.80:
        alignment_level = "Excellent Match"
        recommendation = "Strongly Recommended"
    elif final_score >= 0.65:
        alignment_level = "Good Match"
        recommendation = "Recommended"
    elif final_score >= 0.50:
        alignment_level = "Moderate Match"
        recommendation = "Consider with Training"
    else:
        alignment_level = "Weak Match"
        recommendation = "Not Recommended"
    
    # Generate summary text
    summary = {
        'candidate_id': resume.get('ID', 'N/A'),
        'candidate_category': resume.get('Category', 'N/A'),
        'job_title': job.get('Title', 'N/A'),
        'company': job.get('Company', 'N/A'),
        'similarity_score': round(final_score, 3),  # Use enhanced final score
        'alignment_level': alignment_level,
        'recommendation': recommendation,
        'why_fit': f"Candidate demonstrates {final_score*100:.1f}% compatibility with the job requirements. "
                  f"Strong skill alignment of {skill_match_ratio*100:.1f}% indicates relevant experience.",
        'ai_summary': generate_ai_match_summary(
            job, resume, final_score, list(matching_skills),
            list(missing_skills), list(extra_skills), skill_match_ratio
        ),
        'matching_skills': list(matching_skills),  # Return all, not limited
        'missing_skills': list(missing_skills),  # Return all, not limited
        'extra_skills': list(extra_skills),  # Return all, not limited
        'skill_match_ratio': round(skill_match_ratio, 3),
        'gaps': f"Missing {len(missing_skills)} key skills: {', '.join(list(missing_skills)[:5])}" if missing_skills else "No significant skill gaps identified."
    }
    
    return summary


def generate_candidate_feedback(
    job: Dict,
    resume: Dict,
    similarity_score: float,
    threshold: float = 0.6
) -> Dict:
    """
    Generate detailed feedback report for candidates.
    Exact implementation from notebook.
    
    Args:
        job: Job dictionary with Skills, Title, Company, etc.
        resume: Resume dictionary with Skills, ID, Category, etc.
        similarity_score: Calculated similarity score
        threshold: Minimum score threshold (default 0.6)
    
    Returns:
        Dictionary containing feedback components
    """
    # Get skills - handle both list and string formats (same as generate_match_summary)
    job_skills_raw = job.get('Skills', [])
    if isinstance(job_skills_raw, str):
        job_skills = set(job_skills_raw.split(',')) if job_skills_raw else set()
    elif isinstance(job_skills_raw, list):
        job_skills = set(job_skills_raw) if job_skills_raw else set()
    else:
        job_skills = set()
    
    resume_skills_raw = resume.get('Skills', [])
    if isinstance(resume_skills_raw, str):
        resume_skills = set(resume_skills_raw.split(',')) if resume_skills_raw else set()
    elif isinstance(resume_skills_raw, list):
        resume_skills = set(resume_skills_raw) if resume_skills_raw else set()
    else:
        resume_skills = set()
    
    # Normalize skills to lowercase for comparison
    job_skills = {s.lower().strip() if isinstance(s, str) else str(s).lower().strip() for s in job_skills}
    resume_skills = {s.lower().strip() if isinstance(s, str) else str(s).lower().strip() for s in resume_skills}
    
    missing_skills = job_skills - resume_skills
    matching_skills = job_skills.intersection(resume_skills)
    
    skill_gap = len(missing_skills) / len(job_skills) if job_skills else 1.0
    
    # Determine improvement areas
    improvement_areas = []
    if similarity_score < threshold:
        improvement_areas.append("Overall profile alignment needs improvement")
    if skill_gap > 0.3:
        improvement_areas.append(f"Missing {len(missing_skills)} critical skills")
    if len(matching_skills) < 3:
        improvement_areas.append("Limited overlap with required skills")
    
    # Generate learning path suggestions
    learning_paths = []
    skill_categories = {
        'technical': ['python', 'java', 'javascript', 'sql', 'database', 'aws', 'docker'],
        'soft_skills': ['leadership', 'communication', 'project management', 'agile', 'scrum'],
        'domain': ['machine learning', 'data science', 'web development', 'mobile development']
    }
    
    for skill in list(missing_skills)[:5]:
        category = 'technical'
        for cat, skills in skill_categories.items():
            if any(s in skill.lower() for s in skills):
                category = cat
                break
        
        if category == 'technical':
            learning_paths.append(f"{skill}: Consider online courses (Coursera, Udemy) or certification programs")
        elif category == 'soft_skills':
            learning_paths.append(f"{skill}: Practice through projects, mentorship, or workshops")
        else:
            learning_paths.append(f"{skill}: Build portfolio projects and gain hands-on experience")
    
    # Actionable improvements
    improvements = []
    if similarity_score < 0.5:
        improvements.append("Enhance resume keywords to better match job description terminology")
    if len(matching_skills) < len(job_skills) * 0.5:
        improvements.append(f"Focus on acquiring top {min(5, len(missing_skills))} missing skills: {', '.join(list(missing_skills)[:5])}")
    improvements.append("Highlight relevant projects and experiences more prominently")
    improvements.append("Consider obtaining relevant certifications to strengthen profile")
    
    feedback = {
        'candidate_id': resume.get('ID', 'N/A'),
        'job_title': job.get('Title', 'N/A'),
        'company': job.get('Company', 'N/A'),
        'current_score': round(similarity_score, 3),
        'threshold': threshold,
        'meets_threshold': similarity_score >= threshold,
        'missing_skills': list(missing_skills),
        'matching_skills': list(matching_skills),
        'skill_gap_percentage': round(skill_gap * 100, 1),
        'improvement_areas': improvement_areas,
        'learning_paths': learning_paths[:5],
        'actionable_improvements': improvements
    }
    
    return feedback

