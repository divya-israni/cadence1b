import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface MatchResult {
  rank: number;
  similarity_score: number;
  alignment_level: string;
  recommendation: string;
  why_fit: string;
  matching_skills: string[];
  missing_skills: string[];
  extra_skills: string[];
  skill_match_ratio: number;
  gaps: string;
  ai_summary?: string;  // AI-generated match summary
  job_title?: string;
  company?: string;
  location?: string;
  description?: string;
  job_full_text?: string;  // Full job description
  resume_id?: string;
  category?: string;
  resume_text?: string;
  resume_full_text?: string;  // Full resume text
}

export interface MatchesResponse {
  matches: MatchResult[];
  model_used: string;
  total_matches: number;
}

export const api = {
  async resumeToJobs(file: File, model: 'bert' | 'roberta' = 'bert', topN: number = 10): Promise<MatchesResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await axios.post<MatchesResponse>(
      `${API_BASE_URL}/resume-to-jobs?model=${model}&top_n=${topN}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    
    return response.data;
  },

  async jobToCandidates(file: File, model: 'bert' | 'roberta' = 'bert', topN: number = 10): Promise<MatchesResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await axios.post<MatchesResponse>(
      `${API_BASE_URL}/job-to-candidates?model=${model}&top_n=${topN}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    
    return response.data;
  },

  async healthCheck() {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  },
};

