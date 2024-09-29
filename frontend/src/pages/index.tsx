import React, { useState, useRef } from 'react';
import DefaultLayout from '@/layouts/default';
import VideoCard from '@/components/VideoCard';

const IndexPage: React.FC = () => {
  const [videoSrc, setVideoSrc] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleVideoUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const videoURL = URL.createObjectURL(file);
      setVideoSrc(videoURL);
    }
  };

  const handleDeleteVideo = () => {
    if (videoSrc) {
      URL.revokeObjectURL(videoSrc);
      setVideoSrc(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <DefaultLayout>
      <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
        <div className="justify-center inline-block max-w-lg text-center">
          <h1 className="text-4xl font-bold">Upload Your Sign Language Video</h1>
          <input
            type="file"
            accept="video/*"
            onChange={handleVideoUpload}
            className="mt-4"
            ref={fileInputRef}
          />
          {videoSrc && (
            <VideoCard videoSrc={videoSrc} onDelete={handleDeleteVideo} />
          )}
        </div>
      </section>
    </DefaultLayout>
  );
};

export default IndexPage;
