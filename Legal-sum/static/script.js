// API base URL
const API_URL = '/api';

// DOM elements
const searchBtn = document.getElementById('searchBtn');
const caseStudyInput = document.getElementById('caseStudy');
const resultsSection = document.getElementById('resultsSection');
const resultsContainer = document.getElementById('resultsContainer');
const loadingIndicator = document.getElementById('loadingIndicator');
const summarySection = document.getElementById('summarySection');
const summaryBox = document.getElementById('summaryBox');
const aiAnalysisSection = document.getElementById('aiAnalysisSection');
const aiAnalysisContainer = document.getElementById('aiAnalysisContainer');

// Toggle between text and PDF input
document.querySelectorAll('.input-mode-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const mode = this.dataset.mode;
        document.querySelectorAll('.input-mode-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        
        const textSection = document.getElementById('textInputSection');
        const pdfSection = document.getElementById('pdfInputSection');
        
        if (mode === 'pdf') {
            textSection.style.display = 'none';
            pdfSection.style.display = 'block';
            caseStudyInput.value = '';
        } else {
            textSection.style.display = 'block';
            pdfSection.style.display = 'none';
            document.getElementById('pdfFile').value = '';
        }
    });
});

// Search for similar cases
searchBtn.addEventListener('click', async () => {
    const isPdfMode = document.getElementById('pdfInputSection').style.display !== 'none';
    
    if (isPdfMode) {
        const pdfFile = document.getElementById('pdfFile').files[0];
        if (!pdfFile) {
            showMessage('Please select a PDF file', 'error');
            return;
        }
        await handlePdfSearch(pdfFile);
    } else {
        const caseStudy = caseStudyInput.value.trim();
        if (!caseStudy) {
            showMessage('Please enter a case study', 'error');
            return;
        }
        await handleTextSearch(caseStudy);
    }
});

