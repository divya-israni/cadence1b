'use client';

import { useState } from 'react';
import { MatchResult } from '@/lib/api';
import { CheckCircle2, XCircle, AlertCircle, TrendingUp, Building2, MapPin, Briefcase, ChevronDown, ChevronUp, FileText, Sparkles } from 'lucide-react';

interface MatchCardProps {
  match: MatchResult;
  type: 'job' | 'candidate';
}

export default function MatchCard({ match, type }: MatchCardProps) {
  const [showFullText, setShowFullText] = useState(false);
  const [showAllMatchingSkills, setShowAllMatchingSkills] = useState(false);
  const [showAllMissingSkills, setShowAllMissingSkills] = useState(false);
  const [showAllExtraSkills, setShowAllExtraSkills] = useState(false);
  
  const getAlignmentColor = (level: string) => {
    switch (level) {
      case 'Excellent Match':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'Good Match':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'Moderate Match':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default:
        return 'bg-red-100 text-red-800 border-red-300';
    }
  };

  const getRecommendationIcon = (recommendation: string) => {
    if (recommendation.includes('Strongly Recommended') || recommendation.includes('Recommended')) {
      return <CheckCircle2 className="w-5 h-5 text-green-600" />;
    } else if (recommendation.includes('Consider')) {
      return <AlertCircle className="w-5 h-5 text-yellow-600" />;
    } else {
      return <XCircle className="w-5 h-5 text-red-600" />;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow p-6 border border-gray-200">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 text-primary-700 font-bold">
              #{match.rank}
            </span>
            {type === 'job' && match.job_title && (
              <h3 className="text-lg font-semibold text-gray-900">{match.job_title}</h3>
            )}
            {type === 'candidate' && match.resume_id && (
              <h3 className="text-lg font-semibold text-gray-900">Candidate #{match.resume_id}</h3>
            )}
          </div>
          
          {type === 'job' && (
            <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600 ml-11">
              {match.company && (
                <span className="flex items-center gap-1">
                  <Building2 className="w-4 h-4" />
                  {match.company}
                </span>
              )}
              {match.location && (
                <span className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  {match.location}
                </span>
              )}
            </div>
          )}
          
          {type === 'candidate' && match.category && (
            <div className="ml-11">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                <Briefcase className="w-3 h-3 mr-1" />
                {match.category}
              </span>
            </div>
          )}
        </div>
        
        <div className={`px-3 py-1 rounded-full border text-sm font-medium ${getAlignmentColor(match.alignment_level)}`}>
          {match.alignment_level}
        </div>
      </div>

      {/* Similarity Score */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Similarity Score</span>
          <span className="text-lg font-bold text-primary-600">
            {(match.similarity_score * 100).toFixed(1)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div
            className="bg-primary-500 h-2.5 rounded-full transition-all duration-500"
            style={{ width: `${match.similarity_score * 100}%` }}
          />
        </div>
      </div>

      {/* AI-Generated Summary */}
      {match.ai_summary && (
        <div className="mb-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
          <div className="flex items-start space-x-2">
            <Sparkles className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-blue-900 mb-1.5">
                💡 Recruiter Insight
              </h4>
              <p className="text-sm text-blue-800 leading-relaxed italic">{match.ai_summary}</p>
            </div>
          </div>
        </div>
      )}

      {/* Recommendation */}
      <div className="flex items-start space-x-2 mb-4 p-3 bg-gray-50 rounded-lg">
        {getRecommendationIcon(match.recommendation)}
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-900">{match.recommendation}</p>
          <p className="text-xs text-gray-600 mt-1">{match.why_fit}</p>
        </div>
      </div>

      {/* Skills */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        {match.matching_skills.length > 0 && (
          <div>
            <div className="flex items-center space-x-1 mb-2">
              <CheckCircle2 className="w-4 h-4 text-green-600" />
              <h4 className="text-sm font-medium text-gray-700">Matching Skills ({match.matching_skills.length})</h4>
            </div>
            <div className="flex flex-wrap gap-1">
              {(showAllMatchingSkills ? match.matching_skills : match.matching_skills.slice(0, 8)).map((skill, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-md"
                >
                  {skill}
                </span>
              ))}
              {match.matching_skills.length > 8 && (
                <button
                  onClick={() => setShowAllMatchingSkills(!showAllMatchingSkills)}
                  className="px-2 py-1 text-xs text-primary-600 hover:text-primary-700 hover:underline font-medium"
                >
                  {showAllMatchingSkills 
                    ? 'Show less' 
                    : `+${match.matching_skills.length - 8} more`}
                </button>
              )}
            </div>
          </div>
        )}

        {match.missing_skills.length > 0 && (
          <div>
            <div className="flex items-center space-x-1 mb-2">
              <XCircle className="w-4 h-4 text-red-600" />
              <h4 className="text-sm font-medium text-gray-700">Missing Skills ({match.missing_skills.length})</h4>
            </div>
            <div className="flex flex-wrap gap-1">
              {(showAllMissingSkills ? match.missing_skills : match.missing_skills.slice(0, 8)).map((skill, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-md"
                >
                  {skill}
                </span>
              ))}
              {match.missing_skills.length > 8 && (
                <button
                  onClick={() => setShowAllMissingSkills(!showAllMissingSkills)}
                  className="px-2 py-1 text-xs text-primary-600 hover:text-primary-700 hover:underline font-medium"
                >
                  {showAllMissingSkills 
                    ? 'Show less' 
                    : `+${match.missing_skills.length - 8} more`}
                </button>
              )}
            </div>
          </div>
        )}

        {match.extra_skills.length > 0 && (
          <div>
            <div className="flex items-center space-x-1 mb-2">
              <TrendingUp className="w-4 h-4 text-blue-600" />
              <h4 className="text-sm font-medium text-gray-700">Extra Skills ({match.extra_skills.length})</h4>
            </div>
            <div className="flex flex-wrap gap-1">
              {(showAllExtraSkills ? match.extra_skills : match.extra_skills.slice(0, 8)).map((skill, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-md"
                >
                  {skill}
                </span>
              ))}
              {match.extra_skills.length > 8 && (
                <button
                  onClick={() => setShowAllExtraSkills(!showAllExtraSkills)}
                  className="px-2 py-1 text-xs text-primary-600 hover:text-primary-700 hover:underline font-medium"
                >
                  {showAllExtraSkills 
                    ? 'Show less' 
                    : `+${match.extra_skills.length - 8} more`}
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Skill Match Ratio */}
      <div className="flex items-center justify-between text-sm pt-4 border-t border-gray-200">
        <span className="text-gray-600">Skill Match Ratio</span>
        <span className="font-semibold text-gray-900">
          {(match.skill_match_ratio * 100).toFixed(1)}%
        </span>
      </div>

      {/* Gaps */}
      {match.gaps && match.gaps !== 'No significant skill gaps identified.' && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">{match.gaps}</p>
        </div>
      )}

      {/* Full Text Toggle */}
      {(match.job_full_text || match.resume_full_text) && (
        <div className="mt-4 border-t border-gray-200 pt-4">
          <button
            onClick={() => setShowFullText(!showFullText)}
            className="w-full flex items-center justify-between p-3 bg-gradient-to-r from-gray-50 to-gray-100 hover:from-gray-100 hover:to-gray-200 rounded-lg transition-all duration-200 shadow-sm"
          >
            <div className="flex items-center space-x-2">
              <FileText className="w-5 h-5 text-primary-600" />
              <span className="text-sm font-semibold text-gray-800">
                {type === 'job' ? 'View Full Job Description' : 'View Full Resume'}
              </span>
            </div>
            {showFullText ? (
              <ChevronUp className="w-5 h-5 text-gray-600" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-600" />
            )}
          </button>
          
          {showFullText && (
            <div className="mt-4 p-6 bg-white rounded-lg border-2 border-gray-300 shadow-sm max-h-[600px] overflow-y-auto">
              <div className="space-y-6">
                {(() => {
                  const fullText = type === 'job' ? match.job_full_text : match.resume_full_text;
                  if (!fullText) return null;

                  // For job posts, parse structured format
                  if (type === 'job') {
                    const lines = fullText.split(/\r?\n/).map(l => l.trim()).filter(l => l);
                    const sections: Array<{ title: string; content: string[] }> = [];
                    let currentSection: { title: string; content: string[] } | null = null;
                    
                    for (let i = 0; i < lines.length; i++) {
                      const line = lines[i];
                      const nextLine = i + 1 < lines.length ? lines[i + 1] : '';
                      
                      // Check if current line is a field label (short line followed by content)
                      const isFieldLabel = 
                        line.length < 50 && 
                        !line.startsWith('-') && 
                        !line.startsWith('•') &&
                        !/^\d+\./.test(line) &&
                        nextLine.length > 0 &&
                        (
                          /^(Title|Job Title|Company|Location|Description|Job Description|Requirements|Job Requirements?|Required Qualifications?|Qualifications?|Responsibilities|Duties|Skills|Experience|Education|About|Benefits|Salary|Remuneration|Contact|Address)$/i.test(line) ||
                          (line === line.toUpperCase() && line.split(' ').length <= 4)
                        );
                      
                      if (isFieldLabel) {
                        // Save previous section
                        if (currentSection && currentSection.content.length > 0) {
                          sections.push(currentSection);
                        }
                        // Start new section
                        currentSection = {
                          title: line.replace(/:\s*$/, ''),
                          content: []
                        };
                      } else if (currentSection) {
                        // Add to current section
                        currentSection.content.push(line);
                      } else {
                        // No section yet, create default
                        currentSection = {
                          title: 'Job Details',
                          content: [line]
                        };
                      }
                    }
                    
                    // Add last section
                    if (currentSection && currentSection.content.length > 0) {
                      sections.push(currentSection);
                    }
                    
                    return sections.map((section, sectionIdx) => (
                      <div key={sectionIdx} className="pb-5 border-b border-gray-200 last:border-b-0 last:pb-0">
                        <h3 className="text-base font-bold text-gray-900 mb-3 bg-gradient-to-r from-blue-50 to-indigo-50 px-4 py-2.5 rounded-lg border-l-4 border-blue-600">
                          {section.title}
                        </h3>
                        <div className="space-y-2.5 px-4">
                          {section.content.map((line, lineIdx) => {
                            const trimmed = line.trim();
                            if (!trimmed) return null;
                            
                            const isBulletPoint = /^[-•*]\s/.test(trimmed) || /^\d+\.\s/.test(trimmed);
                            
                            if (isBulletPoint) {
                              return (
                                <div key={lineIdx} className="flex items-start space-x-3">
                                  <span className="text-blue-600 font-bold text-base leading-none mt-1">•</span>
                                  <p className="flex-1 text-gray-700 text-sm leading-relaxed">
                                    {trimmed.replace(/^[-•*]\s/, '').replace(/^\d+\.\s/, '')}
                                  </p>
                                </div>
                              );
                            } else {
                              return (
                                <p key={lineIdx} className="text-gray-700 text-sm leading-relaxed">
                                  {trimmed}
                                </p>
                              );
                            }
                          })}
                        </div>
                      </div>
                    ));
                  }
                  
                  // For resumes, use enhanced parsing with intelligent line breaking
                  let resumeText = fullText;
                  
                  // SECURITY: Remove sensitive personal information
                  // Remove entire sensitive sections
                  resumeText = resumeText.replace(/Personal Information[\s\S]*?(?=\n\n[A-Z]|Skills|Education|$)/gi, '');
                  resumeText = resumeText.replace(/Additional\s*Information[\s\S]*?(?=\n\n[A-Z]|Skills|Education|Declaration|$)/gi, '');
                  resumeText = resumeText.replace(/Personal Data[\s\S]*?(?=\n\n[A-Z]|Declaration|$)/gi, '');
                  resumeText = resumeText.replace(/Declaration[\s\S]*$/gi, '');
                  
                  // Remove specific sensitive data patterns
                  resumeText = resumeText.replace(/Date of Birth\s*:?\s*[^\n]*/gi, '');
                  resumeText = resumeText.replace(/Passport\s*(No\.?|Number)\s*:?\s*[^\n]*/gi, '');
                  resumeText = resumeText.replace(/Permanent Address[\s\S]*?(?=\n[A-Z]|$)/gi, '');
                  resumeText = resumeText.replace(/Current [Ll]ocation[\s\S]*?(?=\n[A-Z]|$)/gi, '');
                  resumeText = resumeText.replace(/Marital Status\s*:?[^\n]*/gi, '');
                  resumeText = resumeText.replace(/Sex\s*:?[^\n]*/gi, '');
                  resumeText = resumeText.replace(/Nationality\s*:?[^\n]*/gi, '');
                  
                  // Remove phone numbers (various formats)
                  resumeText = resumeText.replace(/\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b/g, '[REDACTED]');
                  resumeText = resumeText.replace(/\+\d{1,3}\s?\d{1,14}/g, '[REDACTED]');
                  
                  // Remove email addresses for privacy
                  resumeText = resumeText.replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, '[EMAIL REDACTED]');
                  
                  // Clean up multiple consecutive newlines
                  resumeText = resumeText.replace(/\n{3,}/g, '\n\n');
                  
                  // Add line breaks before common section headers if they're in the middle of text
                  const sectionKeywords = [
                    'Summary', 'Objective', 'Profile', 'Experience', 'Work Experience', 
                    'Education', 'Skills', 'Technical Skills', 'Accomplishments', 
                    'Achievements', 'Highlights', 'Certifications', 'Projects',
                    'Employment', 'Qualifications', 'Teaching', 'Consultant',
                    'Additional', 'Publications', 'Awards', 'Interests'
                  ];
                  
                  // Add newlines before section keywords that appear mid-text
                  sectionKeywords.forEach(keyword => {
                    const regex = new RegExp(`([a-z])\\s+(${keyword})\\s+`, 'g');
                    resumeText = resumeText.replace(regex, `$1\n\n$2\n`);
                  });
                  
                  // Add breaks after common date patterns (employment dates)
                  resumeText = resumeText.replace(/(\d{4})\s+(to|–|-)\s+(Current|\d{4})/gi, '$1 $2 $3\n');
                  
                  // Add breaks after company names with locations (City, State pattern)
                  resumeText = resumeText.replace(/([A-Z][a-z]+\s*,\s*[A-Z]{2})\s+([A-Z])/g, '$1\n$2');
                  
                  const lines = resumeText.split(/\r?\n/).map(l => l.trim()).filter(l => l);
                  
                  // Just display content with proper spacing, no section headers
                  return (
                    <div className="space-y-4">
                      {lines.map((line, lineIdx) => {
                        // Skip empty lines
                        if (!line) return null;
                        
                        // Check if line is a potential header (all caps or short title-like)
                        const isLikelyHeader = 
                          (line === line.toUpperCase() && line.length > 3 && line.length < 50) ||
                          (/^[A-Z][a-z]+(\s+[A-Z][a-z]+)*:?$/.test(line) && line.length < 50);
                        
                        // Break long lines into sentences for readability
                        if (line.length > 200 && line.includes('.')) {
                          const sentences = line.split(/\.\s+/);
                          return (
                            <div key={lineIdx} className="space-y-2">
                              {sentences.map((sent, sentIdx) => (
                                sent.trim() && (
                                  <p key={sentIdx} className="text-gray-700 text-sm leading-relaxed">
                                    {sent.trim()}{sentIdx < sentences.length - 1 ? '.' : ''}
                                  </p>
                                )
                              ))}
                            </div>
                          );
                        }
                        
                        // Display as header-like text (bold) or regular text
                        if (isLikelyHeader) {
                          return (
                            <p key={lineIdx} className="text-gray-900 font-semibold text-sm mt-4 first:mt-0">
                              {line}
                            </p>
                          );
                        }
                        
                        // Regular content
                        const isBulletPoint = /^[-•*]\s/.test(line) || /^\d+\.\s/.test(line);
                        if (isBulletPoint) {
                          return (
                            <div key={lineIdx} className="flex items-start space-x-2 ml-4">
                              <span className="text-green-600 font-bold text-sm leading-none mt-1">•</span>
                              <p className="flex-1 text-gray-700 text-sm leading-relaxed">
                                {line.replace(/^[-•*]\s/, '').replace(/^\d+\.\s/, '')}
                              </p>
                            </div>
                          );
                        }
                        
                        return (
                          <p key={lineIdx} className="text-gray-700 text-sm leading-relaxed">
                            {line}
                          </p>
                        );
                      })}
                    </div>
                  );
                })()}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

