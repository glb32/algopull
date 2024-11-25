import yt_dlp
import requests
import os
import platform
from flask import current_app

def get_valid_video_numbers():
    """Return a list of all valid video numbers in the cdn folder"""
    cdn_path = os.path.join(current_app.root_path, 'cdn')
    valid_videos = []
    
    
    current_app.logger.debug(f"All files in cdn: {os.listdir(cdn_path)}")
    
    for filename in os.listdir(cdn_path):
        if filename.endswith('.mp4'):
            file_path = os.path.join(cdn_path, filename)
            try:
                video_num = int(filename.split('.')[0])
                file_size = os.path.getsize(file_path)
                current_app.logger.debug(f"Found video {filename} with size {file_size}")
                if file_size > 0:
                    valid_videos.append(video_num)
            except (ValueError, OSError) as e:
                current_app.logger.error(f"Error processing {filename}: {str(e)}")
    
    current_app.logger.info(f"Valid videos found: {valid_videos}")
    return sorted(valid_videos)


def get_next_video_number():
    """Get the next available video number"""
    valid_videos = get_valid_video_numbers()
    if not valid_videos:
        return 1
    return max(valid_videos) + 1




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
    temp_path = os.path.join(current_app.root_path, 'cdn', f'temp_{video_number}.mp4')
    final_path = os.path.join(current_app.root_path, 'cdn', f'{video_number}.mp4')
    
    ydl_opts = {
        'format': 'mp4',  
        'outtmpl': temp_path,
        'quiet': True,
        'no_warnings': True,
        
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        
        'postprocessor_args': [
            '-c:v', 'libx264', 
            '-c:a', 'aac',      
            '-movflags', '+faststart',  
            '-pix_fmt', 'yuv420p',  
            '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2'  
        ],
    }
    
    try:
        if platform == 'tiktok':
            success = download_tiktok_video(url, ydl_opts)
        else:  
            success = download_instagram_video(url, ydl_opts)
            
        if not success:
            raise Exception("Download failed")
            
        
        if os.path.exists(temp_path):
            os.rename(temp_path, final_path)
            
        return True
    except Exception as e:
        current_app.logger.error(f"Error downloading video: {str(e)}")
        
        for path in [temp_path, final_path]:
            if os.path.exists(path):
                os.remove(path)
        return False

def download_tiktok_video(url, ydl_opts):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        current_app.logger.error(f"TikTok download error: {str(e)}")
        return False

def download_instagram_video(url, ydl_opts):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        current_app.logger.error(f"Instagram download error: {str(e)}")
        return False
    

def get_ffmpeg_path():
  
    project_root = os.path.abspath(os.path.join(current_app.root_path, '..'))
    
    if platform.system() == 'Windows':
        ffmpeg_path = os.path.join(project_root, 'bin', 'ffmpeg.exe')
    else:
        ffmpeg_path = os.path.join(project_root, 'bin', 'ffmpeg')
    
    current_app.logger.info(f"Looking for FFmpeg at: {ffmpeg_path}")
    
    
    if not os.path.exists(ffmpeg_path):
        current_app.logger.error(f"FFmpeg not found at: {ffmpeg_path}")
        raise FileNotFoundError(f"FFmpeg not found at: {ffmpeg_path}")
        
    return ffmpeg_path

def get_valid_video_numbers():
    """Return a list of all valid video numbers in the cdn folder"""
    cdn_path = os.path.join(current_app.root_path, 'cdn')
    valid_videos = []
    
    for filename in os.listdir(cdn_path):
        if filename.endswith('.mp4') and not filename.startswith('temp_'):
            try:
                video_num = int(filename.split('.')[0])
                file_path = os.path.join(cdn_path, filename)
                if os.path.getsize(file_path) > 0:
                    valid_videos.append(video_num)
            except ValueError:
                continue
    
    return sorted(valid_videos)

def cleanup_temp_files():
    
    cdn_path = os.path.join(current_app.root_path, 'cdn')
    for filename in os.listdir(cdn_path):
        if filename.startswith('temp_'):
            try:
                os.remove(os.path.join(cdn_path, filename))
            except Exception as e:
                current_app.logger.error(f"Error removing temp file {filename}: {str(e)}")
