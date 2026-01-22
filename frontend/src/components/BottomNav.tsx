'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, HelpCircle, Upload, User } from 'lucide-react';
import { clsx } from 'clsx';
import { useTranslation } from '@/hooks/useTranslation';

export default function BottomNav() {
  const pathname = usePathname();
  const { t } = useTranslation();

  // Hide bottom nav on specific pages
  if (pathname?.startsWith('/login') ||
    pathname?.startsWith('/register') ||
    pathname?.startsWith('/profile/language')) {
    return null;
  }

  const navItems = [
    { href: '/', icon: Home, labelKey: 'common.home' },
    { href: '/help', icon: HelpCircle, labelKey: 'common.help' },
    { href: '/upload', icon: Upload, labelKey: 'common.upload' },
    { href: '/profile', icon: User, labelKey: 'common.profile' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-cream border-t border-gray-200 z-50">
      <div className="flex justify-around items-center h-16 max-w-lg mx-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                'flex flex-col items-center justify-center w-full h-full',
                'transition-colors duration-200',
                isActive ? 'text-primary-600' : 'text-gray-500 hover:text-gray-700'
              )}
            >
              <Icon className="w-6 h-6" />
              <span className="text-xs mt-1 font-medium">{t(item.labelKey)}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

