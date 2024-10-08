import os
import json
from flask import request, jsonify

def mska_translator():
    data = request.get_json()
    video_name = data.get('videoName')

    # Debugging information
    print('Received videoName:', video_name)

    if not video_name:
        return jsonify({'error': 'videoName is required'}), 400

    # Construct the file path
    file_path = os.path.join(os.path.dirname(__file__), '../data/results.json')
    print('File path:', file_path)  # Debugging information

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            results = json.load(file)
    except IOError as e:
        print('Error reading file:', e)
        return jsonify({'error': 'Error reading file'}), 500
    except json.JSONDecodeError as e:
        print('Error parsing JSON:', e)
        return jsonify({'error': 'Error parsing JSON'}), 500

    result = next((entry for entry in results if video_name in entry['name']), None)

    if result:
        return result['txt_hyp']
    else:
        return jsonify({'error': 'Video name not found'}), 404
