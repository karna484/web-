from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import face_recognition
import sqlite3
import numpy as np
import cv2
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Database setup
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (username TEXT, password TEXT, face_encoding BLOB)''')
conn.commit()

# Folder to store uploaded files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        face_image = request.files['face_image']

        # Read and process the face image
        image = face_recognition.load_image_file(face_image)
        face_encodings = face_recognition.face_encodings(image)

        if not face_encodings:
            return "No face detected. Please upload a clear photo."

        # Save the face encoding in the database
        face_encoding = face_encodings[0].tobytes()
        c.execute("INSERT INTO users (username, password, face_encoding) VALUES (?, ?, ?)", 
                  (username, password, face_encoding))
        conn.commit()

        return redirect(url_for('home'))

    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    if c.fetchone():
        session['username'] = username  # Start session
        return redirect(url_for('dashboard'))
    else:
        return jsonify({"status": "error", "message": "Invalid credentials!"})

@app.route('/face_login', methods=['POST'])
def face_login():
    file = request.files['face_image']
    image = face_recognition.load_image_file(file)
    face_encodings = face_recognition.face_encodings(image)

    if not face_encodings:
        return jsonify({"status": "error", "message": "No face detected!"})

    face_encoding = face_encodings[0]

    # Compare with stored face encodings
    c.execute("SELECT username, face_encoding FROM users")
    for username, stored_encoding in c.fetchall():
        stored_encoding = np.frombuffer(stored_encoding, dtype=np.float64)
        if face_recognition.compare_faces([stored_encoding], face_encoding)[0]:
            session['username'] = username  # Start session
            return jsonify({"status": "success", "message": f"Welcome {username}!", "redirect": "/dashboard"})

    return jsonify({"status": "error", "message": "Face not recognized!"})

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        return render_template('dashboard.html', username=username)
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
