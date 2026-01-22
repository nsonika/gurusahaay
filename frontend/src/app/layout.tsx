import type { Metadata } from 'next'
import './globals.css'
import { AuthProvider } from '@/context/AuthContext'
import { LanguageProvider } from '@/context/LanguageContext'
import BottomNav from '@/components/BottomNav'

export const metadata: Metadata = {
  title: 'GuruSahaay - Teacher Support',
  description: 'Just-in-time classroom support for teachers',
  viewport: 'width=device-width, initial-scale=1, maximum-scale=1',
  manifest: '/manifest.json',
  themeColor: '#ea580c',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'GuruSahaay',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-cream  pb-20">
        <AuthProvider>
          <LanguageProvider>
            {children}
            <BottomNav />
          </LanguageProvider>
        </AuthProvider>
      </body>
    </html>
  )
}
