import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import translations, { type Lang, type TKey } from '../i18n/translations';

const LANG_KEY = 'educrm_lang';

interface LanguageContextValue {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: (key: TKey) => string;
}

const LanguageContext = createContext<LanguageContextValue | null>(null);

function loadLang(): Lang {
  try {
    const v = localStorage.getItem(LANG_KEY);
    if (v === 'uz' || v === 'ru' || v === 'en') return v;
  } catch { /* ignore */ }
  return 'uz';
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(loadLang);

  const setLang = useCallback((l: Lang) => {
    setLangState(l);
    try { localStorage.setItem(LANG_KEY, l); } catch { /* ignore */ }
  }, []);

  const t = useCallback((key: TKey): string => {
    return (translations[lang] as Record<string, string>)[key]
      ?? (translations.uz as Record<string, string>)[key]
      ?? key;
  }, [lang]);

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error('useLanguage must be used inside <LanguageProvider>');
  return ctx;
}
