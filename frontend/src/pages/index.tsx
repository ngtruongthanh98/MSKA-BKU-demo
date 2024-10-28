import React, { useState } from 'react';
import DefaultLayout from '@/layouts/default';
import ResultCard from '@/components/ResultCard';
import { useTranslation } from 'react-i18next';
import { FileUpload } from '@/components/FileUpload';
import { videoToText, googleTranslate } from '@/utils/api.ts';

const IndexPage: React.FC = () => {
  const [videoSrc, setVideoSrc] = useState<string | null>(null);
  const [videoName, setVideoName] = useState<string | null>(null);
  const [originalText, setOriginalText] = useState<string>('');
  const [translation, setTranslation] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [fileUploadKey, setFileUploadKey] = useState<number>(0);

  const [file, setFile] = useState<File | null>(null);

  const { t } = useTranslation();

  const handleVideoUpload = (file: File) => {
    const videoURL = URL.createObjectURL(file);
    setVideoSrc(videoURL);
    setVideoName(file.name.replace('.mp4', ''));
    setFile(file);
  };

  const handleTranslate = async () => {
    setLoading(true);
    try {
      const recognizedText = await recognizeSignLanguage(file!);
      const translatedText = await translateToSpokenLanguage(recognizedText);

      setTranslation(translatedText);
    } catch (error) {
      console.error('Error during translation process:', error);
    } finally {
      setLoading(false);
    }
  };

  const recognizeSignLanguage = async (file: File): Promise<string> => {
    try {
      let response = await videoToText(file!)
      response = response.trim().replace(/\s+\.$/, '.');

      const capitalized =
        response.charAt(0).toUpperCase() + response.slice(1);

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

  const handleReset = () => {
    setVideoSrc(null);
    setVideoName(null);
    setOriginalText('');
    setTranslation('');
    setFileUploadKey(prevKey => prevKey + 1); // Change the key to force re-render
  };

  return (
    <DefaultLayout>
      <section className="flex flex-col items-center justify-center gap-4">
        <div className="justify-center inline-block max-w-lg text-center">
          <h1 className="mb-8 text-4xl font-bold">{t('homepage.title')}</h1>
          <FileUpload key={fileUploadKey} onFileUpload={handleVideoUpload} />
          {videoSrc && videoName && (
            <>
              <div className="mt-2 text-center">
                <p className="text-lg font-semibold">{videoName}</p>
              </div>

              <div className="flex flex-row items-center justify-center mt-4 space-x-4">

                <div className="flex space-x-4 button-container">
                  <button
                    onClick={handleReset}
                    className="px-6 py-3 text-white transition duration-300 ease-in-out transform bg-red-600 rounded-lg shadow-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-400 focus:ring-opacity-75 hover:scale-105"
                  >
                    {t('button.delete')}
                  </button>

                  <button
                    onClick={handleTranslate}
                    className={`px-6 py-3 text-white transition duration-300 ease-in-out transform bg-blue-500 rounded-lg shadow-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-75 hover:scale-105 ${loading || !!originalText ? 'cursor-not-allowed' : ''}`}
                    disabled={loading || !!originalText}
                  >
                    {loading ? t('button.translating') : t('button.translate')}
                  </button>
                </div>
              </div>

              <ResultCard
                videoSrc={videoSrc}
                onTranslate={handleTranslate}
                loading={loading}
                translation={translation}
                originalText={originalText}
              />
            </>
          )}
        </div>
      </section>
    </DefaultLayout>
  );
};

export default IndexPage;
