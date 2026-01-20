'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import Header from '@/components/Header';
import { getCommunityFeed, getPoints, Content, PointsResponse } from '@/lib/api';
import { Upload, Award, TrendingUp, HelpCircle, Clock, MessageCircle, ArrowRight, RefreshCw } from 'lucide-react';
import BottomNav from '@/components/BottomNav';

type FeedTab = 'all' | 'help_needed';

export default function HomePage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [feed, setFeed] = useState<Content[]>([]);
  const [points, setPoints] = useState<PointsResponse | null>(null);
  const [feedLoading, setFeedLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<FeedTab>('all');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (user) {
      getPoints().then(setPoints).catch(console.error);
    }
  }, [user]);

  useEffect(() => {
    if (user) {
      fetchFeed();
    }
  }, [user, activeTab]);

  const fetchFeed = async (showRefresh = false) => {
    if (showRefresh) setRefreshing(true);
    else setFeedLoading(true);
    
    try {
      const data = await getCommunityFeed(activeTab, 10);
      setFeed(data);
    } catch (err) {
      console.error('Failed to fetch feed:', err);
    } finally {
      setFeedLoading(false);
      setRefreshing(false);
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
    if (diffDays === 1) return 'yesterday';
    return `${diffDays} days ago`;
  };

  if (loading || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <Header title="GuruSahaay" />
      
      <main className="max-w-lg mx-auto px-4 py-6 space-y-6">
        {/* Welcome */}
        <div className="card bg-gradient-to-r from-primary-600 to-primary-700 text-white">
          <h2 className="text-lg font-semibold">Welcome, {user.name}!</h2>
          <p className="text-primary-100 text-sm mt-1">
            How can we help you today?
          </p>
          <Link
            href="/help"
            className="inline-flex items-center gap-2 mt-4 px-4 py-2 bg-white text-primary-600 rounded-lg font-medium hover:bg-primary-50 transition-colors"
          >
            <HelpCircle className="w-5 h-5" />
            Get Help Now
          </Link>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-4">
          <Link href="/upload" className="card hover:shadow-md transition-shadow">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                <Upload className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Upload</h3>
                <p className="text-xs text-gray-500">Share content</p>
              </div>
            </div>
          </Link>
          
          <Link href="/profile" className="card hover:shadow-md transition-shadow">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-yellow-100 flex items-center justify-center">
                <Award className="w-5 h-5 text-yellow-600" />
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Points</h3>
                <p className="text-xs text-gray-500">
                  {points ? `${points.total_points} pts` : 'Loading...'}
                </p>
              </div>
            </div>
          </Link>
        </div>

        {/* Community Feed with Tabs */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-primary-600" />
              Community Feed
            </h2>
            <button
              onClick={() => fetchFeed(true)}
              disabled={refreshing}
              className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-4">
            <button
              onClick={() => setActiveTab('all')}
              className={`flex-1 py-2 px-4 rounded-full text-sm font-medium transition-colors ${
                activeTab === 'all'
                  ? 'bg-gray-900 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setActiveTab('help_needed')}
              className={`flex-1 py-2 px-4 rounded-full text-sm font-medium transition-colors ${
                activeTab === 'help_needed'
                  ? 'bg-gray-900 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Help Needed
            </button>
          </div>
          
          {feedLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="card animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
                  <div className="h-3 bg-gray-200 rounded w-1/2" />
                </div>
              ))}
            </div>
          ) : feed.length > 0 ? (
            <div className="space-y-3">
              {feed.map((item) => {
                const isHelpRequest = item.content_type === 'help_request' || item.source_type === 'help_request';
                return (
                  <div key={item.id} className="bg-white rounded-2xl border p-4">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                          isHelpRequest ? 'bg-orange-100' : 'bg-green-100'
                        }`}>
                          <HelpCircle className={`w-5 h-5 ${isHelpRequest ? 'text-orange-500' : 'text-green-500'}`} />
                        </div>
                        <span className="font-medium text-gray-900">
                          {item.uploader_name || 'Teacher'}
                        </span>
                      </div>
                      <div className="flex items-center gap-1 text-gray-400 text-sm">
                        <Clock className="w-4 h-4" />
                        {formatTimeAgo(item.created_at)}
                      </div>
                    </div>
                    
                    {/* Category Tag */}
                    <div className="mb-2">
                      <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                        isHelpRequest 
                          ? 'bg-amber-100 text-amber-700' 
                          : 'bg-green-100 text-green-700'
                      }`}>
                        {isHelpRequest ? 'Help Needed' : 'Upload'}
                      </span>
                    </div>
                    
                    {/* Content */}
                    <h3 className="text-lg font-medium text-gray-900 mb-3">
                      &quot;{item.title}&quot;
                    </h3>
                    
                    {/* Footer */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1 text-gray-500 text-sm">
                        <MessageCircle className="w-4 h-4" />
                        0 responses
                      </div>
                      
                      {isHelpRequest ? (
                        <button
                          onClick={() => router.push(`/help-request/${item.id}`)}
                          className="flex items-center gap-1 text-orange-600 font-medium text-sm hover:text-orange-700"
                        >
                          Help out
                          <ArrowRight className="w-4 h-4" />
                        </button>
                      ) : (
                        <button
                          onClick={() => router.push(`/content/${item.id}`)}
                          className="flex items-center gap-1 text-green-600 font-medium text-sm hover:text-green-700"
                        >
                          View Content
                          <ArrowRight className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="card text-center py-8">
              <p className="text-gray-500">
                {activeTab === 'help_needed' 
                  ? 'No help requests yet.' 
                  : 'No content yet. Be the first to upload!'}
              </p>
              <Link href={activeTab === 'help_needed' ? '/help' : '/upload'} className="btn-primary inline-block mt-4">
                {activeTab === 'help_needed' ? 'Ask for Help' : 'Upload Content'}
              </Link>
            </div>
          )}
        </section>
      </main>

      <BottomNav />
    </div>
  );
}
