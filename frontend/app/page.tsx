'use client';

import { useState } from 'react';
import { Search, FileText, Users, Loader2, AlertCircle } from 'lucide-react';
import FileUpload from '@/components/FileUpload';
import MatchCard from '@/components/MatchCard';
import ModelSelector from '@/components/ModelSelector';
import { api, MatchesResponse } from '@/lib/api';

type Mode = 'resume-to-jobs' | 'job-to-candidates';

export default function Home() {
  const [mode, setMode] = useState<Mode>('resume-to-jobs');
  const [file, setFile] = useState<File | null>(null);
  const [model, setModel] = useState<'bert' | 'roberta'>('bert');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<MatchesResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile);
    setResults(null);
    setError(null);
  };

  const handleSearch = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      let response: MatchesResponse;
      
      if (mode === 'resume-to-jobs') {
        response = await api.resumeToJobs(file, model, 10);
      } else {
        response = await api.jobToCandidates(file, model, 10);
      }

      setResults(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">AI Recruitment System</h1>
              <p className="text-gray-600 mt-1">Intelligent job-resume matching powered by BERT & RoBERTa</p>
            </div>
            <div className="flex items-center space-x-4">
              <ModelSelector model={model} onModelChange={setModel} />
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Mode Selection */}
        <div className="mb-8">
          <div className="flex rounded-lg border border-gray-300 overflow-hidden bg-white shadow-sm">
            <button
              onClick={() => {
                setMode('resume-to-jobs');
                setResults(null);
                setFile(null);
                setError(null);
              }}
              className={`
                flex-1 px-6 py-4 text-left transition-colors
                ${mode === 'resume-to-jobs'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
                }
              `}
            >
              <div className="flex items-center space-x-3">
                <FileText className="w-5 h-5" />
                <div>
                  <div className="font-semibold">Resume to Jobs</div>
                  <div className={`text-sm ${mode === 'resume-to-jobs' ? 'text-primary-100' : 'text-gray-500'}`}>
                    Find best jobs for a resume
                  </div>
                </div>
              </div>
            </button>
            <button
              onClick={() => {
                setMode('job-to-candidates');
                setResults(null);
                setFile(null);
                setError(null);
              }}
              className={`
                flex-1 px-6 py-4 text-left transition-colors border-l border-gray-300
                ${mode === 'job-to-candidates'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
                }
              `}
            >
              <div className="flex items-center space-x-3">
                <Users className="w-5 h-5" />
                <div>
                  <div className="font-semibold">Job to Candidates</div>
                  <div className={`text-sm ${mode === 'job-to-candidates' ? 'text-primary-100' : 'text-gray-500'}`}>
                    Find best candidates for a job
                  </div>
                </div>
              </div>
            </button>
          </div>
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <FileUpload
            onFileSelect={handleFileSelect}
            label={mode === 'resume-to-jobs' ? 'Upload Resume PDF' : 'Upload Job Description PDF'}
            description={
              mode === 'resume-to-jobs'
                ? 'Upload a resume PDF to find matching job opportunities'
                : 'Upload a job description PDF to find matching candidates'
            }
            isLoading={loading}
          />

          <button
            onClick={handleSearch}
            disabled={!file || loading}
            className={`
              mt-6 w-full py-3 px-6 rounded-lg font-semibold text-white
              transition-all duration-200 flex items-center justify-center space-x-2
              ${!file || loading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-primary-600 hover:bg-primary-700 shadow-md hover:shadow-lg'
              }
            `}
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Search className="w-5 h-5" />
                <span>Find Matches</span>
              </>
            )}
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-8 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-semibold text-red-800">Error</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Results */}
        {results && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Match Results</h2>
                <p className="text-gray-600 mt-1">
                  Found {results.total_matches} matches using {results.model_used.toUpperCase()} model
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-6">
              {results.matches.map((match) => (
                <MatchCard
                  key={match.rank}
                  match={match}
                  type={mode === 'resume-to-jobs' ? 'job' : 'candidate'}
                />
              ))}
            </div>

            {results.matches.length === 0 && (
              <div className="text-center py-12 bg-white rounded-xl">
                <p className="text-gray-500">No matches found. Try adjusting your search criteria.</p>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 bg-white border-t border-gray-200 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-600">
          <p>AI Recruitment System - Powered by BERT & RoBERTa</p>
        </div>
      </footer>
    </div>
  );
}

