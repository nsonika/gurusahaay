'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { useAuth } from '@/context/AuthContext';
import { useTranslation } from '@/hooks/useTranslation';
import { updateLanguagePreference } from '@/lib/api';
import { Check } from 'lucide-react';

export default function LanguageSelectionPage() {
    const { user, refreshUser } = useAuth();
    const { t } = useTranslation();
    const router = useRouter();
    const [selectedLang, setSelectedLang] = useState(user?.language_preference || 'en');
    const [saving, setSaving] = useState(false);

    const languages = [
        { code: 'en', label: 'English', native: 'English' },
        { code: 'hi', label: 'Hindi', native: 'हिंदी' },
        { code: 'kn', label: 'Kannada', native: 'ಕನ್ನಡ' },
    ];

    const handleContinue = async () => {
        if (selectedLang === user?.language_preference) {
            router.push('/profile');
            return;
        }

        setSaving(true);
        try {
            await updateLanguagePreference(selectedLang);
            await refreshUser();
            // Hard navigate to profile to apply new translations
            window.location.href = '/profile';
        } catch (error) {
            console.error('Failed to update language:', error);
            setSaving(false);
        }
    };

    return (
        <div className="min-h-screen bg-cream flex flex-col items-center justify-center p-6">
            <div className="w-full max-w-md">
                {/* Logo & Header */}
                <div className="text-center mb-10">
                    {/* Logo */}
                    <div className="w-24 h-24 rounded-[28px] bg-orange-500 flex items-center justify-center mx-auto mb-6 shadow-md">
                        <span className="text-5xl font-bold text-white">गु</span>
                    </div>

                    <h1 className="text-3xl font-bold text-gray-900 mb-2">GuruSahaay</h1>
                    <p className="text-gray-500 text-base">{t('auth.preferredLanguage') || 'Your classroom companion'}</p>

                    <p className="text-gray-600 text-sm mt-10 mb-6">
                        {t('profile.selectLanguage') || 'Select your language'}
                    </p>
                </div>

                {/* Language Options */}
                <div className="space-y-3 mb-12">
                    {languages.map((lang) => (
                        <button
                            key={lang.code}
                            onClick={() => setSelectedLang(lang.code)}
                            className={`w-full flex items-center justify-between p-5 rounded-2xl border-2 transition-all ${selectedLang === lang.code
                                ? 'border-orange-500 bg-white'
                                : 'border-gray-200 bg-white hover:border-gray-300'
                                }`}
                        >
                            <div className="text-left">
                                <p className="font-semibold text-gray-900 text-xl mb-0.5">{lang.native}</p>
                                <p className="text-sm text-gray-500">{lang.label}</p>
                            </div>
                            {selectedLang === lang.code && (
                                <div className="w-7 h-7 rounded-full bg-orange-500 flex items-center justify-center flex-shrink-0">
                                    <Check className="w-4 h-4 text-white" strokeWidth={3} />
                                </div>
                            )}
                        </button>
                    ))}
                </div>

                {/* Continue Button */}
                <button
                    onClick={handleContinue}
                    disabled={saving}
                    className="w-full py-4 bg-orange-500 text-white font-semibold text-lg rounded-2xl hover:bg-orange-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
                >
                    {saving ? t('common.loading') : (t('common.save') || 'Continue')}
                </button>
            </div>
        </div>
    );
}
