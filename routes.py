from flask import Blueprint, render_template, request, redirect, flash
from models import db, User, Profile
import os
from werkzeug.utils import secure_filename
import subprocess
import random
from flask import session
import time

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app_routes = Blueprint('app_routes', __name__)
app_routes.config = {'UPLOAD_FOLDER': UPLOAD_FOLDER}

# Vulnerable Login Route (Broken Authentication)
@app_routes.route('/login', methods=['GET', 'POST'])
def login():
    if 'attempts' not in session:
        session['attempts'] = 0

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # ✅ No lockout → Vulnerable to brute force
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['attempts'] = 0
            flash('Logged in successfully!', 'success')
            return redirect('/')
        else:
            session['attempts'] += 1
            if session['attempts'] > 5:
                time.sleep(2)  # ✅ Slow down after 5 attempts (basic protection)
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

# Vulnerable XSS Route
@app_routes.route('/comment', methods=['POST'])
def comment():
    comment = request.form.get('comment')
    # ✅ No escaping - Vulnerable to XSS
    return f"<h1>{comment}</h1>"

# Vulnerable SQL Injection Route
@app_routes.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search = request.form.get('search')
        # ✅ Direct string formatting - Vulnerable to SQL Injection
        query = f"SELECT * FROM user WHERE username = '{search}'"
        result = db.engine.execute(query)
        return str([row for row in result])

    return render_template('search.html')

@app_routes.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if request.method == 'POST':
        from_user = request.form.get('from_user')
        to_user = request.form.get('to_user')
        amount = request.form.get('amount')

        # ✅ No CSRF token - vulnerable to CSRF
        query = f"UPDATE accounts SET balance = balance - {amount} WHERE username = '{from_user}'"
        db.engine.execute(query)
        query = f"UPDATE accounts SET balance = balance + {amount} WHERE username = '{to_user}'"
        db.engine.execute(query)

        return f"Transferred ₹{amount} from {from_user} to {to_user}"

    return render_template('transfer.html')

@app_routes.route('/profile/<int:id>', methods=['GET'])
def profile(id):
    # ✅ No permission check - vulnerable to IDOR
    profile = Profile.query.get(id)
    if profile:
        return f"<h1>{profile.full_name}</h1><p>{profile.email}</p>"
    return "Profile not found"

@app_routes.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            # ✅ No file extension check - Vulnerable to malicious file uploads
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            return f"File uploaded: {filename}"
    return render_template('upload.html')

@app_routes.route('/ping', methods=['POST'])
def ping():
    target = request.form.get('target')
    # ✅ Direct shell execution - Vulnerable to command injection
    result = subprocess.getoutput(f"ping -c 4 {target}")
    return f"<pre>{result}</pre>"

@app_routes.route('/.git/config', methods=['GET'])
def git_config():
    try:
        with open('.git/config', 'r') as file:
            return f"<pre>{file.read()}</pre>"  # ✅ Exposing git config file
    except FileNotFoundError:
        return "Git config not found"

@app_routes.route('/session-fixation', methods=['GET', 'POST'])
def session_fixation():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            # ✅ Vulnerable to session fixation - Fixed session ID
            session['user_id'] = 1  # Fix session to user ID 1
            return f"Session fixed for user: {user.username}"
        else:
            flash('Invalid login', 'danger')

    return render_template('login.html')

@app_routes.route('/read-file', methods=['GET'])
def read_file():
    filename = request.args.get('filename')
    # ✅ No path sanitization - Vulnerable to directory traversal
    try:
        with open(f'static/uploads/{filename}', 'r') as file:
            return f"<pre>{file.read()}</pre>"
    except FileNotFoundError:
        return "File not found"
