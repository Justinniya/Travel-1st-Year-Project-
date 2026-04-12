from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def landing_page():
    return "Welcome to Visayas Travel!"

@app.route('/boracay')
def boracay_page():
    return render_template('boracay_page.html')


if __name__ == '__main__':
    app.run(debug=True, port=3300)