

#importing the essential libraries
from flask import Flask , render_template , request , redirect, url_for ,  flash
import pickle
import numpy as np
import hashlib
import secrets
import sqlite3

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generates a random 16-byte hex string

# Loading the saved models
model = pickle.load(open('model.pkl', 'rb'))
cv = pickle.load(open('vector.pkl', 'rb'))

users = {
    'root': {
        'password': hashlib.sha256('123456'.encode()).hexdigest()  # Hashed password
    },
    'admin': {
        'password': hashlib.sha256('123456'.encode()).hexdigest()  # Hashed password for admin
    }
}
def get_db_connection():
    conn = sqlite3.connect('feedback.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def register():
    return render_template('register.html')

@app.route('/predict', methods=['POST'])
def predict():
    message = request.form['text']
    data = [message]
    data = cv.transform(data).toarray()
    pred = model.predict(data)
    return render_template('result.html', prediction=pred[0])

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        comments = request.form['comments']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO feedback (name, email, comments) VALUES (?, ?, ?)',
                     (name, email, comments))
        conn.commit()
        conn.close()
        
        flash('Feedback submitted successfully!', 'success')
        return redirect(url_for('feedback'))
    return render_template('feedback.html')

@app.route('/description')
def description():
    return render_template('description.html')

@app.route('/article')
def article():
    return render_template('article.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username in users and hashlib.sha256(password.encode()).hexdigest() == users[username]['password']:
        if username == 'admin':
            return redirect(url_for('admin'))
        else:
            # Set session to remember the user
            return redirect(url_for('home'))
    else:
        flash('Invalid username or password. Please try again.', 'danger')
        return render_template('register.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']

    if username in users:
        flash('Username already exists. Please choose a different one.', 'danger')
    else:
        # Hash the password before storing (for security)
        users[username] = {'password': hashlib.sha256(password.encode()).hexdigest()}
        flash('Signed up successfully! You can now login.', 'success')

    return render_template('register.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/admin')
def admin():
    conn = get_db_connection()
    feedbacks = conn.execute('SELECT * FROM feedback').fetchall()
    conn.close()
    return render_template('admin.html', feedbacks=feedbacks)

if __name__ == '__main__':
    app.run(debug=True)
