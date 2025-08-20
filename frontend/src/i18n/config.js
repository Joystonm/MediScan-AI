import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

// Import translation files
import enTranslations from './locales/en.json';
import esTranslations from './locales/es.json';
import frTranslations from './locales/fr.json';
import deTranslations from './locales/de.json';
import itTranslations from './locales/it.json';
import ptTranslations from './locales/pt.json';

// Translation resources
const resources = {
  en: {
    translation: enTranslations
  },
  es: {
    translation: esTranslations
  },
  fr: {
    translation: frTranslations
  },
  de: {
    translation: deTranslations
  },
  it: {
    translation: itTranslations
  },
  pt: {
    translation: ptTranslations
  }
};

// Language detector options
const detectionOptions = {
  order: ['localStorage', 'navigator', 'htmlTag'],
  lookupLocalStorage: 'medai_language',
  caches: ['localStorage'],
  excludeCacheFor: ['cimode']
};

i18n
  // Load translation using http backend
  .use(Backend)
  // Detect user language
  .use(LanguageDetector)
  // Pass the i18n instance to react-i18next
  .use(initReactI18next)
  // Initialize i18next
  .init({
    resources,
    
    // Language detection
    detection: detectionOptions,
    
    // Fallback language
    fallbackLng: 'en',
    
    // Debug mode (disable in production)
    debug: process.env.NODE_ENV === 'development',
    
    // Interpolation options
    interpolation: {
      escapeValue: false, // React already does escaping
      formatSeparator: ',',
      format: function(value, format, lng) {
        if (format === 'uppercase') return value.toUpperCase();
        if (format === 'lowercase') return value.toLowerCase();
        if (format === 'capitalize') return value.charAt(0).toUpperCase() + value.slice(1);
        return value;
      }
    },
    
    // React options
    react: {
      useSuspense: false,
      bindI18n: 'languageChanged',
      bindI18nStore: '',
      transEmptyNodeValue: '',
      transSupportBasicHtmlNodes: true,
      transKeepBasicHtmlNodesFor: ['br', 'strong', 'i', 'em', 'span']
    },
    
    // Backend options (if using http backend)
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
      addPath: '/locales/add/{{lng}}/{{ns}}',
      allowMultiLoading: false,
      crossDomain: false,
      withCredentials: false,
      overrideMimeType: false,
      requestOptions: {
        mode: 'cors',
        credentials: 'same-origin',
        cache: 'default'
      }
    },
    
    // Namespace options
    ns: ['translation'],
    defaultNS: 'translation',
    
    // Key separator
    keySeparator: '.',
    nsSeparator: ':',
    
    // Pluralization
    pluralSeparator: '_',
    contextSeparator: '_',
    
    // Missing key handling
    saveMissing: process.env.NODE_ENV === 'development',
    missingKeyHandler: function(lng, ns, key, fallbackValue) {
      if (process.env.NODE_ENV === 'development') {
        console.warn(`Missing translation key: ${key} for language: ${lng}`);
      }
    },
    
    // Post processing
    postProcess: ['interval', 'plural'],
    
    // Clean code on production
    cleanCode: true,
    
    // Load languages
    preload: ['en', 'es', 'fr', 'de', 'it', 'pt'],
    
    // Whitelist languages
    supportedLngs: ['en', 'es', 'fr', 'de', 'it', 'pt', 'zh', 'ja', 'ko', 'ar'],
    nonExplicitSupportedLngs: false,
    
    // Load options
    load: 'languageOnly',
    
    // Update missing
    updateMissing: process.env.NODE_ENV === 'development',
    
    // Return objects
    returnObjects: false,
    returnEmptyString: true,
    returnNull: true,
    
    // Join arrays
    joinArrays: false,
    
    // Override options
    overloadTranslationOptionHandler: function(args) {
      return {
        defaultValue: args[1]
      };
    }
  });

// Add custom formatters
i18n.services.formatter.add('medical', (value, lng, options) => {
  // Custom formatter for medical terms
  if (typeof value === 'string') {
    // Apply medical terminology formatting
    return value.charAt(0).toUpperCase() + value.slice(1);
  }
  return value;
});

i18n.services.formatter.add('urgency', (value, lng, options) => {
  // Custom formatter for urgency levels
  const urgencyColors = {
    emergency: '#ef4444',
    urgent: '#f59e0b',
    routine: '#10b981'
  };
  
  if (options.color && urgencyColors[value]) {
    return `<span style="color: ${urgencyColors[value]}">${value}</span>`;
  }
  
  return value;
});

// Export configured i18n instance
export default i18n;
