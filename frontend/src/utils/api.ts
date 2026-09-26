export async function translateVideoToText(videoName: string): Promise<string> {
  const response = await fetch('http://localhost:3000/api/sl-translate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ videoName }),
  });

  if (!response.ok) {
    throw new Error('Network response was not ok');
  }

  const data = await response.text();
  return data;
}


export async function googleTranslate(text: string, target: string): Promise<string> {
  const response = await fetch('http://localhost:3000/api/google-translate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text, target }),
  });

  if (!response.ok) {
    throw new Error('Network response was not ok');
  }

  const data = await response.json();
  return data.translatedText;
}

export async function getVideo(videoName: string): Promise<string> {
  const response = await fetch('http://localhost:3000/api/get-video', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ videoName }),
  });

  if (!response.ok) {
    throw new Error('Network response was not ok');
  }

  const data = await response.json();
  return data.videoUrl;
}

export async function getVideoFrames(videoName: string): Promise<string> {
  const response = await fetch('http://localhost:3000/api/video-to-frames', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ videoName }),
  });

  if (!response.ok) {
    throw new Error('Network response was not ok');
  }

  const data = await response.json();
  return data.videoUrl;
}

export async function videoToText(videoFile: File): Promise<string> {
  const formData = new FormData();
  formData.append('file', videoFile);

  const response = await fetch('http://localhost:3000/api/video-to-text', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Network response was not ok');
  }

  const data = await response.text();
  return data;
}

export interface DemoVideoSummary {
  name: string;
  category: string;
  gtncFlag: boolean;
}

export interface DemoResult {
  name: string;
  split: string;
  glossHyp: string;
  glossRef: string;
  textHyp: string;
  textRef: string;
  gtncFlag: boolean;
  numErr: number;
  category: string;
}

export async function listDemoVideos(): Promise<DemoVideoSummary[]> {
  const response = await fetch('http://localhost:3000/api/demo/videos');

  if (!response.ok) {
    throw new Error('Network response was not ok');
  }

  return response.json();
}

export async function getDemoResult(videoName: string): Promise<DemoResult> {
  const response = await fetch('http://localhost:3000/api/demo/translate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ videoName }),
  });

  if (!response.ok) {
    throw new Error('Network response was not ok');
  }

  return response.json();
}
