"""
Category matching module to infer job categories from text and match with resume categories.
"""
from typing import List, Dict, Optional, Set


# Category keywords mapping - Enhanced for web development
CATEGORY_KEYWORDS = {
    'INFORMATION-TECHNOLOGY': ['it', 'information technology', 'software', 'programming', 'developer', 'coding',
                              'python', 'java', 'javascript', 'typescript', 'react', 'vue', 'angular', 'angular.io',
                              'vue.js', 'node', 'node.js', 'database', 'orm', 'sql', 'api', 'backend', 'frontend', 
                              'full stack', 'fullstack', 'web development', 'web developer', 'web application', 
                              'web applications', 'website', 'stateful', 'html', 'css', 'php', 'asp', 'net', 'c++',
                              'event-driven', 'testing', 'relational database', 'web design', 'user interface',
                              'system administrator', 'network', 'cybersecurity', 'data science', 
                              'machine learning', 'ai', 'artificial intelligence', 'seo', 'server-side'],
    'ENGINEERING': ['engineer', 'engineering', 'software engineer', 'mechanical engineer', 'electrical engineer', 
                    'civil engineer', 'full stack engineer', 'backend engineer', 'frontend engineer', 'staff engineer',
                    'senior engineer', 'computer science', 'cs', 'development',
                    'web application', 'orm', 'software development'],
    'PUBLIC-RELATIONS': ['public relations', 'pr', 'communications', 'media relations', 'press release',
                        'brand management', 'marketing communications'],
    'HR': ['human resources', 'hr', 'recruiting', 'talent acquisition', 'employee relations', 'hr administrator'],
    'FINANCE': ['finance', 'accounting', 'financial analyst', 'cpa', 'audit', 'bookkeeping', 'tax'],
    'SALES': ['sales', 'account executive', 'business development', 'account manager', 'sales representative'],
    'MARKETING': ['marketing', 'digital marketing', 'social media', 'advertising', 'brand', 'campaign'],
    'HEALTHCARE': ['healthcare', 'medical', 'nurse', 'doctor', 'physician', 'hospital', 'clinical'],
    'EDUCATION': ['teacher', 'education', 'teaching', 'professor', 'instructor', 'curriculum']
}


def infer_job_category(job_text: str) -> List[str]:
    """
    Infer likely job categories from job description text.
    
    Args:
        job_text: Cleaned job description text
    
    Returns:
        List of likely categories (ordered by relevance)
    """
    if not job_text:
        return []
    
    job_text_lower = job_text.lower()
    category_scores = {}
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in job_text_lower)
        if score > 0:
            category_scores[category] = score
    
    # Sort by score descending
    sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Debug output
    if sorted_categories:
        print(f"Category detection scores: {dict(sorted_categories[:5])}")
    
    return [cat for cat, score in sorted_categories[:3]]  # Top 3 categories


def get_relevant_categories(job_text: str) -> Set[str]:
    """
    Get set of relevant resume categories for a job.
    
    Args:
        job_text: Cleaned job description text
    
    Returns:
        Set of relevant category names
    """
    inferred = infer_job_category(job_text)
    
    # Add related categories - be more selective to avoid false matches
    related = {
        'ENGINEERING': {'ENGINEERING', 'INFORMATION-TECHNOLOGY'},
        'INFORMATION-TECHNOLOGY': {'INFORMATION-TECHNOLOGY', 'ENGINEERING'},
        'PUBLIC-RELATIONS': {'PUBLIC-RELATIONS', 'MARKETING'},
        'HR': {'HR'},
        'FINANCE': {'FINANCE', 'ACCOUNTANT'},
        'SALES': {'SALES', 'BUSINESS-DEVELOPMENT'},
        'MARKETING': {'MARKETING', 'PUBLIC-RELATIONS'}
    }
    
    relevant = set(inferred)
    
    # Only add related categories if the primary category is strongly detected
    # For ENGINEERING/IT jobs, don't add marketing-related categories
    if 'ENGINEERING' in inferred or 'INFORMATION-TECHNOLOGY' in inferred:
        # For tech jobs, ONLY include tech categories
        relevant = {'ENGINEERING', 'INFORMATION-TECHNOLOGY'}
    else:
        # For other jobs, add related categories
        for cat in inferred:
            if cat in related:
                relevant.update(related[cat])
    
    return relevant


def boost_score_by_category(
    similarity_score: float,
    resume_category: str,
    relevant_categories: Set[str],
    boost_factor: float = 0.1
) -> float:
    """
    Boost similarity score if resume category matches job category.
    
    Args:
        similarity_score: Original similarity score
        resume_category: Resume category
        relevant_categories: Set of relevant categories for the job
        boost_factor: Amount to boost (default 0.1 = 10% boost)
    
    Returns:
        Adjusted similarity score
    """
    if resume_category in relevant_categories:
        # Boost score by boost_factor (capped at 1.0)
        boosted = similarity_score + boost_factor
        return min(boosted, 1.0)
    return similarity_score

