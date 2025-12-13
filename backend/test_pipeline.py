"""
Test script to debug the matching pipeline with the Fora job description.
"""
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.preprocessing import clean_text
from core.skills import extract_skills
from core.category_matcher import infer_job_category, get_relevant_categories
from core.embeddings import EmbeddingGenerator
import spacy

# Test job description
job_text = """About Fora

Fora is the modern travel agency, redefining what it means to be a travel advisor in today's world. We're a next-generation platform that provides a comprehensive, business-in-a-box solution—combining cutting-edge technology, personalized training, a vibrant community, and exclusive industry partnerships—all designed to empower anyone with a passion for travel to turn that passion into a thriving business. Whether you're a travel enthusiast or an experienced professional, Fora equips you with everything needed to launch and scale a successful travel advisory business, making it the ultimate way to align work with your lifestyle.

At the heart of Fora is our mission: to power the next generation of travel entrepreneurs to transform their love for travel into a fulfilling full-time or part-time career, offering unparalleled flexibility, autonomy, and support. We believe that everyone, from seasoned travel professionals to first-time entrepreneurs, can build a career that's both profitable and aligned with their passions.

Our platform combines innovative technology with the human touch, offering:

Best-in-class training programs to help agents develop expert knowledge, no matter their starting point.

A powerful suite of tools for booking, client management, and marketing, ensuring agents can focus on delivering exceptional travel experiences.

Access to an engaged community of fellow advisors, fostering collaboration, support, and shared learning.

Exclusive partnerships with top travel brands, providing access to competitive rates, perks, and experiences that elevate advisors' offerings.

Since our founding in 2021 by experienced travel entrepreneurs Henley Vazquez, Jake Peters, and Evan Frank, Fora has experienced rapid growth, expanding to a team of 130+ full-time employees based in downtown New York City. Earlier this year, we announced our $60 million Series B and C investment rounds, led by Thrive Capital and Insight Partners, with participation by previous investors including Forerunner and Heartcore Capital. This funding represents a vote of confidence in the enduring power of entrepreneurship, and secures our ability to build a category-defining travel brand. We have a vision for the future that leverages the best of humans and the best of technology to create the first truly unified platform for all travel needs - from staycation to the safari.

We're proud of the recognition we've received, including:

LinkedIn's Top Startups List 2024

Fast Company's Most Innovative Companies 2025 and 2023

Built In 2025 Best Places to Work

And several "top agency" awards from our fantastic partners including Virtuoso, IHG, Four Seasons, and more

Fora is a mission-driven company that believes in the power of entrepreneurship, community, and passion. As we continue to grow, we are looking for more talented and like-minded individuals to join our team - people who are excited about transforming the travel space and helping us scale our vision globally.

About The Role

We're looking for a seasoned Senior/Staff Full Stack Engineer to join us as we continue to build Fora's products and infrastructure. In this role, you will be instrumental in building out the Consumer Experience, the heart of the Fora Platform. In collaboration with Product and Design, this Sr. Full Stack Engineer will work on our externally facing website, content and supplier systems and external integrations. Our ideal candidate is someone who understands our mission & brand, is excited about what we're creating, and is passionate about building high-quality software.

Key Responsibilities

Partner cross-functionally with Product Managers and Designers to define and prioritize the roadmap

Alongside your fellow engineers, build the travel advisors application that is responsible for new advisors onboarding, searching, and booking travel, and manages the advisor's itineraries and interactions with their clients

Focus on web development, and collaborate with backend engineers in order to define end-to-end engineering solutions

Own projects and be responsible for the solution, implementation, and deliver

Requirements

Bachelor's Degree in Computer Science

5+ years experience in frontend web development

3+ years experience using React / Vue.js / Angular.io

Experience building stateful and event-driven web applications

Experience testing web applications

3+ years experience in backend web development

Experience with relational database ORMs

Ability to be a team player, with solid communication and collaboration skills

An entrepreneurial mindset

Compensation

Compensation for this role varies based on experience, with an indicative range of $155K–$225K + equity. Final compensation will depend on the level at which the candidate is hired, as we're considering multiple levels for this role.

Other benefits include:

Unlimited vacation

Health Insurance (including an option completely covered by Fora HQ)

Dental & Vision Insurance

Wellhub Memberships

401k plan with company match

Commuter Benefits

Supplemental Life Insurance

Stock Options

This role is based in New York City with a hybrid WFH & office schedule (Monday, Tuesday and Thursday are our Tribeca in-office days, with flexibility for Wednesday and Friday at your preference).

Our Values

We're forging our own path

Fora has always been about driving change within the industry. We're not interested in maintaining the status quo.

We're stronger together

Community is our cornerstone and collective power is our strength. We believe we can all go further when we operate together, using our combined leverage to unlock better opportunities and outcomes for our advisors, partners, and travelers.

We believe in technology

We believe technology is an answer to some of the most fundamental challenges the travel industry faces. We believe advancements in AI, bold investments in our platforms, and a world-class data infrastructure will transform the work of our advisors and our partners, while creating better travel experiences for travelers.

We're here to serve

We operate in service of our community and believe that when they're empowered to focus on what they do best, we all win. It's why we relentlessly advocate for our advisors and prioritize their best interest every step of the way.

We mean business

Fora is equal parts fun, meaningful work and serious travel business. We're unlocking opportunities for thousands of travel entrepreneurs, delivering a stream of high-quality guests at scale for our partners, and providing a superior travel experience for our travelers. It's a better equation for the future of our industry.

-

WORK AUTHORIZATION

You must have authorization to work in the United States. Fora is unable to assist applicants with obtaining work authorization.

EQUAL OPPORTUNITY

Fora is committed to an equitable hiring process and an inclusive work environment. BIPOC and traditionally underrepresented candidates are strongly encouraged to apply. We will not discriminate and will take action to ensure against discrimination in employment, recruitment, advertisements for employment, compensation, termination, upgrading, promotions, and other conditions of employment against any employee or job applicant on the bases of race, color, gender, national origin, age, religion, creed, disability, veteran's status, sexual orientation, gender identity, gender expression or any other characteristic protected by law."""

