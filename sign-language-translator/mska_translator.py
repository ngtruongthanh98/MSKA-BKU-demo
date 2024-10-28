import os
import json
from flask import request, jsonify
from utils import get_training_result, hello_world

def mska_translator():
    data = request.get_json()
    video_name = data.get('videoName')
    image_array = data.get('imageArray')

    file_path = '../../baseline-MSKA/train.py'
    config_path = '../../baseline-MSKA/configs/phoenix-2014t_s2t.yaml'
    resume_path = '../../pretrained_models/Phoenix-2014T_SLT/best.pth'
    input_keypoints_path = os.path.join('../../HRNet-keypoints', video_name, 'src_input.pkl')

    if not video_name:
        return jsonify({'error': 'videoName is required'}), 400

    # # Construct the file path
    # file_path = os.path.join(os.path.dirname(__file__), '../data/results.json')

    # try:
    #     with open(file_path, 'r', encoding='utf-8') as file:
    #         results = json.load(file)
    #         print(hello_world())
    # except IOError as e:
    #     print('Error reading file:', e)
    #     return jsonify({'error': 'Error reading file'}), 500
    # except json.JSONDecodeError as e:
    #     print('Error parsing JSON:', e)
    #     return jsonify({'error': 'Error parsing JSON'}), 500

    try:
        result = get_training_result(file_path, config_path, resume_path, input_keypoints_path)

        return result['txt_hyp']

    except Exception as e:
        print('Error occurred:', e)
        return jsonify({'error': 'Error occurred'}), 500

    # result = next((entry for entry in results if video_name in entry['name']), None)

    # if result:
    #     return result['txt_hyp']
    # else:
    #     return jsonify({'error': 'Video name not found'}), 404


    # return 'Im süden hält sich der nebel zum teil länger an auf den bergen scheint die sonne auch für längere zeit.'
