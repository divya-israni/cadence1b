"""
ONE-TIME SCRIPT: Fix skills in JSON files using strict whitelist.
Run this once, then you won't need to re-extract on every startup.
"""
import json
import spacy
from pathlib import Path
from core.skills import extract_skills

# Load spacy model
print("Loading spaCy model...")
nlp = spacy.load('en_core_web_sm')

# Paths
DATA_DIR = Path(__file__).parent / "data"
JOBS_FILE = DATA_DIR / "jobs.json"
RESUMES_FILE = DATA_DIR / "resumes.json"

# Fix jobs
print("\n" + "="*60)
print("FIXING JOBS...")
print("="*60)
with open(JOBS_FILE, 'r', encoding='utf-8') as f:
    jobs = json.load(f)

fixed_count = 0
for job in jobs:
    old_skills = job.get('Skills', [])
    text = job.get('CombinedText', '') or job.get('JobDescription', '')
    new_skills = extract_skills(text, nlp)
    
    if set(old_skills) != set(new_skills):
        fixed_count += 1
        if fixed_count <= 3:  # Show first 3 examples
            print(f"\nJob {fixed_count}:")
            print(f"  Old skills ({len(old_skills)}): {old_skills[:10]}")
            print(f"  New skills ({len(new_skills)}): {new_skills[:10]}")
    
    job['Skills'] = new_skills

print(f"\n✅ Fixed {fixed_count} jobs")

# Save jobs
with open(JOBS_FILE, 'w', encoding='utf-8') as f:
    json.dump(jobs, f, indent=2, ensure_ascii=False)
print(f"✅ Saved to {JOBS_FILE}")

# Fix resumes
print("\n" + "="*60)
print("FIXING RESUMES...")
print("="*60)
with open(RESUMES_FILE, 'r', encoding='utf-8') as f:
    resumes = json.load(f)

fixed_count = 0
for resume in resumes:
    old_skills = resume.get('Skills', [])
    text = resume.get('CleanText', '') or resume.get('Resume_str', '')
    new_skills = extract_skills(text, nlp)
    
    if set(old_skills) != set(new_skills):
        fixed_count += 1
        if fixed_count <= 3:  # Show first 3 examples
            print(f"\nResume {fixed_count}:")
            print(f"  Old skills ({len(old_skills)}): {old_skills[:10]}")
            print(f"  New skills ({len(new_skills)}): {new_skills[:10]}")
    
    resume['Skills'] = new_skills

print(f"\n✅ Fixed {fixed_count} resumes")

# Save resumes
with open(RESUMES_FILE, 'w', encoding='utf-8') as f:
    json.dump(resumes, f, indent=2, ensure_ascii=False)
print(f"✅ Saved to {RESUMES_FILE}")

print("\n" + "="*60)
print("✅ ALL DONE! Skills have been fixed in JSON files.")
print("You can now remove the re-extraction code from app.py")
print("="*60)
