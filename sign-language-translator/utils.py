import subprocess

def get_training_result(file_path, config_path, resume_path, input_keypoints_path):
    command = [
        'python', file_path,
        '--config', config_path,
        '--resume', resume_path,
        '--input_keypoints_path', input_keypoints_path,
        '--eval'
    ]

    print('file_path: ', file_path)

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        print('test result: ', result)

        # return result.stdout

        # return json file in ../result/predicted_result.json
        with open('../result/predicted_result.json', 'r', encoding='utf-8') as file:
            results = json.load(file)
            return results

    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr}")
        return None

def hello_world():
    return 'Hello, World!'
