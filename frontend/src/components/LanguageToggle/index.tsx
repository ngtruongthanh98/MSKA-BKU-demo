import React from 'react';
import { useTranslation } from 'react-i18next';

const LanguageToggle: React.FC = () => {
  const { i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className="flex gap-2">
      <button
        onClick={() => changeLanguage('en')}
        className={`px-2 py-1 ${i18n.language === 'en' ? 'font-bold' : ''}`}
      >
        EN
      </button>
      <button
        onClick={() => changeLanguage('vi')}
        className={`px-2 py-1 ${i18n.language === 'vi' ? 'font-bold' : ''}`}
      >
        VI
      </button>
    </div>
  );
};

export default LanguageToggle;
