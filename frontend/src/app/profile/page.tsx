'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import Header from '@/components/Header';
import { getPoints, PointsResponse } from '@/lib/api';
import { Award, LogOut, User, Phone, MapPin, School, Globe } from 'lucide-react';

export default function ProfilePage() {
  const { user, loading, logout } = useAuth();
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

  const languageLabels: Record<string, string> = {
    en: 'English',
    kn: 'ಕನ್ನಡ (Kannada)',
    hi: 'हिंदी (Hindi)',
  };

  const reasonLabels: Record<string, string> = {
    upload: 'Uploaded content',
    verification: 'Content verified',
    helped: 'Content helped someone',
    feedback: 'Gave feedback',
  };

  if (loading || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header title="Profile" />
      
      <main className="max-w-lg mx-auto px-4 py-6 space-y-6">
        {/* Profile Card */}
        <div className="card">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
              <User className="w-8 h-8 text-primary-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">{user.name}</h2>
              <p className="text-sm text-gray-500 capitalize">{user.role}</p>
            </div>
          </div>
          
          <div className="space-y-3 text-sm">
            <div className="flex items-center gap-3 text-gray-600">
              <Phone className="w-4 h-4" />
              <span>{user.phone}</span>
            </div>
            {user.school_name && (
              <div className="flex items-center gap-3 text-gray-600">
                <School className="w-4 h-4" />
                <span>{user.school_name}</span>
              </div>
            )}
            {(user.district || user.state) && (
              <div className="flex items-center gap-3 text-gray-600">
                <MapPin className="w-4 h-4" />
                <span>{[user.district, user.state].filter(Boolean).join(', ')}</span>
              </div>
            )}
            <div className="flex items-center gap-3 text-gray-600">
              <Globe className="w-4 h-4" />
              <span>{languageLabels[user.language_preference] || user.language_preference}</span>
            </div>
          </div>
        </div>

        {/* Points Card */}
        <div className="card bg-gradient-to-r from-yellow-50 to-orange-50 border-yellow-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
                <Award className="w-6 h-6 text-yellow-600" />
              </div>
              <div>
                <p className="text-sm text-yellow-700">Total Points</p>
                <p className="text-2xl font-bold text-yellow-800">
                  {pointsLoading ? '...' : points?.total_points || 0}
                </p>
              </div>
            </div>
          </div>
          
          {/* Points History */}
          {points && points.history.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Recent Activity</h3>
              <div className="space-y-2">
                {points.history.slice(0, 5).map((item) => (
                  <div key={item.id} className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">
                      {reasonLabels[item.reason || ''] || item.reason}
                    </span>
                    <span className="font-medium text-green-600">+{item.points}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Rewards Info */}
        <div className="card">
          <h3 className="font-medium text-gray-900 mb-3">How to Earn Points</h3>
          <div className="space-y-2 text-sm text-gray-600">
            <div className="flex justify-between">
              <span>Upload content</span>
              <span className="font-medium text-primary-600">+10 pts</span>
            </div>
            <div className="flex justify-between">
              <span>Content gets verified</span>
              <span className="font-medium text-primary-600">+20 pts</span>
            </div>
            <div className="flex justify-between">
              <span>Content helps someone</span>
              <span className="font-medium text-primary-600">+5 pts</span>
            </div>
            <div className="flex justify-between">
              <span>Give feedback</span>
              <span className="font-medium text-primary-600">+2 pts</span>
            </div>
          </div>
        </div>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-center gap-2 py-3 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        >
          <LogOut className="w-5 h-5" />
          Sign Out
        </button>
      </main>
    </div>
  );
}
