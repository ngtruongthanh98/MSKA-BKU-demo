import React, { useState } from 'react';

import { translateImage, googleTranslate, getVideo } from '@/utils/api.ts';

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
    try {
      const recognizedText = await recognizeSignLanguage(videoName);
      const translatedText = await translateToSpokenLanguage(recognizedText);
      setTranslation(translatedText);
    } catch (error) {
      console.error('Error during translation process:', error);
    } finally {
      setLoading(false);
    }
  };

  const recognizeSignLanguage = async (imageName: string): Promise<string> => {
    try {
      let response = await translateImage(imageName);

      const capitalized =
      response.charAt(0).toUpperCase()
    + response.slice(1)

      setOriginalText(capitalized);
      return response;
    } catch (error) {
      console.error('Error recognizing sign language:', error);
      throw error;
    }
  };

  const translateToSpokenLanguage = async (text: string): Promise<string> => {
    try {
      const translatedText = await googleTranslate(text, 'en');
      return translatedText;
    } catch (error) {
      console.error('Error translating text:', error);
      throw error;
    }
  };

  const doGetVideo = async (videoName: string): Promise<string> => {
    try {
      const videoUrl = await getVideo(videoName);
      return videoUrl;
    } catch (error) {
      console.error('Error getting video:', error);
      throw error;
    }
  }

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
        <div className="p-6 mt-6 bg-gray-100 rounded-lg shadow-md dark:bg-gray-800">
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
