"""
AI-generated match summary module using OpenAI or Google Gemini API.
"""
from typing import Dict, Optional
import os


def generate_ai_match_summary(
    job: Dict,
    resume: Dict,
    similarity_score: float,
    matching_skills: list,
    missing_skills: list,
    extra_skills: list,
    skill_match_ratio: float
) -> str:
    """
    Generate an AI-powered match summary using Groq, OpenAI, or Google Gemini.
    
    Args:
        job: Job dictionary with Title, Company, JobDescription, etc.
        resume: Resume dictionary with ID, Category, Resume_str, etc.
        similarity_score: Calculated similarity score (0-1)
        matching_skills: List of matching skills
        missing_skills: List of missing skills
        extra_skills: List of extra skills
        skill_match_ratio: Skill match ratio (0-1)
    
    Returns:
        AI-generated summary string
    """
    # Try Groq first (fastest and most affordable), then OpenAI, then Gemini, then fallback
    summary = _generate_with_groq(
        job, resume, similarity_score, matching_skills, missing_skills,
        extra_skills, skill_match_ratio
    )
    
    if summary:
        return summary
    
    summary = _generate_with_openai(
        job, resume, similarity_score, matching_skills, missing_skills, 
        extra_skills, skill_match_ratio
    )
    
    if summary:
        return summary
    
    summary = _generate_with_gemini(
        job, resume, similarity_score, matching_skills, missing_skills,
        extra_skills, skill_match_ratio
    )
    
    if summary:
        return summary
    
    # Fallback to template-based summary
    return _generate_fallback_summary(
        job, resume, similarity_score, matching_skills, missing_skills,
        extra_skills, skill_match_ratio
    )


