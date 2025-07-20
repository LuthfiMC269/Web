from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/page_baru')
def page_baru():
    return render_template('page.html')

if __name__ == '__main__':
    app.run("0.0.0.0")
