# Sign Language Translater

## Introduction
This project uses the Talkify TTS API for text-to-speech functionality.

## Setup

### Register for Talkify TTS API
1. Visit the [Talkify TTS API Registration](https://manage.talkify.net/).
2. Create an account or log in if you already have one.
3. Navigate to the API section and generate a new API key.
4. Copy the generated API key.

### Configuration
1. Add the Talkify script to your `public/index.html` file:
    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>React App</title>
      <script src="https://cdn.talkify.net/talkify.js"></script>
    </head>
    <body>
      <div id="root"></div>
    </body>
    </html>
    ```

2. Initialize Talkify in your React component:
    ```tsx
    import React, { useEffect, useState } from 'react';

    const App = () => {
      useEffect(() => {
        if (window.talkify) {
          window.talkify.config.remoteService.host = 'https://talkify.net';
          window.talkify.config.remoteService.apiKey = 'YOUR_API_KEY_HERE';
          window.talkify.config.ui.audioControls.enabled = true;
          window.talkify.config.ui.audioControls.voicepicker.enabled = true;

          window.talkify.selectionActivator
            .withTextHighlighting()
            .activate();
        }
      }, []);

      const handleTextToSpeech = () => {
        if (window.talkify) {
          const player = new window.talkify.TtsPlayer();
          player.playText('Hello world');
        }
      };

      return (
        <div>
          <button onClick={handleTextToSpeech}>Speak</button>
        </div>
      );
    };

    export default App;
    ```

Replace `'YOUR_API_KEY_HERE'` with the API key you generated from the Talkify dashboard.

## Usage
Click the "Speak" button to hear the text "Hello world" spoken aloud using Talkify TTS.
