'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { getContentById, Content, recordContentView, toggleContentLike } from '@/lib/api';
import { ArrowLeft, FileText, Play, Clock, Eye, Heart, Loader2 } from 'lucide-react';
import BottomNav from '@/components/BottomNav';

export default function ContentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const [content, setContent] = useState<Content | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [likesCount, setLikesCount] = useState(0);
  const [viewsCount, setViewsCount] = useState(0);
  const [userLiked, setUserLiked] = useState(false);
  const [likeLoading, setLikeLoading] = useState(false);

  const contentId = params.id as string;

  useEffect(() => {
    if (contentId) {
      fetchContent();
      recordView();
    }
  }, [contentId]);

  const fetchContent = async () => {
    try {
      setLoading(true);
      const data = await getContentById(contentId);
      setContent(data);
      setLikesCount(data.likes_count || 0);
      setViewsCount(data.views_count || 0);
      setUserLiked(data.user_liked || false);
    } catch (err) {
      console.error('Failed to fetch content:', err);
      setError('Failed to load content');
    } finally {
      setLoading(false);
    }
  };

  const recordView = async () => {
    try {
      await recordContentView(contentId);
      setViewsCount(prev => prev + 1);
    } catch (err) {
      console.error('Failed to record view:', err);
    }
  };

  const handleLike = async () => {
    if (likeLoading) return;
    setLikeLoading(true);
    try {
      const result = await toggleContentLike(contentId);
      setUserLiked(result.liked);
      setLikesCount(result.likes_count);
    } catch (err) {
      console.error('Failed to toggle like:', err);
    } finally {
      setLikeLoading(false);
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

  const isVideo = content?.content_type === 'video';
  const isDocument = content?.content_type === 'document';
  
  // For documents, use Google Docs Viewer to display inline instead of downloading
  const getViewUrl = (url: string, contentType: string) => {
    if (contentType === 'document' && url) {
      // Use Google Docs Viewer to display PDF/docs in browser
      return `https://docs.google.com/viewer?url=${encodeURIComponent(url)}&embedded=true`;
    }
    return url;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-orange-500" />
      </div>
    );
  }

  if (error || !content) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">{error || 'Content not found'}</p>
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
    <div className="min-h-screen bg-gray-50 pb-20">
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
            <h1 className="text-lg font-semibold text-gray-900">Content Details</h1>
          </div>
        </div>
      </div>

      <main className="max-w-lg mx-auto px-4 py-6">
        {/* Preview Area */}
        <div className="bg-gray-100 rounded-2xl aspect-video flex items-center justify-center mb-4">
          {isVideo ? (
            <div className="text-center">
              <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-2 shadow-md">
                <Play className="w-8 h-8 text-gray-600 ml-1" />
              </div>
              <p className="text-gray-500 text-sm">Video Preview</p>
            </div>
          ) : (
            <div className="text-center">
              <FileText className="w-16 h-16 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-500 text-sm">Document</p>
            </div>
          )}
        </div>

        {/* View Button */}
        <a
          href={getViewUrl(content.content_url ?? '', content.content_type ?? '')}
          target="_blank"
          rel="noopener noreferrer"
          className="w-full bg-orange-500 text-white py-3 px-6 rounded-xl font-medium flex items-center justify-center gap-2 hover:bg-orange-600 transition-colors mb-6"
        >
          {isVideo ? (
            <>
              <Play className="w-5 h-5" />
              Watch Video
            </>
          ) : (
            <>
              <FileText className="w-5 h-5" />
              View Document
            </>
          )}
        </a>

        {/* Content Info */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900">{content.title}</h2>
          
          <div className="flex items-center gap-2 text-gray-600">
            <span className="font-medium">{content.uploader_name}</span>
            <span>•</span>
            <div className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              {formatTimeAgo(content.created_at)}
            </div>
          </div>

          {/* Stats */}
          <div className="flex items-center gap-4">
            <button 
              onClick={handleLike}
              disabled={likeLoading}
              className={`flex items-center gap-2 px-4 py-2 border rounded-full transition-colors ${
                userLiked 
                  ? 'bg-red-50 border-red-200 text-red-600' 
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <Heart className={`w-5 h-5 ${userLiked ? 'fill-red-500 text-red-500' : ''}`} />
              <span>{likesCount}</span>
            </button>
            <div className="flex items-center gap-1 text-gray-500">
              <Eye className="w-5 h-5" />
              <span>{viewsCount} views</span>
            </div>
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-2">
            {content.language && (
              <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm">
                {content.language}
              </span>
            )}
            {content.grade && (
              <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm">
                Grade {content.grade}
              </span>
            )}
            {content.subject && (
              <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm">
                {content.subject}
              </span>
            )}
          </div>

          {/* Description */}
          {content.description && (
            <div className="pt-4 border-t">
              <h3 className="font-medium text-gray-900 mb-2">Description</h3>
              <p className="text-gray-600">{content.description}</p>
            </div>
          )}
        </div>
      </main>

      <BottomNav />
    </div>
  );
}
