export async function translateImage(imageName: string): Promise<string> {
  const response = await fetch('http://localhost:3000/api/sl-translate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ imageName }),
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
