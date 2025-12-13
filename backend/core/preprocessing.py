"""
Text preprocessing module with exact logic from notebook.
Handles text cleaning, normalization, and lemmatization.
"""
import re
from typing import Optional


def clean_text(text: str) -> str:
    """
    Clean and normalize text by removing HTML, special characters, and normalizing whitespace.
    Exact implementation from notebook.
    
    Args:
        text: Raw text string
    
    Returns:
        Cleaned lowercase text string
    """
    if not text or text is None:
        return ""
    
    text = str(text).lower()
    text = re.sub(r'<.*?>', ' ', text)  # Remove HTML tags
    text = re.sub(r'[^a-z\s]', ' ', text)  # Remove special characters, keep only lowercase letters and spaces
    text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace
    return text


def lemmatize_text(text: str, nlp_model=None) -> str:
    """
    Lemmatize text and remove stopwords for improved matching.
    Exact implementation from notebook.
    
    Args:
        text: Input text string
        nlp_model: spaCy language model (optional, will be loaded if None)
    
    Returns:
        Lemmatized text string
    """
    if not text:
        return ""
    
    # Lazy load spaCy model if not provided
    if nlp_model is None:
        try:
            import spacy
            nlp_model = spacy.load("en_core_web_sm")
        except OSError:
            return text  # Return original if model not available
    
    if not nlp_model:
        return text
    
    doc = nlp_model(text)
    return " ".join([token.lemma_ for token in doc if not token.is_stop and token.is_alpha])


def extract_requirements_section(text: str) -> str:
    """
    Extract the requirements/qualifications section from job description.
    This helps focus the embedding on technical requirements rather than company culture.
    
    Args:
        text: Full job description text
    
    Returns:
        Text focused on requirements section
    """
    if not text:
        return ""
    
    text_lower = text.lower()
    
    # Keywords that indicate the start of requirements section
    requirement_keywords = [
        'requirements',
        'qualifications',
        'required qualifications',
        'required skills',
        'must have',
        'required experience',
        'education requirements',
        'bachelor',
        'degree in',
        'years experience',
        'experience with',
        'proficiency in',
        'knowledge of',
        'skills required',
        'we require',
        'you must have',
        'you should have',
        'key responsibilities',
        'responsibilities include'
    ]
    
    # Find the start of requirements section
    lines = text.split('\n')
    requirements_start = -1
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        if any(keyword in line_lower for keyword in requirement_keywords):
            requirements_start = i
            break
    
    # If we found a requirements section, extract from there
    if requirements_start >= 0:
        # Take from requirements section to end, or next major section
        requirements_text = '\n'.join(lines[requirements_start:])
        
        # Also include title and key responsibilities if available
        # Look for "About The Role" or similar sections before requirements
        for i in range(max(0, requirements_start - 10), requirements_start):
            if 'about the role' in lines[i].lower() or 'key responsibilities' in lines[i].lower():
                requirements_text = '\n'.join(lines[i:requirements_start + 20])
                break
        
        return requirements_text
    
    # If no clear requirements section, try to extract technical keywords
    # Focus on lines with technical terms
    technical_keywords = [
        'react', 'vue', 'angular', 'javascript', 'python', 'java', 'sql', 'database',
        'backend', 'frontend', 'full stack', 'engineer', 'developer', 'programming',
        'computer science', 'software', 'orm', 'api', 'aws', 'docker', 'kubernetes'
    ]
    
    technical_lines = []
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in technical_keywords):
            technical_lines.append(line)
    
    if technical_lines:
        return '\n'.join(technical_lines)
    
    # Fallback: return original text
    return text

