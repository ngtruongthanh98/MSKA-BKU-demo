from flask import Flask
from mska_translator import mska_translator

app = Flask(__name__)

@app.route('/mska-translator', methods=['POST'])
def mska_translator_route():
    return mska_translator()

if __name__ == '__main__':
    app.run(debug=True)
