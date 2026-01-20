'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import Header from '@/components/Header';
import FeedbackModal from '@/components/FeedbackModal';
import { getSuggestions, addFeedback, getConcept, SuggestionResponse, Concept, Content } from '@/lib/api';
import { AlertCircle, Loader2, Lightbulb, Youtube, Globe, Clock, Users, Sparkles, CheckCircle } from 'lucide-react';

export default function SuggestionsPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { user } = useAuth();
  
  const conceptId = searchParams.get('concept_id');
  const problemSummary = searchParams.get('summary') || '';
  
  const [suggestions, setSuggestions] = useState<SuggestionResponse | null>(null);
  const [concept, setConcept] = useState<Concept | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [helpPosted, setHelpPosted] = useState(false);
  
  // Feedback modal state
  const [feedbackContent, setFeedbackContent] = useState<Content | null>(null);

  useEffect(() => {
    if (!conceptId) {
      router.push('/help');
      return;
    }

    Promise.all([
      getSuggestions(conceptId),
      getConcept(conceptId)
    ])
      .then(([suggestionsData, conceptData]) => {
        setSuggestions(suggestionsData);
        setConcept(conceptData);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Failed to load suggestions');
      })
      .finally(() => setLoading(false));
  }, [conceptId, router]);

  const handleFeedbackSubmit = async (data: { worked: boolean; rating: number; comment?: string }) => {
    if (!feedbackContent) return;
    try {
      await addFeedback(feedbackContent.id, data);
      setFeedbackContent(null);
    } catch (err) {
      console.error('Feedback error:', err);
    }
  };

  // Get display name for concept
  const getConceptDisplayName = () => {
    if (!concept) return conceptId;
    const langSynonym = concept.synonyms.find((s: { language: string }) => s.language === user?.language_preference);
    if (langSynonym) return langSynonym.term;
    const enSynonym = concept.synonyms.find((s: { language: string }) => s.language === 'en');
    if (enSynonym) return enSynonym.term;
    return concept.description_en || conceptId;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header title="Top Solutions for You" showBack backHref="/help" />
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-lg mx-auto px-4 py-4 flex items-center gap-3">
          <button onClick={() => router.back()} className="p-2 -ml-2 hover:bg-gray-100 rounded-full">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h1 className="text-lg font-semibold flex items-center gap-2">
            Top Solutions for You
            <Sparkles className="w-5 h-5 text-orange-500" />
          </h1>
        </div>
      </div>
      
      <main className="max-w-lg mx-auto px-4 py-6 space-y-4">
        {/* Problem Summary Card */}
        <div className="bg-amber-50 rounded-2xl p-4 border border-amber-100">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0">
              <Lightbulb className="w-4 h-4 text-amber-600" />
            </div>
            <div>
              <p className="text-xs text-amber-700 font-medium mb-1">Problem Summary</p>
              <p className="text-sm text-gray-800">
                {problemSummary || `Students struggle to visualize and understand ${getConceptDisplayName()?.toLowerCase()}.`}
              </p>
            </div>
          </div>
        </div>

        {/* External Content Warning */}
        {(suggestions?.source === 'external_fallback' || suggestions?.source === 'google_search') && (
          <div className="bg-blue-50 rounded-2xl p-4 border border-blue-100">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                <Globe className="w-4 h-4 text-blue-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-blue-800">
                  {suggestions?.source === 'google_search' 
                    ? '🔍 Found via Google Search' 
                    : 'Found suggestions from YouTube/Web'}
                </p>
                <p className="text-xs text-blue-600 mt-0.5">
                  These are external resources. Post to community for teacher-verified content!
                </p>
                {helpPosted ? (
                  <div className="mt-3 flex items-center gap-2 text-green-700 text-sm">
                    <CheckCircle className="w-4 h-4" />
                    Posted to community! Teachers will respond soon.
                  </div>
                ) : (
                  <button 
                    onClick={() => {
                      setHelpPosted(true);
                    }}
                    className="mt-3 flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-full text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    <Users className="w-4 h-4" />
                    Post to Help Needed
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="text-red-600 text-sm bg-red-50 p-4 rounded-lg">
            {error}
          </div>
        )}

        {/* Suggestions list */}
        {suggestions && suggestions.suggestions.length > 0 ? (
          <div className="space-y-4">
            {suggestions.suggestions.map((content, index) => (
              <SolutionCard 
                key={content.id} 
                content={content} 
                index={index + 1}
                onTry={() => setFeedbackContent(content)}
              />
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-2xl p-8 text-center border">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <AlertCircle className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="font-medium text-gray-900 mb-2">No content found</h3>
            <p className="text-sm text-gray-500 mb-4">
              Be the first to share helpful content for this topic!
            </p>
            
            {/* Post to Help Needed */}
            {helpPosted ? (
              <div className="flex items-center justify-center gap-2 text-green-700 text-sm mb-4">
                <CheckCircle className="w-4 h-4" />
                Posted to community! Teachers will respond soon.
              </div>
            ) : (
              <button 
                onClick={() => {
                  setHelpPosted(true);
                }}
                className="mb-4 flex items-center justify-center gap-2 px-4 py-2 bg-green-50 border border-green-200 rounded-full text-sm font-medium text-green-700 hover:bg-green-100 mx-auto"
              >
                <Users className="w-4 h-4" />
                Post to Help Needed
              </button>
            )}
            
            <button
              onClick={() => router.push('/upload')}
              className="btn-primary"
            >
              Upload Content
            </button>
          </div>
        )}
      </main>

      {/* Feedback Modal */}
      <FeedbackModal
        isOpen={!!feedbackContent}
        onClose={() => setFeedbackContent(null)}
        onSubmit={handleFeedbackSubmit}
        contentTitle={feedbackContent?.title || ''}
      />
    </div>
  );
}

// Solution Card Component matching the reference design
function SolutionCard({ content, index, onTry }: { content: Content; index: number; onTry: () => void }) {
  const router = useRouter();
  const isYouTube = content.content_url?.includes('youtube') || content.content_url?.includes('youtu.be');
  const isInternal = content.source_type === 'internal';
  const difficulty = 'Easy'; // Could be derived from content metadata
  const duration = content.content_type === 'video' ? '10 min' : '5 min';
  
  // Motivational messages
  const motivationalMessages = [
    "You're doing a great job making complex science simple for your students. Keep up the amazing work!",
    "Your dedication to finding creative solutions inspires your students every day!",
    "Great teachers like you make learning memorable. Your students are lucky!",
  ];
  
  return (
    <div className="bg-white rounded-2xl border overflow-hidden">
      {/* Header with badges */}
      <div className="p-4 pb-3">
        <div className="flex items-center gap-2 mb-3">
          <span className="w-6 h-6 rounded-full bg-orange-500 text-white text-xs font-bold flex items-center justify-center">
            {index}
          </span>
          {isYouTube ? (
            <span className="flex items-center gap-1 px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">
              <Youtube className="w-3 h-3" />
              YouTube
            </span>
          ) : isInternal ? (
            <span className="flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
              <Users className="w-3 h-3" />
              Upload
            </span>
          ) : (
            <span className="flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs font-medium">
              <Globe className="w-3 h-3" />
              Web
            </span>
          )}
          <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
            {difficulty}
          </span>
          <span className="flex items-center gap-1 text-gray-500 text-xs ml-auto">
            <Clock className="w-3 h-3" />
            {duration}
          </span>
        </div>
        
        {/* Title */}
        <h3 className="font-semibold text-gray-900 mb-2">{content.title}</h3>
        
        {/* Description */}
        {content.description && (
          <p className="text-sm text-gray-600 leading-relaxed">
            {content.description}
          </p>
        )}
      </div>
      
      {/* Action Button */}
      <div className="px-4 pb-4">
        {isInternal ? (
          <button 
            onClick={() => router.push(`/content/${content.id}`)}
            className="w-full py-3 bg-orange-500 hover:bg-orange-600 text-white font-medium rounded-xl transition-colors"
          >
            View Content
          </button>
        ) : (
          <button 
            onClick={onTry}
            className="w-full py-3 bg-orange-500 hover:bg-orange-600 text-white font-medium rounded-xl transition-colors"
          >
            Try in next class
          </button>
        )}
      </div>
      
      {/* Motivational Message (show on some cards) */}
      {index === 2 && (
        <div className="mx-4 mb-4 p-3 bg-green-50 rounded-xl">
          <p className="text-sm text-green-700 text-center italic">
            {motivationalMessages[index % motivationalMessages.length]}
          </p>
        </div>
      )}
    </div>
  );
}
