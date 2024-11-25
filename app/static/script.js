let isSubmitting = false;
let videoManager;

class VideoManager {
    constructor() {
        this.currentVideoNumber = null;
        this.availableVideos = [];
        this.isLoading = false;
        this.hasUserInteracted = false;
    }

    async initialize() {
        try {
            await this.refreshVideoList();
            if (this.availableVideos.length === 0) {
                console.error('No videos available');
            }
        } catch (error) {
            console.error('Error initializing video manager:', error);
        }
    }

    async checkVideoExists(videoNumber) {
        try {
            const response = await fetch(`/cdn/${videoNumber}.mp4`, {
                method: 'HEAD'
            });
            return response.ok;
        } catch (error) {
            console.error('Error checking video:', error);
            return false;
        }
    }

    async loadRandomVideo() {
        if (this.isLoading || this.availableVideos.length === 0) {
            console.log('Skip loading: isLoading=', this.isLoading, 'availableVideos=', this.availableVideos.length);
            return;
        }

        this.isLoading = true;
        const video = document.getElementById('video-player');

        try {
            const videoNumber = this.getRandomVideo();
            if (!videoNumber) {
                console.error('No valid video number selected');
                return;
            }

            const exists = await this.checkVideoExists(videoNumber);
            if (!exists) {
                console.error(`Video ${videoNumber} not found`);
                this.availableVideos = this.availableVideos.filter(v => v !== videoNumber);
                throw new Error('Video not found');
            }

            const newSrc = `/cdn/${videoNumber}.mp4?${Date.now()}`;
            console.log('Loading video:', videoNumber, 'from:', newSrc);

            const loadPromise = new Promise((resolve, reject) => {
                const handleLoad = () => {
                    video.removeEventListener('loadeddata', handleLoad);
                    video.removeEventListener('error', handleError);
                    resolve();
                };
                
                const handleError = (error) => {
                    video.removeEventListener('loadeddata', handleLoad);
                    video.removeEventListener('error', handleError);
                    reject(error);
                };

                video.addEventListener('loadeddata', handleLoad);
                video.addEventListener('error', handleError);
            });

            video.src = newSrc;
            video.load();

            await loadPromise;
            this.currentVideoNumber = videoNumber;
            
            if (this.hasUserInteracted) {
                await video.play();
            }

        } catch (error) {
            console.error('Error loading video:', error);
            await this.refreshVideoList();
            setTimeout(() => this.loadRandomVideo(), 1000);
        } finally {
            this.isLoading = false;
        }
    }

    async refreshVideoList() {
        try {
            const response = await fetch('/api/available-videos');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            this.availableVideos = data.videos;
            console.log('Available videos:', this.availableVideos);
        } catch (error) {
            console.error('Error refreshing video list:', error);
            this.availableVideos = [];
        }
    }

    getRandomVideo() {
        if (this.availableVideos.length === 0) return null;
        if (this.availableVideos.length === 1) return this.availableVideos[0];

        const availableChoices = this.availableVideos.filter(
            num => num !== this.currentVideoNumber
        );

        if (availableChoices.length === 0) {
            return this.availableVideos[0];
        }

        const randomIndex = Math.floor(Math.random() * availableChoices.length);
        return availableChoices[randomIndex];
    }

    async handleFirstInteraction() {
        if (!this.hasUserInteracted) {
            this.hasUserInteracted = true;
            const video = document.getElementById('video-player');
            try {
                await video.play();
            } catch (error) {
                console.error('Error playing video:', error);
            }
        }
    }
}

async function loadRandomVideo() {
    if (videoManager) {
        await videoManager.loadRandomVideo();
    } else {
        console.error('Video manager not initialized');
    }
}

function openModal() {
    document.getElementById('submit-modal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    document.getElementById('submit-modal').style.display = 'none';
    document.body.style.overflow = '';
    resetForm();
    resetCaptcha();
}

function resetForm() {
    document.getElementById('video-url').value = '';
    document.getElementById('status-message').innerHTML = '';
    document.getElementById('submit-btn').disabled = true;
    isSubmitting = false;
    updateSubmitButtonState();
}

function enableSubmit(token) {
    const submitBtn = document.getElementById('submit-btn');
    submitBtn.disabled = false;
    submitBtn.onclick = () => submitVideo(token);
}

function disableSubmit() {
    document.getElementById('submit-btn').disabled = true;
}

function updateSubmitButtonState() {
    const button = document.getElementById('submit-btn');
    const buttonText = button.querySelector('.button-text');
    const spinner = button.querySelector('.loading-spinner');
    
    if (isSubmitting) {
        buttonText.style.display = 'none';
        spinner.style.display = 'block';
        button.disabled = true;
    } else {
        buttonText.style.display = 'block';
        spinner.style.display = 'none';
    }
}

function resetCaptcha() {
    turnstile.reset();
    disableSubmit();
}

function submitVideo(token) {
    if (isSubmitting) return;

    const url = document.getElementById('video-url').value;
    const platform = document.getElementById('platform-select').value;
    const statusDiv = document.getElementById('status-message');
    
    statusDiv.className = '';
    statusDiv.textContent = '';

    if (!url) {
        statusDiv.textContent = 'Please enter a video URL';
        statusDiv.className = 'error';
        return;
    }

    isSubmitting = true;
    updateSubmitButtonState();

    fetch('/api/submit-video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            url: url,
            platform: platform,
            token: token
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            statusDiv.textContent = data.error;
            statusDiv.className = 'error';
        } else {
            statusDiv.textContent = 'Video submitted successfully!';
            statusDiv.className = 'success';
            setTimeout(async () => {
                closeModal();
                if (videoManager.hasUserInteracted) {
                    await videoManager.loadRandomVideo();
                }
            }, 2000);
        }
    })
    .catch(error => {
        statusDiv.textContent = 'An error occurred. Please try again.';
        statusDiv.className = 'error';
    })
    .finally(() => {
        isSubmitting = false;
        updateSubmitButtonState();
        resetCaptcha();
    });
}

// Event Listeners
document.addEventListener('DOMContentLoaded', async () => {
    videoManager = new VideoManager();
    
    const video = document.getElementById('video-player');
    const videoContainer = document.querySelector('.video-container');
    
    const loadingIndicator = document.createElement('div');
    loadingIndicator.id = 'loading-indicator';
    loadingIndicator.style.display = 'none';
    loadingIndicator.textContent = 'Loading...';
    video.parentNode.insertBefore(loadingIndicator, video.nextSibling);

    videoContainer.addEventListener('click', () => {
        videoManager.handleFirstInteraction();
    });

    video.addEventListener('loadstart', () => {
        loadingIndicator.style.display = 'block';
    });

    video.addEventListener('loadeddata', () => {
        loadingIndicator.style.display = 'none';
    });

    video.addEventListener('error', (e) => {
        loadingIndicator.style.display = 'none';
        console.error('Video error:', e);
        if (videoManager.hasUserInteracted) {
            loadRandomVideo();
        }
    });

    await videoManager.initialize();
    await videoManager.loadRandomVideo();

    video.addEventListener('ended', () => {
        if (videoManager.hasUserInteracted) {
            loadRandomVideo();
        }
    });
});

window.onclick = function(event) {
    const modal = document.getElementById('submit-modal');
    if (event.target === modal) {
        closeModal();
    }
};