print("=" * 80)
print("PIPELINE TESTING - FORA JOB DESCRIPTION")
print("=" * 80)

# Step 1: Text Cleaning
print("\n1. TEXT CLEANING")
print("-" * 80)
cleaned_text = clean_text(job_text)
print(f"Original length: {len(job_text)} chars")
print(f"Cleaned length: {len(cleaned_text)} chars")
print(f"Cleaned text preview (first 500 chars):")
print(cleaned_text[:500])
print("...")

# Step 2: Category Detection (for reference only - not used in matching)
print("\n2. CATEGORY DETECTION (Reference Only)")
print("-" * 80)
print("Note: Using pure model-based matching (BERT/RoBERTa), not category filtering")
try:
    from core.category_matcher import infer_job_category
    inferred_categories = infer_job_category(cleaned_text)
    print(f"Inferred categories (for reference): {inferred_categories}")
except:
    print("Category detection not available")

# Step 3: Skill Extraction
print("\n3. SKILL EXTRACTION")
print("-" * 80)
try:
    nlp = spacy.load("en_core_web_sm")
    skills = extract_skills(cleaned_text, nlp)
    print(f"Extracted {len(skills)} skills")
    print(f"Skills: {skills[:20]}")
    
    # Check for technical skills
    technical_keywords = ['react', 'vue', 'angular', 'javascript', 'python', 'sql', 'orm', 'database', 'backend', 'frontend', 'full stack', 'computer science']
    found_technical = [kw for kw in technical_keywords if kw in cleaned_text]
    print(f"\nTechnical keywords found in text: {found_technical}")
except Exception as e:
    print(f"Error loading spaCy: {e}")
    skills = []

# Step 4: Embedding Generation
print("\n4. EMBEDDING GENERATION")
print("-" * 80)
try:
    embedding_gen = EmbeddingGenerator()
    embedding = embedding_gen.generate_bert_embedding(cleaned_text)
    print(f"Embedding shape: {embedding.shape}")
    print(f"Embedding sample (first 10 values): {embedding[:10]}")
except Exception as e:
    print(f"Error generating embedding: {e}")
    embedding = None

