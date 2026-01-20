'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, HelpCircle, Upload, User } from 'lucide-react';
import { clsx } from 'clsx';

const navItems = [
  { href: '/', icon: Home, label: 'Home' },
  { href: '/help', icon: HelpCircle, label: 'Help' },
  { href: '/upload', icon: Upload, label: 'Upload' },
  { href: '/profile', icon: User, label: 'Profile' },
];

export default function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50">
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
              <span className="text-xs mt-1 font-medium">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
