'use client';

import { Brain, Zap } from 'lucide-react';

interface ModelSelectorProps {
  model: 'bert' | 'roberta';
  onModelChange: (model: 'bert' | 'roberta') => void;
}

export default function ModelSelector({ model, onModelChange }: ModelSelectorProps) {
  return (
    <div className="flex items-center space-x-4">
      <label className="text-sm font-medium text-gray-700">Model:</label>
      <div className="flex rounded-lg border border-gray-300 overflow-hidden">
        <button
          onClick={() => onModelChange('bert')}
          className={`
            px-4 py-2 text-sm font-medium transition-colors
            ${model === 'bert' 
              ? 'bg-primary-600 text-white' 
              : 'bg-white text-gray-700 hover:bg-gray-50'
            }
          `}
        >
          <div className="flex items-center space-x-2">
            <Brain className="w-4 h-4" />
            <span>BERT</span>
          </div>
        </button>
        <button
          onClick={() => onModelChange('roberta')}
          className={`
            px-4 py-2 text-sm font-medium transition-colors border-l border-gray-300
            ${model === 'roberta' 
              ? 'bg-primary-600 text-white' 
              : 'bg-white text-gray-700 hover:bg-gray-50'
            }
          `}
        >
          <div className="flex items-center space-x-2">
            <Zap className="w-4 h-4" />
            <span>RoBERTa</span>
          </div>
        </button>
      </div>
    </div>
  );
}