# Step 5: Test against resumes
print("\n5. TESTING AGAINST RESUMES")
print("-" * 80)
resumes_file = Path(__file__).parent / "data" / "resumes.json"
if resumes_file.exists():
    with open(resumes_file, 'r', encoding='utf-8') as f:
        resumes_data = json.load(f)
    
    print(f"Loaded {len(resumes_data)} resumes")
    
    # Count by category
    categories = {}
    for resume in resumes_data:
        cat = resume.get('Category', 'UNKNOWN')
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\nResume categories available:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {cat}: {count}")
    
    # Test similarity - focus on ENGINEERING/IT resumes first
    if embedding is not None:
        print(f"\nTesting similarity with resumes...")
        from core.similarity import find_top_matches
        
        # Filter to ENGINEERING and INFORMATION-TECHNOLOGY resumes
        engineering_resumes = [r for r in resumes_data if r.get('Category') in ['ENGINEERING', 'INFORMATION-TECHNOLOGY']]
        print(f"Found {len(engineering_resumes)} ENGINEERING/IT resumes out of {len(resumes_data)} total")
        
        if not engineering_resumes:
            print("ERROR: No ENGINEERING/IT resumes found in dataset!")
            # Test with all resumes instead
            test_resumes = resumes_data
        else:
            # Test with ENGINEERING/IT resumes + sample of others for comparison
            other_resumes = [r for r in resumes_data if r.get('Category') not in ['ENGINEERING', 'INFORMATION-TECHNOLOGY']][:50]
            test_resumes = engineering_resumes + other_resumes
            print(f"Testing with {len(engineering_resumes)} ENGINEERING/IT + {len(other_resumes)} other resumes")
        
        resume_embeddings = []
        resume_categories = []
        
        print("Generating embeddings for test resumes...")
        for i, resume in enumerate(test_resumes):
            if i % 50 == 0:
                print(f"  Processing resume {i+1}/{len(test_resumes)}...")
            
            clean_resume_text = resume.get('CleanText', '')
            if not clean_resume_text:
                clean_resume_text = clean_text(resume.get('Resume_str', ''))
            
            resume_emb = embedding_gen.generate_bert_embedding(clean_resume_text)
            resume_embeddings.append(resume_emb)
            resume_categories.append(resume.get('Category', 'UNKNOWN'))
        
        # Find top matches with lower threshold to see all scores
        print("\nFinding top matches (min_similarity=0.25)...")
        top_matches = find_top_matches(embedding, resume_embeddings, top_n=20, min_similarity=0.25)
        
        print(f"\nTop 20 matches:")
        engineering_count = 0
        it_count = 0
        other_count = 0
        for rank, (idx, score) in enumerate(top_matches, 1):
            resume = test_resumes[idx]
            cat = resume.get('Category', 'N/A')
            if cat == 'ENGINEERING':
                engineering_count += 1
            elif cat == 'INFORMATION-TECHNOLOGY':
                it_count += 1
            else:
                other_count += 1
            print(f"  {rank}. Score: {score:.3f} | Category: {cat} | ID: {resume.get('ID', 'N/A')}")
        
        print(f"\nCategory distribution in top 20:")
        print(f"  ENGINEERING: {engineering_count}")
        print(f"  INFORMATION-TECHNOLOGY: {it_count}")
        print(f"  Other: {other_count}")
        
        # Check category distribution (for analysis only - not used in matching)
        print(f"\nCategory distribution in top matches (pure model-based):")
        eng_count = sum(1 for idx, _ in top_matches if resume_categories[idx] == 'ENGINEERING')
        it_count = sum(1 for idx, _ in top_matches if resume_categories[idx] == 'INFORMATION-TECHNOLOGY')
        other_count = len(top_matches) - eng_count - it_count
        print(f"  ENGINEERING: {eng_count}")
        print(f"  INFORMATION-TECHNOLOGY: {it_count}")
        print(f"  Other: {other_count}")
        
        if eng_count + it_count == 0:
            print("\n  WARNING: No ENGINEERING/IT resumes in top matches!")
            print("  This suggests the model similarity scores are low for tech resumes.")
            print("  Possible reasons:")
            print("    - Job description has too much company/culture text vs technical requirements")
            print("    - Resume embeddings don't match job embedding well")
            print("    - Need to adjust threshold or improve text preprocessing")
else:
    print(f"Resumes file not found: {resumes_file}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)

