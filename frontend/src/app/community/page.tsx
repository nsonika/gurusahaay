'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { getCommunityFeed, Content } from '@/lib/api';
import { RefreshCw, Loader2, MessageCircle, Clock, ArrowRight, HelpCircle } from 'lucide-react';

type FeedTab = 'all' | 'help_needed' | 'uploads';

export default function CommunityPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<FeedTab>('all');
  const [feed, setFeed] = useState<Content[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchFeed = async (showRefresh = false) => {
    if (showRefresh) setRefreshing(true);
    else setLoading(true);
    
    try {
      const data = await getCommunityFeed(activeTab, 20);
      setFeed(data);
    } catch (err) {
      console.error('Failed to fetch feed:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchFeed();
  }, [activeTab]);

  const tabs = [
    { id: 'all' as const, label: 'All' },
    { id: 'help_needed' as const, label: 'Help Needed' },
    { id: 'uploads' as const, label: 'Uploads' },
  ];

  // Format relative time
  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffHours < 1) return 'just now';
    if (diffHours < 24) return `about ${diffHours} hours ago`;
    if (diffDays === 1) return 'yesterday';
    return `${diffDays} days ago`;
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-lg mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold text-gray-900">Community Feed</h1>
            <button
              onClick={() => fetchFeed(true)}
              disabled={refreshing}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
            >
              <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
              <span className="text-sm font-medium">Refresh</span>
            </button>
          </div>
          
          {/* Tabs */}
          <div className="flex gap-2 mt-4">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 py-2 px-4 rounded-full text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-gray-900 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Feed Content */}
      <main className="max-w-lg mx-auto px-4 py-6">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
          </div>
        ) : feed.length > 0 ? (
          <div className="space-y-4">
            {feed.map((item) => (
              <FeedCard 
                key={item.id} 
                item={item} 
                formatTimeAgo={formatTimeAgo}
                onHelpOut={() => router.push(item.source_type === "help_request" ? `/help-request/${item.id}` : `/suggestions?concept_id=${item.concept_id}`)}
              />
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-2xl p-8 text-center border">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <MessageCircle className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="font-medium text-gray-900 mb-2">No posts yet</h3>
            <p className="text-sm text-gray-500">
              Be the first to share or ask for help!
            </p>
          </div>
        )}
      </main>
    </div>
  );
}

// Feed Card Component matching the reference design
function FeedCard({ 
  item, 
  formatTimeAgo,
  onHelpOut 
}: { 
  item: Content; 
  formatTimeAgo: (date: string) => string;
  onHelpOut: () => void;
}) {
  const isHelpRequest = item.content_type === 'help_request' || item.source_type === 'help_request';
  const conceptLabel = item.concept_id?.replace(/_/g, ' ').toLowerCase() || 'Other';
  
  return (
    <div className="bg-white rounded-2xl border p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center">
            <HelpCircle className="w-5 h-5 text-orange-500" />
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
        &quot;{item.title || conceptLabel}&quot;
      </h3>
      
      {/* Footer */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1 text-gray-500 text-sm">
          <MessageCircle className="w-4 h-4" />
          0 responses
        </div>
        
        {isHelpRequest && (
          <button
            onClick={onHelpOut}
            className="flex items-center gap-1 text-orange-600 font-medium text-sm hover:text-orange-700"
          >
            Help out
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}
