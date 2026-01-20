'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { getHelpRequest, addHelpResponse, HelpRequestDetail, HelpResponseItem } from '@/lib/api';
import { ArrowLeft, Clock, MessageCircle, Send, Loader2, HelpCircle } from 'lucide-react';
import BottomNav from '@/components/BottomNav';

export default function HelpRequestPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const [helpRequest, setHelpRequest] = useState<HelpRequestDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [responseText, setResponseText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const requestId = params.id as string;

  useEffect(() => {
    if (requestId) {
      fetchHelpRequest();
    }
  }, [requestId]);

  const fetchHelpRequest = async () => {
    try {
      setLoading(true);
      const data = await getHelpRequest(requestId);
      setHelpRequest(data);
    } catch (err) {
      console.error('Failed to fetch help request:', err);
      setError('Failed to load help request');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitResponse = async () => {
    if (!responseText.trim()) return;
    
    try {
      setSubmitting(true);
      const newResponse = await addHelpResponse(requestId, { response_text: responseText.trim() });
      setHelpRequest(prev => prev ? {
        ...prev,
        responses: [...(prev.responses || []), newResponse]
      } : null);
      setResponseText('');
    } catch (err) {
      console.error('Failed to submit response:', err);
      setError('Failed to submit response');
    } finally {
      setSubmitting(false);
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffHours < 1) return 'just now';
    if (diffHours < 24) return `${diffHours} hours ago`;
    if (diffDays === 1) return '1 day ago';
    return `${diffDays} days ago`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-orange-500" />
      </div>
    );
  }

  if (error || !helpRequest) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">{error || 'Help request not found'}</p>
          <button
            onClick={() => router.back()}
            className="text-orange-600 font-medium"
          >
            Go back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-lg mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.back()}
              className="p-2 -ml-2 hover:bg-gray-100 rounded-full"
            >
              <ArrowLeft className="w-5 h-5 text-gray-600" />
            </button>
            <h1 className="text-lg font-semibold text-gray-900">Help Request</h1>
          </div>
        </div>
      </div>

      {/* Help Request Card */}
      <main className="max-w-lg mx-auto px-4 py-6 pb-48">
        <div className="bg-white rounded-2xl border p-4 mb-6">
          {/* Header */}
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center">
              <HelpCircle className="w-5 h-5 text-orange-500" />
            </div>
            <div className="flex-1">
              <span className="font-medium text-gray-900">{helpRequest.teacher_name}</span>
              <div className="flex items-center gap-1 text-gray-400 text-sm">
                <Clock className="w-3 h-3" />
                {formatTimeAgo(helpRequest.created_at)}
              </div>
            </div>
          </div>

          {/* Concept Tag */}
          <div className="mb-2">
            <span className="inline-block px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
              Concept
            </span>
          </div>

          {/* Query Text */}
          <h2 className="text-lg font-medium text-gray-900 mb-2">
            &quot;{helpRequest.original_query_text}&quot;
          </h2>

          {/* Language Tag */}
          {helpRequest.detected_language && (
            <span className="inline-block px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-600">
              {helpRequest.detected_language}
            </span>
          )}
        </div>

        {/* Responses Section */}
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-4">
            <MessageCircle className="w-5 h-5 text-gray-600" />
            <h3 className="font-medium text-gray-900">
              Responses ({helpRequest.responses.length})
            </h3>
          </div>

          {helpRequest.responses.length > 0 ? (
            <div className="space-y-3">
              {helpRequest.responses.map((response) => (
                <div key={response.id} className="bg-white rounded-xl border p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                      <span className="text-green-700 text-sm font-medium">
                        {response.teacher_name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-900 text-sm">
                        {response.teacher_name}
                      </span>
                      <span className="text-gray-400 text-xs ml-2">
                        {formatTimeAgo(response.created_at)}
                      </span>
                    </div>
                  </div>
                  <p className="text-gray-700 text-sm">{response.response_text}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-gray-50 rounded-xl p-6 text-center">
              <p className="text-gray-500">No responses yet. Be the first to help!</p>
            </div>
          )}
        </div>
      </main>

      {/* Response Input - Fixed above bottom nav */}
      <div className="fixed bottom-16 left-0 right-0 bg-white border-t p-4 z-20">
        <div className="max-w-lg mx-auto flex gap-2">
          <input
            type="text"
            value={responseText}
            onChange={(e) => setResponseText(e.target.value)}
            placeholder="Share your advice or solution..."
            className="flex-1 px-4 py-3 border border-gray-200 rounded-full focus:outline-none focus:border-orange-300"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmitResponse();
              }
            }}
          />
          <button
            onClick={handleSubmitResponse}
            disabled={!responseText.trim() || submitting}
            className="w-12 h-12 bg-orange-500 text-white rounded-full flex items-center justify-center hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>

      {/* Bottom Navigation */}
      <BottomNav />
    </div>
  );
}
