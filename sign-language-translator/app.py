from flask import Flask
from mska_translator import mska_translator

app = Flask(__name__)

@app.route('/translate-sign-video', methods=['POST'])
def translate_route():
    return mska_translator()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
