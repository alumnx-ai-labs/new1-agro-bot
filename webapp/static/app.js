class FarmerAssistant {
    constructor() {
        this.selectedImageData = null;
        this.currentSessionId = null;
        this.managerThoughtsInterval = null;
        
        this.initializeEventListeners();
        this.checkHealth();
    }
    
    initializeEventListeners() {
        // Image input
        document.getElementById('imageInput').addEventListener('change', (e) => {
            this.handleImageSelection(e);
        });
        
        // Analyze button
        document.getElementById('analyzeBtn').addEventListener('click', () => {
            this.analyzeImage();
        });
        
        // Retry button
        document.getElementById('retryBtn').addEventListener('click', () => {
            this.resetInterface();
        });
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
        
        this.showLoading();
        
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
                this.displayResults(result);
            } else {
                console.error('❌ Analysis failed:', result);
                this.showError(result.error || 'Analysis failed');
            }
            
        } catch (error) {
            console.error('❌ Request failed:', error);
            this.showError('Network error. Please check your connection and try again.');
        }
    }
    
    showLoading() {
        document.getElementById('loadingSection').style.display = 'block';
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('errorSection').style.display = 'none';
        
        // Show manager thoughts
        this.startManagerThoughts();
    }
    
    startManagerThoughts() {
        const thoughts = [
            "🤔 Analyzing your crop image...",
            "🎯 Identifying potential issues...",
            "🔬 Calling disease detection specialist...",
            "✅ Analysis complete! Preparing response..."
        ];
        
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
    
    displayResults(result) {
        document.getElementById('loadingSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'block';
        document.getElementById('errorSection').style.display = 'none';
        
        const resultsContainer = document.getElementById('analysisResults');
        
        if (result.agent_response && result.agent_response.analysis) {
            resultsContainer.innerHTML = this.createDiseaseAnalysisHTML(result.agent_response.analysis);
        } else {
            resultsContainer.innerHTML = this.createSimpleResponseHTML(result);
        }
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
    
    createSimpleResponseHTML(result) {
        return `
            <div class="disease-card">
                <div class="analysis-section">
                    <h4>Response:</h4>
                    <p>${result.final_response?.message || 'Analysis completed'}</p>
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
        
        // Reset form
        document.getElementById('imageInput').value = '';
        document.getElementById('textInput').value = '';
        document.getElementById('analyzeBtn').disabled = true;
        
        this.selectedImageData = null;
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
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    new FarmerAssistant();
});