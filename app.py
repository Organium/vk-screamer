import os
import json
import logging
from flask import Flask, redirect, request, render_template, session
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure logging
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# VK OAuth configuration
VK_CLIENT_ID = os.getenv('VK_CLIENT_ID')
VK_CLIENT_SECRET = os.getenv('VK_CLIENT_SECRET')
VK_REDIRECT_URI = os.getenv('VK_REDIRECT_URI')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    vk_auth_url = f'https://oauth.vk.com/authorize?client_id={VK_CLIENT_ID}&redirect_uri={VK_REDIRECT_URI}&response_type=code&scope=email'
    return redirect(vk_auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'Authorization failed', 400

    # Exchange code for access token
    token_url = f'https://oauth.vk.com/access_token?client_id={VK_CLIENT_ID}&client_secret={VK_CLIENT_SECRET}&redirect_uri={VK_REDIRECT_URI}&code={code}'
    response = requests.get(token_url)
    data = response.json()

    if 'error' in data:
        return 'Token exchange failed', 400

    user_id = data.get('user_id')
    email = data.get('email', 'No email provided')

    # Log user information
    logging.info(f'User ID: {user_id}, Email: {email}')

    # Store user info in session
    session['user_id'] = user_id
    session['email'] = email

    return redirect('/screamer')

@app.route('/screamer')
def screamer():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('screamer.html')

if __name__ == '__main__':
    app.run(debug=True) 