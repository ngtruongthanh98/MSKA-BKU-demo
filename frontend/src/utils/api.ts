export async function translateImage(imageName: string): Promise<string> {
  const response = await fetch('http://localhost:3000/api/translate', {
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
