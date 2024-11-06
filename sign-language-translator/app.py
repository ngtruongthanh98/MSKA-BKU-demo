import getpass
import threading
from flask import Flask
from pyngrok import ngrok, conf
from mska_translator import mska_translator

app = Flask(__name__)

@app.route('/translate-sign-video', methods=['POST'])
def translate_route():
    return mska_translator()

if __name__ == '__main__':
    # auth_token = getpass.getpass("Enter your ngrok authtoken, which can be copied from https://dashboard.ngrok.com/get-started/your-authtoken: ")
    auth_token = '2oSxR6sYqEk9YGsvagepltCTLQx_2igWYPxQQyBsDPbE8hskv'
    conf.get_default().auth_token = auth_token

    # Open a ngrok tunnel to the HTTP server
    public_url = ngrok.connect(5000).public_url
    print(f" * ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:5000/\"")

    # Update the base URL
    app.config["BASE_URL"] = public_url

    # Start the Flask server in a new thread
    threading.Thread(target=app.run, kwargs={"use_reloader": False, "host": '0.0.0.0', "port": 5000, "debug": True}).start()
