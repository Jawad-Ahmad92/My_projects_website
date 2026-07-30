document.addEventListener('DOMContentLoaded', () => {
    const predictForm = document.getElementById('interactive-predict-form');
    const loadingBox = document.getElementById('predict-loading');
    const resultBox = document.getElementById('predict-result');
    const resultValue = document.getElementById('result-value');
    const probabilityWrapper = document.getElementById('probability-wrapper');
    const probabilityLabels = document.getElementById('probability-labels');
    const probabilityBar = document.getElementById('probability-bar');
    
    if (predictForm) {
        predictForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Hide previous results
            resultBox.style.display = 'none';
            probabilityWrapper.style.display = 'none';
            
            // Show loading animation
            loadingBox.style.display = 'block';
            
            const formData = new FormData(predictForm);
            const slug = predictForm.getAttribute('data-slug');
            
            try {
                const response = await fetch(`/project/${slug}/predict`, {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                loadingBox.style.display = 'none';
                
                if (response.ok && result.success) {
                    resultBox.style.display = 'block';
                    
                    let predVal = result.prediction;
                    
                    // Format prediction output based on value
                    if (typeof predVal === 'number' && !result.is_classification) {
                        // Regression (e.g. house price)
                        resultValue.innerHTML = `<span style="color: var(--primary)">$${predVal.toLocaleString(undefined, {maximumFractionDigits: 2})}</span>`;
                        resultValue.style.color = 'var(--primary)';
                    } else {
                        // Classification (e.g. Heart Disease, Diabetes)
                        if (predVal === 1 || String(predVal).toLowerCase() === 'yes' || String(predVal).toLowerCase() === 'positive') {
                            resultValue.textContent = "Positive Result (Risk Detected)";
                            resultValue.style.color = 'var(--danger)';
                        } else if (predVal === 0 || String(predVal).toLowerCase() === 'no' || String(predVal).toLowerCase() === 'negative') {
                            resultValue.textContent = "Negative Result (No Risk)";
                            resultValue.style.color = 'var(--success)';
                        } else {
                            resultValue.textContent = predVal;
                            resultValue.style.color = 'var(--success)';
                        }
                        
                        // Handle classification probabilities
                        if (result.probabilities && result.probabilities.length >= 2) {
                            probabilityWrapper.style.display = 'block';
                            
                            // Assuming binary classification (index 1 is positive class probability)
                            const posProbability = (result.probabilities[1] * 100).toFixed(1);
                            const negProbability = (result.probabilities[0] * 100).toFixed(1);
                            
                            probabilityLabels.innerHTML = `
                                <span>Healthy (Negative): ${negProbability}%</span>
                                <span>At Risk (Positive): ${posProbability}%</span>
                            `;
                            
                            probabilityBar.style.width = `${posProbability}%`;
                            
                            // Color bar based on positive probability severity
                            if (posProbability > 70) {
                                probabilityBar.style.background = 'linear-gradient(90deg, var(--secondary), var(--danger))';
                            } else if (posProbability > 40) {
                                probabilityBar.style.background = 'linear-gradient(90deg, var(--secondary), var(--warning))';
                            } else {
                                probabilityBar.style.background = 'linear-gradient(90deg, var(--secondary), var(--success))';
                            }
                        }
                    }
                } else {
                    resultBox.style.display = 'block';
                    resultValue.textContent = `Error: ${result.error || 'Prediction failed'}`;
                    resultValue.style.color = 'var(--danger)';
                }
            } catch (err) {
                loadingBox.style.display = 'none';
                resultBox.style.display = 'block';
                resultValue.textContent = 'Connection error. Prediction backend is unavailable.';
                resultValue.style.color = 'var(--danger)';
            }
        });
    }
});
