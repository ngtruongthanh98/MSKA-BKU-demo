# app.py
from flask import Flask, request, jsonify
from model import MLModel

app = Flask(__name__)
model = MLModel()

# @app.route('/predict', methods=['POST'])
@app.route('/predict', methods=['GET'])
def predict():
    # X = request.json['X']
    # y = request.json['y']
    # model.train(X, y)
    # prediction = model.predict(X)
    prediction = model.predict()
    return jsonify({'prediction': prediction})

if __name__ == '__main__':
    app.run(debug=True)
