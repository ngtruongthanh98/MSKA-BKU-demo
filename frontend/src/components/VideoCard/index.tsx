import React, { useState } from 'react';

interface VideoCardProps {
  videoSrc: string;
  videoName: string;
  onDelete: () => void;
}

const VideoCard: React.FC<VideoCardProps> = ({ videoSrc, videoName, onDelete }) => {
  const [translation, setTranslation] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const handleTranslate = async () => {
    setLoading(true);
    const recognizedText = await recognizeSignLanguage(videoName);
    const translatedText = await translateToSpokenLanguage(recognizedText);
    setTranslation(translatedText);
    setLoading(false);
  };

  const recognizeSignLanguage = async (text: string): Promise<string> => {
    // Mock data for sign language recognition
    return new Promise((resolve) => {
      setTimeout(() => {
        console.log('Recognizing sign language: ', text);

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
        <div className="p-4 mt-4 bg-gray-100 rounded dark:bg-gray-800">
          <h2 className="text-xl font-bold">Translation:</h2>
          <p>{translation}</p>
        </div>
      )}
    </div>
  );
};

export default VideoCard;
