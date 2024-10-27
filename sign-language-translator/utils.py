import subprocess

def get_training_result(file_path, config_path, resume_path, input_keypoints_path):
    command = [
        'python', file_path,
        '--config', config_path,
        '--resume', resume_path,
        '--input_keypoints_path', input_keypoints_path,
        '--eval'
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr}")
        return None
