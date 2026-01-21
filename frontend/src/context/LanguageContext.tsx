'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useAuth } from './AuthContext';

// Translation type
type Translations = {
    [key: string]: any;
};

interface LanguageContextType {
    language: string;
    t: (key: string, params?: Record<string, any>) => string;
    changeLanguage: (lang: string) => void;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// Supported languages
export const SUPPORTED_LANGUAGES = ['en', 'kn', 'hi', 'ta', 'te'] as const;
export type SupportedLanguage = typeof SUPPORTED_LANGUAGES[number];

export function LanguageProvider({ children }: { children: ReactNode }) {
    const { user } = useAuth();
    const [language, setLanguage] = useState<string>('en');
    const [translations, setTranslations] = useState<Translations>({});

    // Load translations for a given language
    const loadTranslations = async (lang: string) => {
        try {
            const module = await import(`@/translations/${lang}.json`);
            setTranslations(module.default || module);
        } catch (error) {
            console.error(`Failed to load translations for ${lang}:`, error);
            // Fallback to English
            if (lang !== 'en') {
                const module = await import('@/translations/en.json');
                setTranslations(module.default || module);
            }
        }
    };

    // Update language when user preference changes
    useEffect(() => {
        const newLang = user?.language_preference || 'en';
        if (SUPPORTED_LANGUAGES.includes(newLang as SupportedLanguage)) {
            setLanguage(newLang);
            loadTranslations(newLang);
        } else {
            setLanguage('en');
            loadTranslations('en');
        }
    }, [user?.language_preference]);

    // Translation function with nested key support and parameter substitution
    const t = (key: string, params?: Record<string, any>): string => {
        const keys = key.split('.');
        let value: any = translations;

        // Navigate through nested keys
        for (const k of keys) {
            if (value && typeof value === 'object') {
                value = value[k];
            } else {
                value = undefined;
                break;
            }
        }

        // If translation not found, return the key itself
        if (typeof value !== 'string') {
            console.warn(`Translation not found for key: ${key}`);
            return key;
        }

        // Replace parameters in the translation
        if (params) {
            return value.replace(/\{\{(\w+)\}\}/g, (match: string, paramKey: string) => {
                return params[paramKey]?.toString() || match;
            });
        }

        return value;
    };

    const changeLanguage = (lang: string) => {
        if (SUPPORTED_LANGUAGES.includes(lang as SupportedLanguage)) {
            setLanguage(lang);
            loadTranslations(lang);
        }
    };

    return (
        <LanguageContext.Provider value={{ language, t, changeLanguage }}>
            {children}
        </LanguageContext.Provider>
    );
}

export function useLanguage() {
    const context = useContext(LanguageContext);
    if (context === undefined) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
}
