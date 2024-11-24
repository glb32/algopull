import os
import requests
from flask import current_app


def get_total_videos():
    cdn_path = os.path.join(current_app.root_path, 'cdn')
    return len([f for f in os.listdir(cdn_path) if f.endswith('.mp4')])

def get_next_video_number():
    return get_total_videos() + 1

def verify_captcha(token):
    try:
        response = requests.post(
            'https://challenges.cloudflare.com/turnstile/v0/siteverify',
            data={
                'secret': current_app.config['CLOUDFLARE_SECRET_KEY'],
                'response': token
            }
        )
        return response.json()['success']
    except:
        return False

def download_video(url, platform):
    video_number = get_next_video_number()
    output_path = os.path.join(current_app.root_path, 'cdn', f'{video_number}.mp4')
    #TODO: implement ig and tiktok downloads, not downloading duplicates (make a db!)
    try:
        if platform == 'tiktok':
            pass
            #get_tiktok_video(url, output_path)
        else:
            pass
            #get_ig_video(url, output_path)
        return True
    except Exception as e:
        current_app.logger.error(f"Error downloading video: {str(e)}")
        return False