// Handle text search
async function handleTextSearch(caseStudy) {
    try {
        showLoading('Searching for similar cases...');
        resultsSection.style.display = 'none';
        
        const response = await fetch(`${API_URL}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ case_study: caseStudy })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displaySummary(data.summarized_input);
            displayResults(data.results);
            displayAIAnalysis(data.ai_analysis);
        } else {
            showMessage(data.error || 'Failed to search cases', 'error');
        }
    } catch (error) {
        showMessage('Error searching: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Handle PDF search
async function handlePdfSearch(file) {
    const formData = new FormData();
    formData.append('pdf', file);
    
    try {
        showLoading('Processing PDF and searching for similar cases...');
        resultsSection.style.display = 'none';
        
        const response = await fetch(`${API_URL}/search-pdf`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displaySummary(data.summarized_input);
            displayResults(data.results);
            displayAIAnalysis(data.ai_analysis);
        } else {
            showMessage(data.error || 'Failed to process PDF', 'error');
        }
    } catch (error) {
        showMessage('Error processing PDF: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Display summary with clean, readable formatting
function displaySummary(summarizedText) {
    if (summarizedText && summarizedText.trim()) {
        const summaryBox = document.getElementById('summaryBox');
        
        // Split into sentences for better display
        const sentences = summarizedText.match(/[^.!?]+[.!?]+/g) || [summarizedText];
        
        // Create clean, readable summary without stats
        let summaryHTML = '<div class="summary-text">';
        sentences.forEach((sentence, idx) => {
            const cleanSentence = sentence.trim();
            summaryHTML += `<p class="summary-sentence">${cleanSentence}</p>`;
        });
        summaryHTML += '</div>';
        
        summaryBox.innerHTML = summaryHTML;
        summarySection.style.display = 'block';
    } else {
        summarySection.style.display = 'none';
    }
}

// Display AI Analysis
function displayAIAnalysis(aiData) {
    if (!aiData) {
        aiAnalysisSection.style.display = 'none';
        return;
    }
    
    if (!aiData.available) {
        // AI analysis not available (no API key or error)
        aiAnalysisSection.style.display = 'none';
        return;
    }
    
    const analysis = aiData.analysis;
    
    let html = '';
    
    // Verdict Prediction Section
    if (analysis.verdict_prediction) {
        const verdict = analysis.verdict_prediction.toLowerCase();
        const verdictClass = verdict === 'win' ? 'verdict-win' : verdict === 'loss' ? 'verdict-loss' : 'verdict-draw';
        const confidence = analysis.confidence_level || 'medium';
        
        html += `
            <div class="ai-verdict-box ${verdictClass}">
                <div class="verdict-header">
                    <h3>📊 Predicted Verdict</h3>
                    <span class="confidence-badge confidence-${confidence}">${confidence.toUpperCase()} CONFIDENCE</span>
                </div>
                <div class="verdict-result">
                    <strong>${analysis.verdict_prediction.toUpperCase()}</strong>
                </div>
                ${analysis.win_probability_plaintiff !== undefined ? `
                    <div class="probability-bars">
                        <div class="prob-bar">
                            <label>Plaintiff Win Probability:</label>
                            <div class="prob-fill" style="width: ${analysis.win_probability_plaintiff}%">
                                ${analysis.win_probability_plaintiff}%
                            </div>
                        </div>
                        <div class="prob-bar">
                            <label>Defendant Win Probability:</label>
                            <div class="prob-fill" style="width: ${analysis.win_probability_defendant}%">
                                ${analysis.win_probability_defendant}%
                            </div>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    // Analysis Details
    html += '<div class="ai-analysis-details">';
    
    if (analysis.legal_issues && Array.isArray(analysis.legal_issues)) {
        html += `
            <div class="analysis-card">
                <h4>🔍 Key Legal Issues</h4>
                <ul>${analysis.legal_issues.map(issue => `<li>${issue}</li>`).join('')}</ul>
            </div>
        `;
    }
    
    if (analysis.applicable_laws && Array.isArray(analysis.applicable_laws)) {
        html += `
            <div class="analysis-card">
                <h4>⚖️ Applicable Laws & Acts</h4>
                <ul>${analysis.applicable_laws.map(law => `<li>${law}</li>`).join('')}</ul>
            </div>
        `;
    }
    
    if (analysis.plaintiff_strengths && Array.isArray(analysis.plaintiff_strengths)) {
        html += `
            <div class="analysis-card">
                <h4>💪 Plaintiff Strengths</h4>
                <ul>${analysis.plaintiff_strengths.map(strength => `<li>${strength}</li>`).join('')}</ul>
            </div>
        `;
    }
    
    if (analysis.plaintiff_weaknesses && Array.isArray(analysis.plaintiff_weaknesses)) {
        html += `
            <div class="analysis-card">
                <h4>⚠️ Plaintiff Weaknesses</h4>
                <ul>${analysis.plaintiff_weaknesses.map(weakness => `<li>${weakness}</li>`).join('')}</ul>
            </div>
        `;
    }
    
    if (analysis.reasoning) {
        html += `
            <div class="analysis-card">
                <h4>🧠 Detailed Reasoning</h4>
                <p>${analysis.reasoning}</p>
            </div>
        `;
    }
    
    if (analysis.recommended_legal_strategy) {
        html += `
            <div class="analysis-card strategy-card">
                <h4>📋 Recommended Legal Strategy</h4>
                <p>${analysis.recommended_legal_strategy}</p>
            </div>
        `;
    }
    
    html += '</div>';
    
    aiAnalysisContainer.innerHTML = html;
    aiAnalysisSection.style.display = 'block';
}

// Display search results
function displayResults(results) {
    resultsContainer.innerHTML = '';
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<div class="result-card"><p>No similar cases found.</p></div>';
    } else {
        results.forEach((result, index) => {
            const card = document.createElement('div');
            card.className = 'result-card';
            
            const html = `
                <div class="result-header">
                    <div class="case-name">${index + 1}. ${result.case_name}</div>
                    <div class="similarity-score">${result.similarity_score}% Match</div>
                </div>
                <div class="result-footer">
                    <span class="filename">File: ${result.filename}</span>
                    <button class="btn-open-pdf" onclick="openPDF('${result.filename}')">📄 Open PDF</button>
                </div>
            `;
            
            card.innerHTML = html;
            resultsContainer.appendChild(card);
        });
    }
    
    resultsSection.style.display = 'block';
}

// Open PDF file
function openPDF(filename) {
    // Encode filename for URL
    const encodedFilename = encodeURIComponent(filename);
    const pdfUrl = `/pdf/${encodedFilename}`;
    
    // Open PDF in new tab
    window.open(pdfUrl, '_blank');
}

// Show loading indicator
function showLoading(message) {
    loadingIndicator.querySelector('p').textContent = message || 'Processing...';
    loadingIndicator.style.display = 'block';
}

// Hide loading indicator
function hideLoading() {
    loadingIndicator.style.display = 'none';
}

// Show message
function showMessage(message, type) {
    // Remove existing messages
    const existingMsg = document.querySelector('.error, .success');
    if (existingMsg) {
        existingMsg.remove();
    }
    
    const msgDiv = document.createElement('div');
    msgDiv.className = type;
    msgDiv.textContent = message;
    
    const mainContent = document.querySelector('.main-content');
    mainContent.insertBefore(msgDiv, mainContent.firstChild);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        msgDiv.remove();
    }, 5000);
}

