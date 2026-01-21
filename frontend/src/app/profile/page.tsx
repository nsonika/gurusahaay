'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { useTranslation } from '@/hooks/useTranslation';
import { getPoints, PointsResponse, updateLanguagePreference } from '@/lib/api';
import { LogOut, ChevronRight, Video, MessageCircle, Upload as UploadIcon, Heart, Award } from 'lucide-react';

export default function ProfilePage() {
  const { user, loading, logout, refreshUser } = useAuth();
  const { t } = useTranslation();
  const router = useRouter();
  const [points, setPoints] = useState<PointsResponse | null>(null);
  const [pointsLoading, setPointsLoading] = useState(true);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (user) {
      getPoints()
        .then(setPoints)
        .catch(console.error)
        .finally(() => setPointsLoading(false));
    }
  }, [user]);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };



  if (loading || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    );
  }

  const totalPoints = points?.total_points || 0;


  // Calculate stats from points history
  const stats = {
    solutionsTried: 0,
    feedbackGiven: 0,
    contentShared: 0,
    teachersHelped: 0
  };

  if (points?.history) {
    points.history.forEach(item => {
      const reason = item.reason.toLowerCase();
      if (reason.includes('view') || reason.includes('solution')) stats.solutionsTried++;
      if (reason.includes('feedback') || reason.includes('rate')) stats.feedbackGiven++;
      if (reason.includes('upload') || reason.includes('share')) stats.contentShared++;
      if (reason.includes('help') || reason.includes('response')) stats.teachersHelped++;
    });
  }

  return (
    <div className="min-h-screen bg-cream pb-20">
      <main className="max-w-lg mx-auto px-4 py-8 space-y-5">
        {/* Profile Card */}
        <div className="bg-white rounded-3xl shadow-sm p-8">
          <div className="flex flex-col items-center text-center">
            {/* Avatar */}
            <div className="w-24 h-24 rounded-full bg-orange-100 flex items-center justify-center mb-4">
              <span className="text-3xl font-bold text-orange-600">
                {getInitials(user.name)}
              </span>
            </div>

            {/* Name & School */}
            <h2 className="text-xl font-semibold text-gray-900 mb-1">{user.name}</h2>
            <p className="text-sm text-gray-500 mb-4">{user.school_name || 'Government School'}</p>

            {/* Points Badge */}
            <div className="inline-flex items-center gap-2 px-5 py-2.5 bg-yellow-50 rounded-full">
              <Award className="w-5 h-5 text-yellow-600" />
              <span className="font-semibold text-gray-900 text-base">
                {totalPoints}
              </span>
              <span className="text-gray-600 text-sm">{t('common.points')}</span>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4">
          {/* Solutions Tried */}
          <div className="bg-white rounded-2xl p-6 text-center shadow-sm">
            <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-3">
              <Video className="w-6 h-6 text-blue-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900 mb-1">{stats.solutionsTried}</p>
            <p className="text-xs text-gray-500">Solutions tried</p>
          </div>

          {/* Feedback Given */}
          <div className="bg-white rounded-2xl p-6 text-center shadow-sm">
            <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-3">
              <MessageCircle className="w-6 h-6 text-green-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900 mb-1">{stats.feedbackGiven}</p>
            <p className="text-xs text-gray-500">Feedback given</p>
          </div>

          {/* Content Shared */}
          <div className="bg-white rounded-2xl p-6 text-center shadow-sm">
            <div className="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center mx-auto mb-3">
              <UploadIcon className="w-6 h-6 text-orange-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900 mb-1">{stats.contentShared}</p>
            <p className="text-xs text-gray-500">Content shared</p>
          </div>

          {/* Teachers Helped */}
          <div className="bg-white rounded-2xl p-6 text-center shadow-sm">
            <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-3">
              <Heart className="w-6 h-6 text-red-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900 mb-1">{stats.teachersHelped}</p>
            <p className="text-xs text-gray-500">Teachers helped</p>
          </div>
        </div>

        {/* Points & Rewards */}
        {/* How to Earn Points */}
        <div className="bg-white rounded-3xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">How to Earn Points</h3>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-600 font-medium">Upload content</span>
              <span className="text-primary-600 font-bold">+10 pts</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600 font-medium">Content gets verified</span>
              <span className="text-primary-600 font-bold">+20 pts</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600 font-medium">Content helps someone</span>
              <span className="text-primary-600 font-bold">+5 pts</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600 font-medium">Give feedback</span>
              <span className="text-primary-600 font-bold">+2 pts</span>
            </div>
          </div>
        </div>

        {/* Settings */}
        <div className="bg-white rounded-3xl shadow-sm overflow-hidden">
          <h3 className="text-lg font-semibold text-gray-900 px-6 pt-6 pb-4">Settings</h3>

          {/* Language Selector */}
          <button
            onClick={() => router.push('/profile/language')}
            className="w-full flex items-center justify-between px-6 py-4 hover:bg-gray-50 transition-colors border-b border-gray-100"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                <svg className="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
                </svg>
              </div>
              <span className="text-gray-900 font-medium">{t('profile.language')}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-gray-500 text-sm">{t(`languages.${user.language_preference}`)}</span>
              <ChevronRight className="w-5 h-5 text-gray-400" />
            </div>
          </button>

          {/* Logout */}
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-6 py-4 text-red-600 hover:bg-red-50 transition-colors"
          >
            <div className="w-10 h-10 rounded-full bg-red-50 flex items-center justify-center">
              <LogOut className="w-5 h-5" />
            </div>
            <span className="font-medium">{t('profile.logout')}</span>
          </button>
        </div>
      </main>
    </div>
  );
}
