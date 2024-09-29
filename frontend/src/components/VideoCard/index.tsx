import React, { useState } from 'react';

interface VideoCardProps {
  videoSrc: string;
  onDelete: () => void;
}

const VideoCard: React.FC<VideoCardProps> = ({ videoSrc, onDelete }) => {
  const [translation, setTranslation] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const handleTranslate = async () => {
    setLoading(true);
    const recognizedText = await recognizeSignLanguage();
    const translatedText = await translateToSpokenLanguage(recognizedText);
    setTranslation(translatedText);
    setLoading(false);
  };

  const recognizeSignLanguage = async (): Promise<string> => {
    // Mock data for sign language recognition
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve('Hello, how are you?');
      }, 2000);
    });
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
      <video
        src={videoSrc}
        controls
        className="max-w-full"
      />
      <button
        onClick={onDelete}
        className="px-4 py-2 mt-2 text-white bg-red-500 rounded"
      >
        Delete Video
      </button>
      <button
        onClick={handleTranslate}
        className="px-4 py-2 mt-2 ml-2 text-white bg-blue-500 rounded"
        disabled={loading}
      >
        {loading ? 'Translating...' : 'Translate Video'}
      </button>
      {loading && (
        <div className="mt-2 text-blue-500">Loading...</div>
      )}
      {translation && (
        <div className="p-4 mt-4 bg-gray-100 rounded">
          <h2 className="text-xl font-bold">Translation:</h2>
          <p>{translation}</p>
        </div>
      )}
    </div>
  );
};

export default VideoCard;
