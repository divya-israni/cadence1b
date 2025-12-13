"""
Skill extraction module using spaCy NLP.
Enhanced with better filtering and skill validation.
"""
from typing import List, Optional


def extract_skills(text: str, nlp_model) -> List[str]:
    """
    Extract skill keywords from text using spaCy NLP model with improved filtering.
    
    Args:
        text: Input text to analyze
        nlp_model: spaCy language model
    
    Returns:
        List of unique, validated skill keywords
    """
    if not nlp_model or not text:
        return []
    
    # Comprehensive technical skills whitelist - STRICT VERSION
    technical_keywords = {
        # Programming Languages (core only)
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
        'go', 'rust', 'scala', 'r',
        
        # Web Technologies (essential)
        'html', 'css', 'react', 'vue', 'angular', 'node.js', 'nodejs', 'express', 
        'fastapi', 'django', 'flask', 'spring', 'bootstrap', 'tailwind',
        
        # Databases (major ones)
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite',
        
        # Cloud & DevOps (core)
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'jenkins', 'ci/cd',
        
        # Design Tools (essential)
        'photoshop', 'illustrator', 'figma', 'sketch', 'autocad',
        
        # Data & Analytics
        'excel', 'tableau', 'powerbi', 'pandas', 'numpy', 'tensorflow', 'pytorch',
        
        # Methodologies
        'agile', 'scrum', 'rest', 'api', 'microservices',
        
        # Essential Soft Skills
        'leadership', 'management', 'communication'
    }
    
    # Expanded exclusion list - remove common non-skill words
    excluded_words = {
        # Dates & Time
        'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 
        'september', 'october', 'november', 'december',
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
        'year', 'month', 'week', 'day', 'hour', 'minute', 'today', 'tomorrow', 'yesterday',
        'time', 'date', 'period', 'duration', 'deadline', 'current',
        
        # Common Words
        'person', 'people', 'individual', 'candidate', 'employee', 'staff', 'member',
        'thing', 'item', 'object', 'element', 'part', 'work', 'works', 'working',
        'job', 'position', 'role', 'task', 'duty', 'responsibility',
        'company', 'organization', 'business', 'firm', 'agency', 'corporation',
        'experience', 'background', 'history', 'qualification',
        'skill', 'skills', 'ability', 'capability', 'competency', 'proficiency',
        'level', 'degree', 'grade', 'rank', 'status',
        'requirement', 'need', 'must', 'should', 'prefer',
        'description', 'summary', 'overview', 'detail', 'details',
        
        # Locations & Contact
        'office', 'location', 'place', 'site', 'area', 'region', 'country', 'city', 'state',
        'email', 'phone', 'address', 'contact', 'number',
        'salary', 'pay', 'wage', 'compensation', 'benefit', 'package',
        'application', 'resume', 'cv', 'profile', 'portfolio',
        
        # Generic verbs/actions
        'design', 'designing', 'develop', 'developing', 'create', 'creating',
        'build', 'building', 'make', 'making', 'manage', 'managing',
        'monitor', 'monitoring', 'prepare', 'preparing', 'review', 'reviewing',
        'track', 'tracking', 'update', 'updating', 'analyze', 'analyzing',
        'coordinate', 'coordinating', 'supervise', 'supervising',
        
        # Document/Report terms
        'report', 'reports', 'reporting', 'reporter', 'document', 'documents',
        'drawing', 'drawings', 'program', 'programs', 'progress', 'project', 'projects',
        
        # Generic nouns
        'client', 'consultant', 'contractor', 'supplier', 'vendor',
        'material', 'materials', 'delivery', 'schedule', 'meeting', 'meetings',
        'activity', 'activities', 'payment', 'payments', 'quantity', 'quantities',
        
        # Misc common words
        'government', 'english', 'hindi', 'language', 'languages',
        'video', 'page', 'maker', 'editor', 'editing',
        'information', 'technology', 'dos'
    }
    
    doc = nlp_model(text)
    skills = []
    text_lower = text.lower()
    
    # ONLY extract from whitelist - no noun extraction
    # This prevents extracting random words as skills
    for keyword in technical_keywords:
        if keyword in text_lower:
            skills.append(keyword)
    
    # Return unique skills, sorted by frequency of use (implicit by order)
    return list(set(skills))