def _generate_with_groq(
    job: Dict,
    resume: Dict,
    similarity_score: float,
    matching_skills: list,
    missing_skills: list,
    extra_skills: list,
    skill_match_ratio: float
) -> Optional[str]:
    """Generate summary using Groq API (fast and affordable)."""
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        return None
    
    try:
        from openai import OpenAI
        # Groq uses OpenAI-compatible API
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        job_title = job.get('Title', 'N/A')
        company = job.get('Company', 'N/A')
        category = resume.get('Category', 'N/A')
        job_desc = job.get('JobDescription', '')[:600]
        
        # Determine match level for tone
        if similarity_score >= 0.75:
            tone = "highly enthusiastic"
            match_level = "excellent"
        elif similarity_score >= 0.60:
            tone = "positive and encouraging"
            match_level = "strong"
        elif similarity_score >= 0.45:
            tone = "balanced and constructive"
            match_level = "moderate"
        else:
            tone = "honest but constructive"
            match_level = "limited"
        
        prompt = f"""As an experienced technical recruiter with a {tone} approach, write a compelling 2-3 sentence match assessment for this {match_level} candidate-job pairing:

**Position:** {job_title} at {company}
**Candidate Background:** {category}
**Match Score:** {similarity_score*100:.1f}%
**Key Strengths:** {', '.join(matching_skills[:8]) if matching_skills else 'Limited overlap detected'}
**Growth Areas:** {', '.join(missing_skills[:5]) if missing_skills else 'None identified'}

Create an engaging, human-sounding summary that:
- Highlights the candidate's strongest relevant qualifications
- Mentions 2-3 specific technical/domain skills they bring
- If there are gaps, frame them as "development opportunities" or "areas to strengthen"
- Use active, confident language
- Be specific about WHY they're a fit (or not)
- Avoid generic phrases like "shows alignment" - be creative and specific

Write naturally, as if you're explaining this match to a hiring manager over coffee."""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Updated model (3.1 was decommissioned)
            messages=[
                {"role": "system", "content": "You are a charismatic senior technical recruiter known for insightful, engaging candidate assessments. Write naturally and avoid corporate jargon."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.8
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq API error: {e}")
        return None


def _generate_with_openai(
    job: Dict,
    resume: Dict,
    similarity_score: float,
    matching_skills: list,
    missing_skills: list,
    extra_skills: list,
    skill_match_ratio: float
) -> Optional[str]:
    """Generate summary using OpenAI API."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        job_title = job.get('Title', 'N/A')
        company = job.get('Company', 'N/A')
        category = resume.get('Category', 'N/A')
        job_desc = job.get('JobDescription', '')[:600]
        
        # Determine match level for tone
        if similarity_score >= 0.75:
            tone = "highly enthusiastic"
            match_level = "excellent"
        elif similarity_score >= 0.60:
            tone = "positive and encouraging"
            match_level = "strong"
        elif similarity_score >= 0.45:
            tone = "balanced and constructive"
            match_level = "moderate"
        else:
            tone = "honest but constructive"
            match_level = "limited"
        
        prompt = f"""As an experienced technical recruiter with a {tone} approach, write a compelling 2-3 sentence match assessment for this {match_level} candidate-job pairing:

**Position:** {job_title} at {company}
**Candidate Background:** {category}
**Match Score:** {similarity_score*100:.1f}%
**Key Strengths:** {', '.join(matching_skills[:8]) if matching_skills else 'Limited overlap detected'}
**Growth Areas:** {', '.join(missing_skills[:5]) if missing_skills else 'None identified'}

Create an engaging, human-sounding summary that:
- Highlights the candidate's strongest relevant qualifications
- Mentions 2-3 specific technical/domain skills they bring
- If there are gaps, frame them as "development opportunities" or "areas to strengthen"
- Use active, confident language
- Be specific about WHY they're a fit (or not)
- Avoid generic phrases like "shows alignment" - be creative and specific

Write naturally, as if you're explaining this match to a hiring manager over coffee."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a charismatic senior technical recruiter known for insightful, engaging candidate assessments. Write naturally and avoid corporate jargon."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.8
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None


def _generate_with_gemini(
    job: Dict,
    resume: Dict,
    similarity_score: float,
    matching_skills: list,
    missing_skills: list,
    extra_skills: list,
    skill_match_ratio: float
) -> Optional[str]:
    """Generate summary using Google Gemini API."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return None
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-pro')
        
        job_title = job.get('Title', 'N/A')
        company = job.get('Company', 'N/A')
        job_desc = job.get('JobDescription', '')[:500]
        
        prompt = f"""As a professional recruiter, provide a concise match summary (2-3 sentences) for this candidate-resume match:

Job: {job_title} at {company}
Job Description: {job_desc}
Similarity Score: {similarity_score*100:.1f}%
Skill Match: {skill_match_ratio*100:.1f}%
Matching Skills: {', '.join(matching_skills[:10])}
Missing Skills: {', '.join(missing_skills[:10])}

Write a brief, professional summary explaining why this candidate is or isn't a good fit. Focus on key strengths and any critical gaps."""
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None


def _generate_fallback_summary(
    job: Dict,
    resume: Dict,
    similarity_score: float,
    matching_skills: list,
    missing_skills: list,
    extra_skills: list,
    skill_match_ratio: float
) -> str:
    """Fallback template-based summary if AI APIs are not available."""
    job_title = job.get('Title', 'N/A')
    
    if similarity_score >= 0.70:
        strength = "strong"
        fit = "excellent fit"
    elif similarity_score >= 0.55:
        strength = "good"
        fit = "solid candidate"
    elif similarity_score >= 0.45:
        strength = "moderate"
        fit = "potential candidate with some gaps"
    else:
        strength = "limited"
        fit = "candidate with significant gaps"
    
    summary = f"This candidate shows {strength} alignment ({similarity_score*100:.1f}% similarity) for the {job_title} position. "
    
    if matching_skills:
        summary += f"Key strengths include: {', '.join(matching_skills[:5])}. "
    
    if missing_skills:
        summary += f"Areas for development: {', '.join(missing_skills[:3])}."
    else:
        summary += "No significant skill gaps identified."
    
    return summary

