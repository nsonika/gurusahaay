'use client';

import { Content } from '@/lib/api';
import { Star, ExternalLink, CheckCircle, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';

interface ContentCardProps {
  content: Content;
  onFeedback?: (contentId: string) => void;
  onClick?: () => void;
}

export default function ContentCard({ content, onFeedback, onClick }: ContentCardProps) {
  const contentTypeColors: Record<string, string> = {
    video: 'bg-red-100 text-red-700',
    document: 'bg-blue-100 text-blue-700',
    activity: 'bg-green-100 text-green-700',
    tip: 'bg-yellow-100 text-yellow-700',
  };

  const languageLabels: Record<string, string> = {
    en: 'English',
    kn: 'ಕನ್ನಡ',
    hi: 'हिंदी',
  };

  return (
    <div 
      className="card hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            {content.content_type && (
              <span className={clsx(
                'text-xs px-2 py-0.5 rounded-full font-medium',
                contentTypeColors[content.content_type] || 'bg-gray-100 text-gray-700'
              )}>
                {content.content_type}
              </span>
            )}
            <span className="text-xs text-gray-500">
              {languageLabels[content.language] || content.language}
            </span>
          </div>
          
          <h3 className="font-medium text-gray-900 line-clamp-2">{content.title}</h3>
          
          {content.description && (
            <p className="text-sm text-gray-600 mt-1 line-clamp-2">{content.description}</p>
          )}
          
          <div className="flex items-center gap-3 mt-3">
            {content.feedback_score !== undefined && content.feedback_score > 0 && (
              <div className="flex items-center gap-1 text-sm text-yellow-600">
                <Star className="w-4 h-4 fill-current" />
                <span>{content.feedback_score}</span>
              </div>
            )}
            
            {content.is_verified ? (
              <div className="flex items-center gap-1 text-sm text-green-600">
                <CheckCircle className="w-4 h-4" />
                <span>Verified</span>
              </div>
            ) : (
              <div className="flex items-center gap-1 text-sm text-orange-500">
                <AlertCircle className="w-4 h-4" />
                <span>Unverified</span>
              </div>
            )}
            
            {content.uploader_name && (
              <span className="text-sm text-gray-500">by {content.uploader_name}</span>
            )}
          </div>
        </div>
        
        {content.content_url && (
          <a
            href={content.content_url}
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 text-gray-400 hover:text-primary-600"
            onClick={(e) => e.stopPropagation()}
          >
            <ExternalLink className="w-5 h-5" />
          </a>
        )}
      </div>
      
      {onFeedback && (
        <div className="mt-4 pt-3 border-t border-gray-100">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onFeedback(content.id);
            }}
            className="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            Give Feedback
          </button>
        </div>
      )}
    </div>
  );
}
