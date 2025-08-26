// Twitter Space AI Assistant - Frontend JavaScript

class TwitterSpaceAssistant {
    constructor() {
        this.isListening = false;
        this.websocket = null;
        this.rollingBuffer = [];
        this.allTranscripts = [];
        this.rollingBufferLimit = 12;
        this.recordDuration = 5;
        
        this.initializeElements();
        this.bindEvents();
    }

    initializeElements() {
        this.topicInput = document.getElementById('topic');
        this.clearDataBtn = document.getElementById('clearData');
        this.pdfUpload = document.getElementById('pdfUpload');
        this.customPrompt = document.getElementById('customPrompt');
        this.startButton = document.getElementById('startButton');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.transcriptDisplay = document.getElementById('transcriptDisplay');
        this.transcriptContent = document.getElementById('transcriptContent');
        this.questionsDisplay = document.getElementById('questionsDisplay');
        this.questionsContent = document.getElementById('questionsContent');
    }

    bindEvents() {
        this.startButton.addEventListener('click', () => this.toggleListening());
        this.clearDataBtn.addEventListener('click', () => this.clearData());
        this.pdfUpload.addEventListener('change', (e) => this.handlePdfUpload(e));
    }

    async toggleListening() {
        if (this.isListening) {
            this.stopListening();
        } else {
            await this.startListening();
        }
    }

    async startListening() {
        try {
            // Check if browser supports WebRTC
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('WebRTC is not supported in this browser');
            }

            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            this.isListening = true;
            this.updateUI();
            this.startAudioProcessing(stream);
            
        } catch (error) {
            console.error('Error starting audio recording:', error);
            this.showNotification('Error: Could not access microphone. Please check permissions.', 'error');
        }
    }

    stopListening() {
        this.isListening = false;
        this.updateUI();
        
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        // Stop all audio tracks
        if (this.audioStream) {
            this.audioStream.getTracks().forEach(track => track.stop());
            this.audioStream = null;
        }
    }

    startAudioProcessing(stream) {
        this.audioStream = stream;
        
        // Create WebSocket connection to backend
        this.connectWebSocket();
        
        // Start audio recording loop
        this.recordAudioLoop();
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected');
            this.sendMessage({
                type: 'init',
                topic: this.topicInput.value,
                customPrompt: this.customPrompt.value
            });
        };
        
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showNotification('Connection error. Please try again.', 'error');
        };
        
        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
        };
    }

    async recordAudioLoop() {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioContext.createMediaStreamSource(this.audioStream);
        const processor = audioContext.createScriptProcessor(4096, 1, 1);
        
        let audioBuffer = [];
        const sampleRate = 16000;
        const bufferSize = sampleRate * this.recordDuration;
        
        processor.onaudioprocess = (event) => {
            const inputData = event.inputBuffer.getChannelData(0);
            
            // Convert to 16-bit PCM
            for (let i = 0; i < inputData.length; i++) {
                audioBuffer.push(Math.max(-1, Math.min(1, inputData[i])));
            }
            
            // Send audio data when buffer is full
            if (audioBuffer.length >= bufferSize) {
                const audioData = audioBuffer.slice(0, bufferSize);
                audioBuffer = audioBuffer.slice(bufferSize);
                
                this.sendAudioData(audioData);
            }
        };
        
        source.connect(processor);
        processor.connect(audioContext.destination);
        
        // Store references for cleanup
        this.audioContext = audioContext;
        this.audioProcessor = processor;
        this.audioSource = source;
    }

    sendAudioData(audioData) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: 'audio',
                data: audioData
            }));
        }
    }

    sendMessage(message) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(message));
        }
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'transcript':
                this.updateTranscript(data.text);
                break;
            case 'questions':
                this.updateQuestions(data.questions);
                break;
            case 'error':
                this.showNotification(data.message, 'error');
                break;
            case 'success':
                this.showNotification(data.message, 'success');
                break;
        }
    }

    updateTranscript(text) {
        if (text && text.trim()) {
            this.allTranscripts.push(text);
            this.rollingBuffer.push(text);
            
            if (this.rollingBuffer.length > this.rollingBufferLimit) {
                this.rollingBuffer.shift();
            }
            
            const joinedText = this.rollingBuffer.join(' ');
            this.transcriptContent.textContent = joinedText;
            this.transcriptDisplay.style.display = 'block';
        }
    }

    updateQuestions(questions) {
        if (questions) {
            this.questionsContent.innerHTML = this.formatQuestions(questions);
            this.questionsDisplay.style.display = 'block';
        }
    }

    formatQuestions(questions) {
        // Convert markdown-style questions to HTML
        return questions
            .split('\n')
            .filter(line => line.trim())
            .map(line => {
                if (line.match(/^\d+\./)) {
                    return `<div class="mb-2"><strong>${line}</strong></div>`;
                } else if (line.trim()) {
                    return `<div class="mb-2">${line}</div>`;
                }
                return '';
            })
            .join('');
    }

    async clearData() {
        const topic = this.topicInput.value;
        if (!topic) {
            this.showNotification('Please enter a topic first.', 'warning');
            return;
        }
        
        try {
            const response = await fetch('/clear-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ topic })
            });
            
            if (response.ok) {
                this.showNotification(`Namespace '${topic}' cleared successfully.`, 'success');
            } else {
                throw new Error('Failed to clear data');
            }
        } catch (error) {
            console.error('Error clearing data:', error);
            this.showNotification('Error clearing data. Please try again.', 'error');
        }
    }

    async handlePdfUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const formData = new FormData();
        formData.append('pdf', file);
        formData.append('topic', this.topicInput.value);
        
        try {
            const response = await fetch('/upload-pdf', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                this.showNotification('PDF uploaded and embedded successfully.', 'success');
            } else {
                throw new Error('Failed to upload PDF');
            }
        } catch (error) {
            console.error('Error uploading PDF:', error);
            this.showNotification('Error uploading PDF. Please try again.', 'error');
        }
    }

    updateUI() {
        if (this.isListening) {
            this.startButton.innerHTML = '<i class="fas fa-stop me-2"></i>Stop Listening';
            this.startButton.classList.remove('btn-primary');
            this.startButton.classList.add('btn-danger');
            this.statusIndicator.style.display = 'block';
        } else {
            this.startButton.innerHTML = '<i class="fas fa-microphone me-2"></i>Start Listening';
            this.startButton.classList.remove('btn-danger');
            this.startButton.classList.add('btn-primary');
            this.statusIndicator.style.display = 'none';
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    cleanup() {
        this.stopListening();
        
        if (this.audioProcessor) {
            this.audioProcessor.disconnect();
        }
        if (this.audioSource) {
            this.audioSource.disconnect();
        }
        if (this.audioContext) {
            this.audioContext.close();
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.twitterSpaceAssistant = new TwitterSpaceAssistant();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.twitterSpaceAssistant) {
        window.twitterSpaceAssistant.cleanup();
    }
}); 