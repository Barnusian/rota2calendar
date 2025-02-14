from flask import Flask, render_template, request

app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/whatisthis')
def what():
    return render_template('what.html')

@app.route('/howdoesthiswork')
def how():
    return render_template('how.html')

@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'GET':
        return render_template('testpage.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'Barnie' and password == 'Aja2805!8':
            return "YOU HAVE LOGGED IN"
        else:
            return "YOU HAVE DIED"

@app.route('/file_upload', methods=['POST'])
def file_upload():
    return "YEP, Uploaded"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)