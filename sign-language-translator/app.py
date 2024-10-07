import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/mska-translator', methods=['POST'])
def mska_translator():
    data = request.get_json()
    image_array = data.get('imageArray', [])
    video_name = data.get('videoName')

    # Process the imageArray as needed
    print('Received imageArray:', image_array)
    print('Received videoName:', video_name)

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
        return jsonify({'txt_hyp': result['txt_hyp']})
    else:
        return jsonify({'error': 'Image name not found'}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
