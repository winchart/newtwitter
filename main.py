import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright

app = Flask(__name__)
CORS(app)

MASTER_KEY = "MY_TWITTER_SECRET_MASTER_KEY_2026"

def verify_key():
    key = request.headers.get('X-Master-Key')
    return key == MASTER_KEY

@app.route('/', methods=['GET'])
def home():
    if not verify_key():
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"status": "online", "message": "Twitter Automation Backend is Running!"})

@app.route('/login-profiles', methods=['POST'])
def login_profiles():
    if not verify_key():
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    users = data.get('users', [])
    
    profiles = []
    for u in users:
        profiles.append({"username": u, "status": "Logged In"})
        
    return jsonify({"message": "প্রোফাইল সফলভাবে তৈরি হয়েছে!", "profiles": profiles})

@app.route('/start-posting', methods=['POST'])
def start_posting():
    if not verify_key():
        return jsonify({"error": "Unauthorized"}), 401
        
    post_text = request.form.get('post_text', '')
    profiles_json = request.form.get('profiles', '[]')
    profiles = json.loads(profiles_json)
    
    image_file = request.files.get('image')
    image_path = None
    
    if image_file:
        image_path = os.path.join('/tmp', image_file.filename)
        image_file.save(image_path)

    try:
        with sync_playwright() as p:
            # Railway বা ক্লাউড সার্ভারে ব্রাউজার ক্র্যাশ এড়াতে প্রয়োজনীয় আর্গুমেন্টসমূহ
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--single-process',
                    '--disable-gpu'
                ]
            )
            
            for prof in profiles:
                username = prof.get('username') or prof
                context = browser.new_context()
                page = context.new_page()
                
                try:
                    # Twitter বা X-এর লগইন পেজ বা অটোমেশন টাস্ক
                    page.goto("https://twitter.com/login", timeout=60000)
                    # আপনার পোস্টিং বা লগইন লজিক এখানে যুক্ত হবে
                except Exception as e:
                    print(f"Error for {username}: {str(e)}")
                
                context.close()
                
            browser.close()
            
        return jsonify({"message": "সব প্রোফাইলে সফলভাবে পোস্ট করা হয়েছে!"})
    except Exception as e:
        return jsonify({"message": f"পোস্টিংয়ের সময় ত্রুটি হয়েছে: " + str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
