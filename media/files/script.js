// Lightbox functionality
        function openLightbox(src) {
            const lightbox = document.querySelector('.lightbox');
            const lightboxImg = lightbox.querySelector('img.lightbox-content');
            const lightboxVideo = lightbox.querySelector('video.lightbox-content');
            
            if (src.endsWith('.mp4')) {
                lightboxVideo.querySelector('source').src = src;
                lightboxVideo.style.display = 'block';
                lightboxImg.style.display = 'none';
                lightboxVideo.load(); // Reload the video with new source
            } else {
                lightboxImg.src = src;
                lightboxImg.style.display = 'block';
                lightboxVideo.style.display = 'none';
            }
            
            lightbox.classList.add('active');
        }

        function closeLightbox() {
            const lightbox = document.querySelector('.lightbox');
            const lightboxVideo = lightbox.querySelector('video.lightbox-content');
            lightbox.classList.remove('active');
            lightboxVideo.pause(); // Stop video playback when closing
        }

        // Prevent lightbox from closing when clicking on media
        document.querySelector('.lightbox-content').onclick = function(e) {
            e.stopPropagation();
        };

        // Lightbox functionality for videos
        function openLightbox(src) {
            const lightbox = document.querySelector('.lightbox');
            const lightboxImg = lightbox.querySelector('img.lightbox-content');
            const lightboxVideo = lightbox.querySelector('video.lightbox-content');

            if (src.endsWith('.mp4')) {
                lightboxVideo.querySelector('source').src = src;
                lightboxVideo.style.display = 'block';
                lightboxImg.style.display = 'none';
                lightboxVideo.load(); // Reload the video with new source
            } else {
                lightboxImg.src = src;
                lightboxImg.style.display = 'block';
                lightboxVideo.style.display = 'none';
            }

            lightbox.classList.add('active');
        }

        function closeLightbox() {
            const lightbox = document.querySelector('.lightbox');
            const lightboxVideo = lightbox.querySelector('video.lightbox-content');
            lightbox.classList.remove('active');
            lightboxVideo.pause(); // Stop video playback when closing
        }

        // Prevent lightbox from closing when clicking on media
        document.querySelector('.lightbox-content').onclick = function(e) {
            e.stopPropagation();
        };

        // Enhanced audio player functionality
    function toggleAudio(button) {
        const audioContainer = button.closest('.audio-message');
        const audio = audioContainer.querySelector('audio');
        const icon = button.querySelector('i');
        const progressBar = audioContainer.querySelector('.progress');
        const timeDisplay = audioContainer.querySelector('.audio-time');
        
        if (audio.paused) {
            audio.play();
            icon.className = 'fas fa-pause';
            
            audio.ontimeupdate = function() {
                const percentage = (audio.currentTime / audio.duration) * 100;
                progressBar.style.width = percentage + '%';
                timeDisplay.textContent = formatTime(audio.currentTime);
            };
            
            audio.onended = function() {
                icon.className = 'fas fa-play';
                progressBar.style.width = '0%';
                timeDisplay.textContent = formatTime(audio.duration);
            };
        } else {
            audio.pause();
            icon.className = 'fas fa-play';
        }
    }

    // New function to handle audio seeking
    function seekAudio(event, progressBar) {
        const audio = progressBar.closest('.audio-message').querySelector('audio');
        const rect = progressBar.getBoundingClientRect();
        const pos = (event.clientX - rect.left) / rect.width;
        audio.currentTime = pos * audio.duration;
        event.stopPropagation();
    }

    // Utility function to format time
    function formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }