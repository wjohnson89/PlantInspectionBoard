from flask import Flask, render_template, request, jsonify
import threading, webbrowser, xmlreader

app = Flask(__name__)


@app.after_request
def add_header(response):
    """
    Add headers to both force the latest IE rendering engine or  Chrome Frame,
    and also to cache the rendered page for 1 minute.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge, chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.route('/')
def index():
    try:
        xmlreader.run()
        return render_template('index.html')
    except (FileNotFoundError, IOError) as e:
        print(e)


if __name__ == '__main__':
    port = 5000
    url = 'http://127.0.0.1:{0}'.format(port)
    threading.Timer(1.25, lambda: webbrowser.open(url)).start()
    app.run(port=port, debug=False)
