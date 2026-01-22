'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { uploadFileToCloudinary, checkCloudinaryStatus, getRecentHelpRequests, HelpRequestDetail, suggestTopic, createTopicWithTranslations } from '@/lib/api';
import { ArrowLeft, Video, FileText, Upload, Loader2, CheckCircle, AlertCircle, HelpCircle, Clock, ChevronRight } from 'lucide-react';
import BottomNav from '@/components/BottomNav';

export default function UploadPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [contentType, setContentType] = useState<'video' | 'document'>('video');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [conceptId, setConceptId] = useState(searchParams.get('concept_id') || '');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cloudinaryReady, setCloudinaryReady] = useState<boolean | null>(null);
  const [helpRequests, setHelpRequests] = useState<HelpRequestDetail[]>([]);
  const [loadingHelp, setLoadingHelp] = useState(true);
  const [selectedHelpRequestId, setSelectedHelpRequestId] = useState<string | null>(null);

  useEffect(() => {
    checkCloudinary();
    fetchHelpRequests();
  }, []);



  const checkCloudinary = async () => {
    try {
      const status = await checkCloudinaryStatus();
      setCloudinaryReady(status.configured);
    } catch (err) {
      setCloudinaryReady(false);
    }
  };

  const fetchHelpRequests = async () => {
    try {
      setLoadingHelp(true);
      const data = await getRecentHelpRequests(5);
      setHelpRequests(data);
    } catch (err) {
      console.error('Failed to fetch help requests:', err);
    } finally {
      setLoadingHelp(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile || !title.trim()) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let finalConceptId = conceptId;

      // If no concept selected (which is expected now), try to auto-suggest
      if (!finalConceptId) {
        // 1. Suggest Topic
        const suggestion = await suggestTopic(title, description);

        if (suggestion.matched_topic_id) {
          finalConceptId = suggestion.matched_topic_id;
        } else if (suggestion.suggested_new_topic && suggestion.suggested_new_topic_id) {
          // 2. Create New Topic if needed
          await createTopicWithTranslations(
            suggestion.suggested_new_topic_id,
            suggestion.suggested_new_topic,
            suggestion.suggested_new_topic_hi || undefined,
            suggestion.suggested_new_topic_kn || undefined,
            suggestion.synonyms_en || [],
            suggestion.synonyms_hi || [],
            suggestion.synonyms_kn || []
          );

          finalConceptId = suggestion.suggested_new_topic_id;
        } else {
          throw new Error('Could not automatically determine a topic. Please try a more descriptive title.');
        }
      }

      if (!finalConceptId) {
        throw new Error('Failed to determine topic.');
      }

      // 3. Upload File
      await uploadFileToCloudinary({
        file: selectedFile,
        title: title.trim(),
        concept_id: finalConceptId,
        content_type: contentType,
        description: description.trim(),
        language: user?.language_preference || 'en',
        help_request_id: selectedHelpRequestId || undefined,
      });

      router.push('/');
    } catch (err) {
      console.error('Upload flow failed:', err);
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleHelpRequestClick = (request: HelpRequestDetail) => {
    // Toggle selection - if already selected, deselect
    if (selectedHelpRequestId === request.id) {
      setSelectedHelpRequestId(null);
      setConceptId('');
      setTitle('');
    } else {
      setSelectedHelpRequestId(request.id);
      if (request.concept_id) {
        setConceptId(request.concept_id);
      }
      setTitle(request.original_query_text);
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) return 'just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return '1 day ago';
    return `${diffDays} days ago`;
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
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
            <h1 className="text-lg font-semibold text-gray-900">Upload Content</h1>
          </div>
        </div>
      </div>

      <main className="max-w-lg mx-auto px-4 py-6">
        {/* Help Needed Section */}
        {helpRequests.length > 0 && (
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <HelpCircle className="w-5 h-5 text-orange-500" />
              <h2 className="font-semibold text-gray-900">Help Needed</h2>
              <span className="text-xs bg-orange-100 text-orange-600 px-2 py-0.5 rounded-full">
                {helpRequests.length} requests
              </span>
            </div>
            <p className="text-sm text-gray-500 mb-3">
              Teachers are looking for help on these topics. Upload content to help them!
            </p>

            <div className="space-y-2">
              {loadingHelp ? (
                <div className="flex justify-center py-4">
                  <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
                </div>
              ) : (
                helpRequests.map((request) => {
                  const isSelected = selectedHelpRequestId === request.id;
                  return (
                    <button
                      key={request.id}
                      onClick={() => handleHelpRequestClick(request)}
                      className={`w-full rounded-xl border p-3 flex items-center gap-3 transition-colors text-left ${isSelected
                        ? 'bg-orange-50 border-orange-400 ring-2 ring-orange-200'
                        : 'bg-white hover:border-orange-300'
                        }`}
                    >
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${isSelected ? 'bg-orange-500' : 'bg-orange-100'
                        }`}>
                        {isSelected ? (
                          <CheckCircle className="w-5 h-5 text-white" />
                        ) : (
                          <HelpCircle className="w-5 h-5 text-orange-500" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 truncate">
                          &quot;{request.original_query_text}&quot;
                        </p>
                        <div className="flex items-center gap-2 text-xs text-gray-500">
                          <span>{request.teacher_name}</span>
                          <span>•</span>
                          <Clock className="w-3 h-3" />
                          <span>{formatTimeAgo(request.created_at)}</span>
                        </div>
                      </div>
                      {isSelected ? (
                        <span className="text-xs text-orange-600 font-medium">Selected</span>
                      ) : (
                        <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
                      )}
                    </button>
                  );
                })
              )}
            </div>
          </div>
        )}

        {/* Divider */}
        {helpRequests.length > 0 && (
          <div className="flex items-center gap-4 mb-6">
            <div className="flex-1 h-px bg-gray-200"></div>
            <span className="text-sm text-gray-400">or upload your own</span>
            <div className="flex-1 h-px bg-gray-200"></div>
          </div>
        )}

        {/* Content Type Selection */}
        <p className="text-sm text-gray-500 mb-3">What are you uploading?</p>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <button
            onClick={() => setContentType('video')}
            className={`p-4 rounded-2xl border-2 flex flex-col items-center gap-2 transition-all ${contentType === 'video'
              ? 'border-orange-300 bg-orange-50'
              : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
          >
            <Video className={`w-6 h-6 ${contentType === 'video' ? 'text-orange-600' : 'text-gray-500'}`} />
            <span className={`text-sm font-medium ${contentType === 'video' ? 'text-gray-900' : 'text-gray-600'}`}>
              Video
            </span>
          </button>

          <button
            onClick={() => setContentType('document')}
            className={`p-4 rounded-2xl border-2 flex flex-col items-center gap-2 transition-all ${contentType === 'document'
              ? 'border-orange-300 bg-orange-50'
              : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
          >
            <FileText className={`w-6 h-6 ${contentType === 'document' ? 'text-orange-600' : 'text-gray-500'}`} />
            <span className={`text-sm font-medium ${contentType === 'document' ? 'text-gray-900' : 'text-gray-600'}`}>
              PDF/Doc
            </span>
          </button>
        </div>

        {/* Cloudinary Status Warning */}
        {cloudinaryReady === false && (
          <div className="bg-amber-50 rounded-2xl p-4 border border-amber-200 mb-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-amber-800">File upload not configured</p>
              <p className="text-xs text-amber-600 mt-1">Please configure Cloudinary credentials to enable file uploads.</p>
            </div>
          </div>
        )}

        {/* File Upload Area */}
        <div
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-gray-300 rounded-2xl p-6 text-center cursor-pointer hover:border-gray-400 transition-colors bg-white mb-4"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept={contentType === 'video' ? 'video/*' : '.pdf,.doc,.docx'}
            onChange={handleFileSelect}
            className="hidden"
          />

          {selectedFile ? (
            <div>
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
              </div>
              <p className="text-sm font-medium text-gray-900">{selectedFile.name}</p>
              <p className="text-xs text-gray-500 mt-1">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
          ) : (
            <div>
              <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <Upload className="w-5 h-5 text-gray-400" />
              </div>
              <p className="text-sm text-gray-500">
                Tap to select a {contentType === 'video' ? 'video' : 'document'}
              </p>
            </div>
          )}
        </div>

        {/* Title Input */}
        <div className="bg-white rounded-2xl p-4 border mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Title *</label>
          <input
            type="text"
            value={title}
            onChange={(e) => {
              setTitle(e.target.value);
            }}
            placeholder="e.g., Water Cycle Explanation Video"
            className="w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:border-orange-300"
          />


        </div>





        {/* Description Input */}
        <div className="bg-white rounded-2xl p-4 border mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Description (optional)</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Briefly describe what this content covers..."
            className="w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:border-orange-300 h-24 resize-none"
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
          disabled={loading || !selectedFile || !title.trim() || cloudinaryReady === false}
          className={`w-full py-4 rounded-2xl font-medium transition-all flex items-center justify-center gap-2 ${selectedFile && title.trim() && cloudinaryReady !== false
            ? 'bg-orange-400 hover:bg-orange-500 text-white'
            : 'bg-orange-200 text-orange-400 cursor-not-allowed'
            }`}
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Processing & Uploading...
            </>
          ) : (
            'Publish Content'
          )}
        </button>
      </main>

      <BottomNav />
    </div>
  );
}
