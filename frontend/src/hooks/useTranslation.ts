import { useLanguage } from '@/context/LanguageContext';

/**
 * Custom hook to access translation function
 * 
 * @example
 * const { t } = useTranslation();
 * return <h1>{t('home.welcomeMessage', { name: user.name })}</h1>;
 */
export function useTranslation() {
    return useLanguage();
}
