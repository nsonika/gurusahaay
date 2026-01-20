'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import VoiceButton from '@/components/VoiceButton';
import { useVoiceRecorder } from '@/hooks/useVoiceRecorder';
import { createHelpRequest } from '@/lib/api';
import { Loader2, Volume2, MessageSquare, Users, Sparkles, Send, MoreHorizontal } from 'lucide-react';

// Predefined problem categories
const problemCategories = [
  { id: 'CLASSROOM_DISCIPLINE', icon: Volume2, label: 'Discipline / Classroom Noise' },
  { id: 'CLASSROOM_ATTENTION', icon: MessageSquare, label: 'Concept Not Understood' },
  { id: 'CLASSROOM_SLOW_LEARNERS', icon: Users, label: 'Student Engagement Low' },
  { id: 'OTHER', icon: MoreHorizontal, label: 'Other' },
];

export default function HelpPage() {
  const { user } = useAuth();
  const router = useRouter();
  
  const [selectedProblem, setSelectedProblem] = useState('');
  const [customProblem, setCustomProblem] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { isRecording, audioBase64, startRecording, stopRecording } = useVoiceRecorder();

  const handleSubmit = async () => {
    setError('');
    setLoading(true);

    try {
      const queryText = selectedProblem || customProblem;
      
      if (!queryText.trim() && !audioBase64) {
        setError('Please select a problem or describe your issue');
        setLoading(false);
        return;
      }

      let requestData: Parameters<typeof createHelpRequest>[0];
      
      if (audioBase64) {
        requestData = {
          audio_base64: audioBase64,
          request_type: 'voice',
          category: selectedProblem || undefined,
        };
      } else if (selectedProblem && customProblem) {
        // Both category selected AND custom problem described
        requestData = {
          query_text: customProblem,
          request_type: 'text',
          category: selectedProblem,
        };
      } else if (selectedProblem) {
        // Only category selected
        requestData = {
          query_text: selectedProblem,
          request_type: 'predefined',
          category: selectedProblem,
        };
      } else {
        // Only custom problem
        requestData = {
          query_text: customProblem,
          request_type: 'text',
        };
      }

      const helpRequest = await createHelpRequest(requestData);
      
      if (helpRequest.concept_id) {
        router.push(`/suggestions?concept_id=${helpRequest.concept_id}&summary=${encodeURIComponent(customProblem || selectedProblem)}`);
      } else {
        setError('Could not understand your question. Please try again.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process request');
    } finally {
      setLoading(false);
    }
  };

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
            Need Help Now
            <Sparkles className="w-5 h-5 text-orange-500" />
          </h1>
        </div>
      </div>
      
      <main className="max-w-lg mx-auto px-4 py-6">
        {/* AI Banner */}
        <div className="bg-green-50 rounded-2xl p-4 mb-6 border border-green-100">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
              <Sparkles className="w-4 h-4 text-green-600" />
            </div>
            <p className="text-sm text-green-800">
              AI-powered suggestions - Instant solutions for your problem!
            </p>
          </div>
        </div>

        {/* Problem Selection */}
        <p className="text-gray-700 font-medium mb-4">What problem are you facing?</p>
        
        <div className="space-y-3 mb-6">
          {problemCategories.map((problem) => {
            const Icon = problem.icon;
            const isSelected = selectedProblem === problem.id;
            
            return (
              <button
                key={problem.id}
                onClick={() => {
                  setSelectedProblem(isSelected ? '' : problem.id);
                  setCustomProblem('');
                }}
                className={`w-full flex items-center gap-4 p-4 rounded-2xl border-2 transition-all ${
                  isSelected
                    ? 'border-orange-300 bg-orange-50'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }`}
              >
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                  isSelected ? 'bg-orange-100' : 'bg-gray-100'
                }`}>
                  <Icon className={`w-5 h-5 ${isSelected ? 'text-orange-600' : 'text-gray-500'}`} />
                </div>
                <span className={`font-medium ${isSelected ? 'text-gray-900' : 'text-gray-700'}`}>
                  {problem.label}
                </span>
              </button>
            );
          })}
        </div>

        {/* Divider */}
        <div className="flex items-center gap-4 mb-6">
          <div className="flex-1 h-px bg-gray-200" />
          <span className="text-sm text-gray-400">and describe your problem</span>
          <div className="flex-1 h-px bg-gray-200" />
        </div>

        {/* Custom Problem Input */}
        <div className="mb-6">
          <div className="relative">
            <textarea
              value={customProblem}
              onChange={(e) => {
                setCustomProblem(e.target.value);
                setSelectedProblem('');
              }}
              placeholder="photosyentesis"
              className="w-full p-4 border-2 border-amber-200 rounded-2xl bg-amber-50 resize-none h-24 focus:outline-none focus:border-amber-300"
              maxLength={500}
            />
            <span className="absolute bottom-3 right-3 text-xs text-gray-400">
              {customProblem.length}/500
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-2 text-center">Or describe your problem</p>
        </div>

        {/* Voice Button */}
        <div className="flex justify-center mb-6">
          <VoiceButton
            isRecording={isRecording}
            isProcessing={loading}
            onStart={startRecording}
            onStop={stopRecording}
          />
        </div>

        {/* Error */}
        {error && (
          <div className="text-red-600 text-sm bg-red-50 p-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        {/* Submit Button */}
        <button
          onClick={handleSubmit}
          disabled={loading || (!selectedProblem && !customProblem.trim() && !audioBase64)}
          className={`w-full py-4 rounded-2xl font-medium transition-all flex items-center justify-center gap-2 ${
            (selectedProblem || customProblem.trim() || audioBase64)
              ? 'bg-orange-500 hover:bg-orange-600 text-white'
              : 'bg-orange-200 text-orange-400 cursor-not-allowed'
          }`}
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Finding suggestions...
            </>
          ) : (
            <>
              <Send className="w-5 h-5" />
              Get Suggestions
            </>
          )}
        </button>
      </main>
    </div>
  );
}
