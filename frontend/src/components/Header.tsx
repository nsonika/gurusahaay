'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { ChevronLeft, Bell } from 'lucide-react';
import Link from 'next/link';
import { getUnreadNotificationCount } from '@/lib/api';

interface HeaderProps {
  title: string;
  showBack?: boolean;
  backHref?: string;
}

export default function Header({ title, showBack = false, backHref = '/' }: HeaderProps) {
  const { user } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (user) {
      fetchUnreadCount();
      // Poll for new notifications every 30 seconds
      const interval = setInterval(fetchUnreadCount, 30000);
      return () => clearInterval(interval);
    }
  }, [user]);

  const fetchUnreadCount = async () => {
    try {
      const data = await getUnreadNotificationCount();
      setUnreadCount(data.unread_count);
    } catch (err) {
      // Silently fail
    }
  };

  return (
    <header className="sticky top-0 bg-white border-b border-gray-200 z-40">
      <div className="flex items-center justify-between h-14 px-4 max-w-lg mx-auto">
        <div className="flex items-center gap-2">
          {showBack && (
            <Link href={backHref} className="p-1 -ml-1 text-gray-600 hover:text-gray-900">
              <ChevronLeft className="w-6 h-6" />
            </Link>
          )}
          <h1 className="text-lg font-semibold text-gray-900">{title}</h1>
        </div>
        
        <div className="flex items-center gap-3">
          {user && (
            <>
              <Link href="/notifications" className="relative p-2 text-gray-600 hover:text-gray-900">
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                  <span className="absolute top-1 right-1 w-4 h-4 bg-orange-500 text-white text-xs rounded-full flex items-center justify-center">
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </span>
                )}
              </Link>
              <div className="text-sm text-gray-500">
                {user.language_preference.toUpperCase()}
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
