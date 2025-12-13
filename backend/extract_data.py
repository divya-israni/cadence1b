"""
Script to extract data from notebook cache to JSON files for FastAPI backend.
Run this script from the notebook or with the same Python environment.
"""
import pandas as pd
import json
from pathlib import Path


def extract_data():
    """Extract jobs and resumes from pickle cache to JSON."""
    # Paths
    cache_dir = Path(__file__).parent.parent / "cache"
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    jobs_cache = cache_dir / "df_jobs_clean.pkl"
    resumes_cache = cache_dir / "df_resumes_clean.pkl"
    
    jobs_file = data_dir / "jobs.json"
    resumes_file = data_dir / "resumes.json"
    
    # Load from cache
    if not jobs_cache.exists():
        print(f"Error: {jobs_cache} not found. Please run the notebook preprocessing first.")
        return
    
    if not resumes_cache.exists():
        print(f"Error: {resumes_cache} not found. Please run the notebook preprocessing first.")
        return
    
    print("Loading data from cache...")
    df_jobs = pd.read_pickle(jobs_cache)
    df_resumes = pd.read_pickle(resumes_cache)
    
    print(f"Loaded {len(df_jobs)} jobs and {len(df_resumes)} resumes")
    
    # Convert to JSON-compatible format
    # Handle numpy types and lists
    def convert_to_json_serializable(obj):
        """Convert numpy types and other non-serializable objects to JSON-compatible types."""
        if isinstance(obj, (pd.Series, pd.DataFrame)):
            return obj.to_dict()
        elif isinstance(obj, (list, tuple)):
            return [convert_to_json_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: convert_to_json_serializable(v) for k, v in obj.items()}
        elif hasattr(obj, 'item'):  # numpy scalar
            return obj.item()
        elif hasattr(obj, 'tolist'):  # numpy array
            return obj.tolist()
        else:
            return str(obj)
    
    # Convert to dictionaries
    jobs_json = df_jobs.to_dict('records')
    resumes_json = df_resumes.to_dict('records')
    
    # Convert numpy types
    jobs_json = [convert_to_json_serializable(job) for job in jobs_json]
    resumes_json = [convert_to_json_serializable(resume) for resume in resumes_json]
    
    # Save to JSON
    print(f"Saving to {jobs_file}...")
    with open(jobs_file, 'w', encoding='utf-8') as f:
        json.dump(jobs_json, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"Saving to {resumes_file}...")
    with open(resumes_file, 'w', encoding='utf-8') as f:
        json.dump(resumes_json, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✅ Successfully extracted {len(jobs_json)} jobs and {len(resumes_json)} resumes to JSON files")
    print(f"   Jobs: {jobs_file}")
    print(f"   Resumes: {resumes_file}")


if __name__ == "__main__":
    extract_data()

