import React, { useState } from 'react';

import { translateImage } from '@/utils/api.ts';

interface VideoCardProps {
  videoSrc: string;
  videoName: string;
  onDelete: () => void;
}

const VideoCard: React.FC<VideoCardProps> = ({ videoSrc, videoName, onDelete }) => {
  const [originalText, setOriginalText] = useState<string>('');
  const [translation, setTranslation] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const handleTranslate = async () => {
    setLoading(true);
    const recognizedText = await recognizeSignLanguage(videoName);
    const translatedText = await translateToSpokenLanguage(recognizedText);
    setTranslation(translatedText);
    setLoading(false);
  };

  const recognizeSignLanguage = async (imageName: string): Promise<string> => {
    try {
      const response = await translateImage(imageName);
      setOriginalText(response);
      return response;
    } catch (error) {
      console.error('Error recognizing sign language:', error);
      throw error;
    }
  };

  const translateToSpokenLanguage = async (text: string): Promise<string> => {
    // Mock data for translation
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve('Hola, ¿cómo estás?');
      }, 2000);
    });
  };

  return (
    <div className="mt-4">
      <div className="flex justify-center">
        <video
          src={videoSrc}
          controls
          className="max-w-full"
        />
      </div>
      <div className="mt-2 text-center">
        <p className="text-lg font-semibold">{videoName}</p>
      </div>
      <div className="flex justify-center mt-2">
        <button
          onClick={onDelete}
          className="px-4 py-2 text-white bg-red-500 rounded"
        >
          Delete Video
        </button>
        <button
          onClick={handleTranslate}
          className="px-4 py-2 ml-2 text-white bg-blue-500 rounded"
          disabled={loading}
        >
          {loading ? 'Translating...' : 'Translate Video'}
        </button>
      </div>
      {loading && (
        <div className="mt-2 text-center text-blue-500">Loading...</div>
      )}
      {translation && (
        <div className="p-6 mt-6 bg-white rounded-lg shadow-md dark:bg-gray-800">
          <div>
            <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">German Text:</h3>
            <p className="mt-1 text-gray-600 dark:text-gray-400">{originalText}</p>
          </div>
          <div className="mt-4">
            <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">English Text:</h3>
            <p className="mt-1 text-gray-600 dark:text-gray-400">{translation}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoCard;
