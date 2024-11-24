from flask import Blueprint, render_template, jsonify, request, send_from_directory, current_app
from app.utils import get_total_videos, verify_captcha, download_video
import random
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/random-video')
def random_video():
    total_videos = get_total_videos()
    if total_videos == 0:
        return jsonify({'error': 'No videos available'}), 404
    
    random_number = random.randint(1, total_videos)
    return jsonify({'video_number': random_number})

@main.route('/cdn/<video_number>')
def serve_video(video_number):
    return send_from_directory(
        os.path.join(current_app.root_path, 'cdn'),
        f'{video_number}.mp4'
    )

@main.route('/api/submit-video', methods=['POST'])
def submit_video():
    data = request.json
    
    if not all(k in data for k in ['url', 'platform', 'token']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if not verify_captcha(data['token']):
        return jsonify({'error': 'Invalid captcha'}), 400

    if download_video(data['url'], data['platform']):
        return jsonify({'message': 'Success'})
    else:
        return jsonify({'error': 'Failed to download video'}), 500
