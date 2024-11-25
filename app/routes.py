from flask import Blueprint, render_template, jsonify, request, send_from_directory, current_app
from app.utils import get_valid_video_numbers, verify_captcha, download_video
import random
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/available-videos')
def available_videos():
    try:
        cdn_path = os.path.join(current_app.root_path, 'cdn')
        files = os.listdir(cdn_path)
        
        valid_videos = []
        for filename in files:
            if filename.endswith('.mp4'):
                try:
                    video_num = int(filename.split('.')[0])
                    file_path = os.path.join(cdn_path, filename)
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        valid_videos.append(video_num)
                except ValueError:
                    continue
        
        return jsonify({
            'videos': sorted(valid_videos),
            'cdn_path': cdn_path,
            'all_files': files
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'cdn_path': cdn_path if 'cdn_path' in locals() else None
        }), 500


@main.route('/api/random-video')
def random_video():
    valid_videos = get_valid_video_numbers()
    current_app.logger.info(f"Selecting from videos: {valid_videos}")
    
    if not valid_videos:
        return jsonify({'error': 'No videos available'}), 404
    
    #force unique selection
    selected_video = random.choice(valid_videos)
    current_app.logger.info(f"Selected video: {selected_video}")
    
    #sometimes shit gets cached and the browser plays a video over and over again, this fixes it apparently
    response = jsonify({'video_number': selected_video})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

@main.route('/cdn/<filename>')
def serve_video(filename):
    cdn_path = os.path.join(current_app.root_path, 'cdn')
    file_path = os.path.join(cdn_path, filename)
    
    
    current_app.logger.info(f"Requested file: {filename}")
    current_app.logger.info(f"Full path: {file_path}")
    current_app.logger.info(f"File exists: {os.path.exists(file_path)}")
    
    if not os.path.exists(file_path):
        return jsonify({
            'error': 'File not found',
            'requested_path': file_path,
            'cdn_path': cdn_path
        }), 404
        
    try:
        return send_from_directory(cdn_path, filename, conditional=True)
    except Exception as e:
        current_app.logger.error(f"Error serving video {filename}: {str(e)}")
        return jsonify({
            'error': str(e),
            'requested_path': file_path
        }), 500

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

