from flask import Flask, request, render_template
from flask_login import *
import db

app = Flask(__name__)


@app.route('/')
def index():
    return 'hello world'


@app.route('/login')
def index():
    return 'hello world'


@app.route('/test', methods=['POST', 'GET'])
def test():
    if request.method == "GET":
        print("GET")
        return render_template('test.html', message="GET")
    else:
        print('POST')
        id = request.form['ID']
        message = db.get_data(id)
        for i in message:
            print(i)
        return render_template('test.html', message=message, id=id)


if __name__ == '__main__':
    app.run(debug=True)
