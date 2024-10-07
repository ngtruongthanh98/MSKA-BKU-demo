# app.py
from flask import Flask, request, jsonify
from model import MLModel

app = Flask(__name__)
model = MLModel()

@app.route('/predict', methods=['GET'])
def predict():
    prediction = model.predict()
    return jsonify({'prediction': prediction})

@app.route('/receive-images', methods=['POST'])
def receive_images():
    data = request.get_json()
    image_array = data.get('imageArray', [])

    # Process the imageArray as needed
    print('Received imageArray:', image_array)

    return jsonify({'message': 'Images received successfully'}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
