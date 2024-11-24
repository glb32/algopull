let isSubmitting = false;
//TODO: fix new video not loading on click
function loadRandomVideo() {
    const video = document.getElementById('video-player');
    const currentSrc = video.src;

    fetch('/api/random-video')
        .then(response => response.json())
        .then(data => {
            if (data.video_number) {
                const newSrc = `/cdn/${data.video_number}`;
                if (newSrc !== currentSrc) {
                    video.src = newSrc;
                    video.play().catch(e => console.error('Playback failed:', e));
                }
            }
        })
        .catch(error => console.error('Error loading video:', error));
}

function openModal() {
    document.getElementById('submit-modal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    document.getElementById('submit-modal').style.display = 'none';
    document.body.style.overflow = '';
    resetForm();
}

function resetForm() {
    document.getElementById('video-url').value = '';
    document.getElementById('status-message').innerHTML = '';
    document.getElementById('submit-btn').disabled = true;
    isSubmitting = false;
    updateSubmitButtonState();
}

function enableSubmit(token) {
    document.getElementById('submit-btn').disabled = false;
    document.getElementById('submit-btn').onclick = () => submitVideo(token);
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
            setTimeout(() => {
                closeModal();
                loadRandomVideo();
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
    });
}


window.onclick = function(event) {
    const modal = document.getElementById('submit-modal');
    if (event.target === modal) {
        closeModal();
    }
}


document.getElementById('video-player').addEventListener('error', function(e) {
    console.error('Video error:', e);
    loadRandomVideo(); 
});


window.addEventListener('DOMContentLoaded', loadRandomVideo);


