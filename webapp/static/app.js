// webapp/static/app.js
class FarmerAssistant {
    constructor() {
        this.selectedImageData = null;
        this.currentSessionId = null;
        this.managerThoughtsInterval = null;
        this.currentMode = 'disease'; // 'disease' or 'schemes'
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.recordedAudioData = null;

        this.initializeEventListeners();
        this.checkHealth();
    }

    initializeEventListeners() {
        // Mode selection buttons
        document.getElementById('diseaseMode').addEventListener('click', () => {
            this.switchMode('disease');
        });

        document.getElementById('schemesMode').addEventListener('click', () => {
            this.switchMode('schemes');
        });

        document.getElementById('talkMode').addEventListener('click', () => {
            this.switchMode('talk');
        });

        // Disease detection listeners
        document.getElementById('imageInput').addEventListener('change', (e) => {
            this.handleImageSelection(e);
        });

        document.getElementById('analyzeBtn').addEventListener('click', () => {
            this.analyzeImage();
        });

        // Government schemes listeners
        document.getElementById('querySchemeBtn').addEventListener('click', () => {
            this.queryGovernmentSchemes();
        });

        document.getElementById('schemeQueryInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.queryGovernmentSchemes();
            }
        });

        // Example chip listeners
        document.querySelectorAll('.example-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                const query = chip.getAttribute('data-query');
                document.getElementById('schemeQueryInput').value = query;
            });
        });

        // Talk Now listeners
        document.getElementById('recordBtn').addEventListener('click', () => {
            this.startRecording();
        });

        document.getElementById('stopBtn').addEventListener('click', () => {
            this.stopRecording();
        });

        document.getElementById('transcribeBtn').addEventListener('click', () => {
            this.transcribeAudio();
        });

        // Retry button
        document.getElementById('retryBtn').addEventListener('click', () => {
            this.resetInterface();
        });
    }

    switchMode(mode) {
        this.currentMode = mode;
        this.resetInterface();

        // Update UI
        document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.mode-section').forEach(section => section.classList.remove('active'));

        if (mode === 'disease') {
            document.getElementById('diseaseMode').classList.add('active');
            document.getElementById('diseaseSection').classList.add('active');
        } else if (mode === 'schemes') {
            document.getElementById('schemesMode').classList.add('active');
            document.getElementById('schemesSection').classList.add('active');
        } else if (mode === 'talk') {
            document.getElementById('talkMode').classList.add('active');
            document.getElementById('talkSection').classList.add('active');
        }
    }

    async checkHealth() {
        try {
            const response = await fetch('/health');
            const health = await response.json();

            if (health.status === 'healthy') {
                console.log('✅ System healthy');
            } else {
                console.warn('⚠️ System health issues:', health);
            }
        } catch (error) {
            console.error('❌ Health check failed:', error);
        }
    }

    handleImageSelection(event) {
        const file = event.target.files[0];

        if (!file) {
            this.selectedImageData = null;
            document.getElementById('analyzeBtn').disabled = true;
            return;
        }

        // Validate file type
        if (!file.type.startsWith('image/')) {
            alert('Please select a valid image file.');
            return;
        }

        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            alert('Image size should be less than 5MB.');
            return;
        }

        // Convert to base64
        const reader = new FileReader();
        reader.onload = (e) => {
            // Remove data URL prefix to get pure base64
            this.selectedImageData = e.target.result.split(',')[1];
            document.getElementById('analyzeBtn').disabled = false;

            console.log('✅ Image selected and converted to base64');
        };

        reader.onerror = () => {
            alert('Error reading image file.');
            this.selectedImageData = null;
            document.getElementById('analyzeBtn').disabled = true;
        };

        reader.readAsDataURL(file);
    }

    async analyzeImage() {
        if (!this.selectedImageData) {
            alert('Please select an image first.');
            return;
        }

        this.showLoading('Analyzing your crop image...');

        try {
            const textDescription = document.getElementById('textInput').value.trim();

            const requestData = {
                inputType: 'image',
                content: this.selectedImageData,
                userId: this.getUserId(),
                language: 'en',
                textDescription: textDescription
            };

            console.log('📤 Sending analysis request...');

            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();

            if (response.ok) {
                console.log('✅ Analysis successful:', result);
                this.currentSessionId = result.session_id;
                this.displayResults(result, 'Disease Analysis Results');
            } else {
                console.error('❌ Analysis failed:', result);
                this.showError(result.error || 'Analysis failed');
            }

        } catch (error) {
            console.error('❌ Request failed:', error);
            this.showError('Network error. Please check your connection and try again.');
        }
    }

    async queryGovernmentSchemes() {
        const queryText = document.getElementById('schemeQueryInput').value.trim();

        if (!queryText) {
            alert('Please enter your question about government schemes.');
            return;
        }

        this.showLoading('Searching government schemes database...');

        try {
            const requestData = {
                inputType: 'text',
                content: queryText,
                userId: this.getUserId(),
                language: 'en',
                queryType: 'government_schemes'
            };

            console.log('📤 Sending schemes query request...');

            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();

            if (response.ok) {
                console.log('✅ Schemes query successful:', result);
                this.currentSessionId = result.session_id;
                this.displayResults(result, 'Government Schemes Information');
            } else {
                console.error('❌ Schemes query failed:', result);
                this.showError(result.error || 'Query failed');
            }

        } catch (error) {
            console.error('❌ Request failed:', error);
            this.showError('Network error. Please check your connection and try again.');
        }
    }

    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];

            this.mediaRecorder.addEventListener('dataavailable', (event) => {
                this.audioChunks.push(event.data);
            });

            this.mediaRecorder.addEventListener('stop', () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                this.convertAudioToBase64(audioBlob);
            });

            this.mediaRecorder.start();

            document.getElementById('recordBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            document.getElementById('recordingStatus').textContent = '🔴 Recording...';
            document.getElementById('recordingStatus').className = 'recording-status recording';

            console.log('✅ Recording started');

        } catch (error) {
            console.error('❌ Recording failed:', error);
            alert('Unable to access microphone. Please check permissions.');
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
            this.mediaRecorder.stop();

            // Stop all tracks
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());

            document.getElementById('recordBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('recordingStatus').textContent = '✅ Recording complete! Ready to transcribe.';
            document.getElementById('recordingStatus').className = 'recording-status ready';

            console.log('✅ Recording stopped');
        }
    }

    convertAudioToBase64(audioBlob) {
        const reader = new FileReader();
        reader.onload = () => {
            // Remove data URL prefix to get pure base64
            this.recordedAudioData = reader.result.split(',')[1];
            document.getElementById('transcribeBtn').disabled = false;
            console.log('✅ Audio converted to base64');
        };
        reader.readAsDataURL(audioBlob);
    }

    async transcribeAudio() {
        if (!this.recordedAudioData) {
            alert('Please record audio first.');
            return;
        }

        this.showLoading('Transcribing your audio...');

        try {
            const selectedLanguage = document.getElementById('languageSelect').value;

            const requestData = {
                inputType: 'audio',
                content: this.recordedAudioData,
                userId: this.getUserId(),
                language: selectedLanguage
            };

            console.log('📤 Sending transcription request...');

            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();

            if (response.ok) {
                console.log('✅ Transcription successful:', result);
                this.currentSessionId = result.session_id;
                this.displayResults(result, 'Audio Transcription Results');
            } else {
                console.error('❌ Transcription failed:', result);
                this.showError(result.error || 'Transcription failed');
            }

        } catch (error) {
            console.error('❌ Request failed:', error);
            this.showError('Network error. Please check your connection and try again.');
        }
    }

    showLoading(message = 'Processing your request...') {
        document.getElementById('loadingSection').style.display = 'block';
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('errorSection').style.display = 'none';

        document.getElementById('loadingText').textContent = message;

        // Show appropriate manager thoughts
        if (this.currentMode === 'disease') {
            this.startDiseaseAnalysisThoughts();
        } else {
            this.startSchemesQueryThoughts();
        }
    }

    startDiseaseAnalysisThoughts() {
        const thoughts = [
            "🤔 Analyzing your crop image...",
            "🎯 Identifying potential issues...",
            "🔬 Calling disease detection specialist...",
            "✅ Analysis complete! Preparing response..."
        ];

        this.displayThoughts(thoughts);
    }

    startSchemesQueryThoughts() {
        const thoughts = [
            "🤔 Understanding your query...",
            "🔍 Searching government schemes database...",
            "📊 Finding relevant schemes and policies...",
            "✅ Query complete! Preparing information..."
        ];

        this.displayThoughts(thoughts);
    }

    displayThoughts(thoughts) {
        const thoughtsContainer = document.getElementById('managerThoughts');
        thoughtsContainer.innerHTML = '';

        thoughts.forEach((thought, index) => {
            setTimeout(() => {
                const bubble = document.createElement('div');
                bubble.className = 'thought-bubble';
                bubble.textContent = thought;
                thoughtsContainer.appendChild(bubble);
            }, index * 2000);
        });
    }

    displayResults(result, title) {
        document.getElementById('loadingSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'block';
        document.getElementById('errorSection').style.display = 'none';

        document.getElementById('resultsTitle').textContent = title;
        const resultsContainer = document.getElementById('analysisResults');

        // Store result for debugging
        this.lastResult = result;

        let htmlContent = '';

        if (this.currentMode === 'disease' && result.agent_response && result.agent_response.analysis) {
            htmlContent = this.createDiseaseAnalysisHTML(result.agent_response.analysis);
        } else if (this.currentMode === 'schemes' && result.agent_response) {
            htmlContent = this.createSchemesResponseHTML(result.agent_response);
        } else if (this.currentMode === 'talk' && result.agent_response) {
            htmlContent = this.createTranscriptionHTML(result.agent_response);
        } else {
            htmlContent = this.createSimpleResponseHTML(result);
        }

        // Add debug panel
        htmlContent += this.createDebugPanel(result);

        resultsContainer.innerHTML = htmlContent;
    }

    createDiseaseAnalysisHTML(analysis) {
        const confidenceClass = `confidence-${analysis.confidence}`;

        return `
            <div class="disease-card">
                <div class="disease-header">
                    <div class="disease-name">${analysis.disease_name}</div>
                    <div class="confidence-badge ${confidenceClass}">${analysis.confidence} confidence</div>
                </div>
                
                ${analysis.severity !== 'none' ? `
                    <div class="analysis-section">
                        <h4>🚨 Severity: ${analysis.severity}</h4>
                    </div>
                ` : ''}
                
                ${analysis.symptoms_observed.length > 0 ? `
                    <div class="analysis-section">
                        <h4>👀 Symptoms Observed:</h4>
                        <ul>
                            ${analysis.symptoms_observed.map(symptom => `<li>${symptom}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                <div class="analysis-section">
                    <h4>⚡ Immediate Action:</h4>
                    <div class="treatment-card">
                        ${analysis.immediate_action}
                    </div>
                </div>
                
                <div class="analysis-section">
                    <h4>💊 Treatment Summary:</h4>
                    <p>${analysis.treatment_summary}</p>
                </div>
                
                ${analysis.organic_solutions.length > 0 ? `
                    <div class="analysis-section">
                        <h4>🌿 Organic Solutions:</h4>
                        ${analysis.organic_solutions.map(solution => `
                            <div class="treatment-card">
                                <strong>${solution.name}</strong><br>
                                <em>Preparation:</em> ${solution.preparation}<br>
                                <em>Application:</em> ${solution.application}
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${analysis.prevention_tips.length > 0 ? `
                    <div class="analysis-section">
                        <h4>🛡️ Prevention Tips:</h4>
                        <ul>
                            ${analysis.prevention_tips.map(tip => `<li>${tip}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                <div class="analysis-section">
                    <h4>💰 Cost Estimate:</h4>
                    <div class="cost-estimate">${analysis.cost_estimate}</div>
                </div>
                
                <div class="analysis-section">
                    <h4>⏱️ Expected Timeline:</h4>
                    <p>${analysis.success_timeline}</p>
                </div>
                
                <div class="analysis-section">
                    <h4>⚠️ Warning Signs:</h4>
                    <p style="color: #d32f2f; font-weight: bold;">${analysis.warning_signs}</p>
                </div>
            </div>
        `;
    }

    createSchemesResponseHTML(agentResponse) {
        return `
            <div class="schemes-card">
                <div class="schemes-header">
                    <div class="schemes-title">Government Schemes Information</div>
                    ${agentResponse.confidence ? `
                        <div class="confidence-badge confidence-${agentResponse.confidence}">${agentResponse.confidence} relevance</div>
                    ` : ''}
                </div>
                
                <div class="schemes-content">
                    ${agentResponse.message ? `
                        <div class="schemes-section">
                            <div class="schemes-text">${this.formatText(agentResponse.message)}</div>
                        </div>
                    ` : ''}
                    
                    ${agentResponse.schemes && agentResponse.schemes.length > 0 ? `
                        <div class="schemes-section">
                            <h4>📋 Relevant Schemes:</h4>
                            ${agentResponse.schemes.map(scheme => `
                                <div class="scheme-item">
                                    <h5>${scheme.name}</h5>
                                    <p><strong>Description:</strong> ${scheme.description}</p>
                                    ${scheme.eligibility ? `<p><strong>Eligibility:</strong> ${scheme.eligibility}</p>` : ''}
                                    ${scheme.benefits ? `<p><strong>Benefits:</strong> ${scheme.benefits}</p>` : ''}
                                    ${scheme.application_process ? `<p><strong>How to Apply:</strong> ${scheme.application_process}</p>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                    
                    ${agentResponse.sources && agentResponse.sources.length > 0 ? `
                        <div class="schemes-section">
                            <h4>📚 Sources:</h4>
                            <ul class="sources-list">
                                ${agentResponse.sources.map(source => `<li>${source}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    createTranscriptionHTML(agentResponse) {
        const success = agentResponse.success;
        const transcript = agentResponse.transcript || '';
        const confidence = agentResponse.confidence || 0;

        return `
        <div class="transcription-card">
            <div class="transcription-header">
                <div class="transcription-title">Audio Transcription</div>
                ${confidence > 0 ? `
                    <div class="confidence-badge confidence-${confidence > 0.8 ? 'high' : confidence > 0.5 ? 'medium' : 'low'}">
                        ${Math.round(confidence * 100)}% confidence
                    </div>
                ` : ''}
            </div>
            
            ${success ? `
                <div class="transcription-content">
                    <div class="transcript-text">
                        <h4>📝 Transcribed Text:</h4>
                        <div class="transcript-box">${transcript}</div>
                    </div>
                    
                    <div class="transcript-actions">
                        <button class="btn btn-primary" onclick="navigator.clipboard.writeText('${transcript.replace(/'/g, "\\'")}')">
                            📋 Copy Text
                        </button>
                    </div>
                </div>
            ` : `
                <div class="transcription-error">
                    <h4>❌ Transcription Failed:</h4>
                    <p>${agentResponse.error || 'Unknown error occurred'}</p>
                </div>
            `}
        </div>
    `;
    }

    createSimpleResponseHTML(result) {
        return `
            <div class="response-card">
                <div class="analysis-section">
                    <h4>Response:</h4>
                    <p>${result.final_response?.message || result.message || 'Request processed'}</p>
                </div>
                
                ${result.classification ? `
                    <div class="analysis-section">
                        <h4>Classification:</h4>
                        <p><strong>Intent:</strong> ${result.classification.intent}</p>
                        <p><strong>Confidence:</strong> ${result.classification.confidence}</p>
                        <p><strong>Reasoning:</strong> ${result.classification.reasoning}</p>
                    </div>
                ` : ''}
            </div>
        `;
    }

    formatText(text) {
        // Simple text formatting - convert line breaks to <br> and bold **text**
        return text
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }

    showError(message) {
        document.getElementById('loadingSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('errorSection').style.display = 'block';

        document.getElementById('errorMessage').textContent = message;
    }

    resetInterface() {
        document.getElementById('loadingSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('errorSection').style.display = 'none';

        // Reset forms
        if (this.currentMode === 'disease') {
            document.getElementById('imageInput').value = '';
            document.getElementById('textInput').value = '';
            document.getElementById('analyzeBtn').disabled = true;
            this.selectedImageData = null;
        } else if (this.currentMode === 'schemes') {
            document.getElementById('schemeQueryInput').value = '';
        } else if (this.currentMode === 'talk') {
            document.getElementById('recordBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('transcribeBtn').disabled = true;
            document.getElementById('recordingStatus').textContent = '';
            document.getElementById('recordingStatus').className = 'recording-status';
            this.recordedAudioData = null;
        }

        this.currentSessionId = null;
    }

    getUserId() {
        // Simple user ID generation for MVP
        let userId = localStorage.getItem('farmerAssistantUserId');
        if (!userId) {
            userId = 'user_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('farmerAssistantUserId', userId);
        }
        return userId;
    }

    createDebugPanel(result) {
        return `
            <div class="debug-panel">
                <button class="debug-toggle" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'block' : 'none'">
                    🔍 Show Debug Info
                </button>
                <div class="debug-content" style="display: none;">
                    <strong>Full Response:</strong>
                    <pre>${JSON.stringify(result, null, 2)}</pre>
                </div>
            </div>
        `;
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    new FarmerAssistant();
});