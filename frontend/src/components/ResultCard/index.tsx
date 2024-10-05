import React, { useEffect, useCallback } from 'react';
import { debounce } from 'lodash';
import { useTranslation } from 'react-i18next';

declare global {
  interface Window {
    talkify: any;
  }
}

interface ResultCardProps {
  videoSrc: string;
  videoName: string;
  onTranslate: () => void;
  loading: boolean;
  translation: string;
  originalText: string;
}

const ResultCard: React.FC<ResultCardProps> = ({ videoName, loading, translation, originalText }) => {
  const { t } = useTranslation();

  useEffect(() => {
    // Initialize Talkify
    if (window.talkify) {
      window.talkify.config.remoteService.host = 'https://talkify.net';
      window.talkify.config.remoteService.apiKey = 'c889183e-dbeb-4012-9d6e-13a12eb291ae';
      window.talkify.config.ui.audioControls.enabled = true;
      window.talkify.config.ui.audioControls.voicepicker.enabled = true;

      window.talkify.selectionActivator
        .withTextHighlighting()
        .activate();
    }
  }, []);

  const handleTextToSpeech = useCallback(
    debounce((sentence: string) => {
      if (window.talkify) {
        const player = new window.talkify.TtsPlayer();
        player.playText(sentence);
      }
    }, 300),
    []
  );

  return (
    <div className="mt-4">
      <div className="mt-2 text-center">
        <p className="text-lg font-semibold">{videoName}</p>
      </div>
      {loading && (
        <div className="mt-2 text-center text-blue-500">{t('loading')}</div>
      )}
      {translation && (
        <div className="p-6 mt-6 bg-gray-100 rounded-lg shadow-md dark:bg-gray-800">
          <div>
            <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">{t('germanText')}:</h3>
            <p className="mt-1 text-gray-600 dark:text-gray-400">
              {originalText}
              <span onClick={() => handleTextToSpeech(originalText)} className="ml-2 cursor-pointer">
                <i className="fas fa-volume-up"></i>
              </span>
            </p>
          </div>
          <div className="mt-4">
            <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">{t('englishText')}:</h3>
            <p className="mt-1 text-gray-600 dark:text-gray-400">
              {translation}
              <span onClick={() => handleTextToSpeech(translation)} className="ml-2 cursor-pointer">
                <i className="fas fa-volume-up"></i>
              </span>
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultCard;
