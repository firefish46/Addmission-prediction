document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('prediction-form');
    const output = document.getElementById('prediction-output');
    const message = document.getElementById('result-message');
    const statusBar = document.getElementById('status-bar');
    const spinner = document.getElementById('loading-spinner');
    const button = document.getElementById('predict-btn');
    const researchToggle = document.getElementById('research_toggle');

    // CRITICAL CHECK: Ensure all required elements are found before proceeding.
    if (!output || !message || !statusBar || !spinner || !button || !researchToggle) {
        console.error("Initialization Error: One or more required UI elements (output, message, statusBar, spinner, button, researchToggle) are missing from index.html. Please ensure all required IDs are present.");
        return; // Stop script execution if UI is incomplete
    }

    // --- NEW: Slider Event Listeners for Range Inputs ---
    const sliderIds = ['gre_score', 'toefl_score', 'sop', 'lor', 'cgpa'];
    sliderIds.forEach(id => {
        const slider = document.getElementById(id);
        const valueSpan = document.getElementById(`${id}_value`);
        if (slider && valueSpan) {
            
            // Function to format the value (2 decimals for CGPA, SOP, LOR)
            const updateValue = () => {
                const step = parseFloat(slider.getAttribute('step'));
                let value = parseFloat(slider.value);
                
                // Format with 2 decimals if step is less than 1 (e.g., 0.5 or 0.01)
                const formattedValue = step < 1 ? value.toFixed(2) : value;
                valueSpan.textContent = formattedValue;
            };

            // Update on initial load
            updateValue(); 
            
            // Update on drag/change
            slider.addEventListener('input', updateValue);
        }
    });
    // --- END NEW: Slider Event Listeners ---


    // Helper function to update the status bar color and message based on chance
    function updateResultDisplay(chance) {
        let color, statusText;

        if (chance >= 0.8) {
            color = 'var(--success-color)';
            statusText = 'Excellent Chance! Your profile is highly competitive.';
        } else if (chance >= 0.6) {
            color = 'var(--primary-color)';
            statusText = 'Good Chance. Strong application required.';
        } else if (chance >= 0.4) {
            color = 'var(--secondary-color)';
            statusText = 'Moderate Chance. Focus on strengthening areas.';
        } else {
            color = 'var(--error-color)';
            statusText = 'Lower Chance. Consider improvements or backup options.';
        }

        // --- Convert to Percentage ---
        const percentageValue = chance * 100;
        const percentage = Math.min(100, Math.round(percentageValue)); 
        
        // Update the status bar width and color
        document.documentElement.style.setProperty('--status-bar-width', `${percentage}%`);
        statusBar.style.backgroundColor = color; 

        // --- Display with % sign, rounded to 2 decimal places ---
        output.textContent = percentageValue.toFixed(2) + '%';
        
        message.textContent = statusText;
        output.style.color = color;
    }
    
    // Function to handle the form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Show loading state
        spinner.style.display = 'block';
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Calculating...';

        // 1. Collect Data
        const formData = new FormData(form);
        const data = {
            'Research': researchToggle.checked ? 1 : 0 
        };
        
        // Collect other numerical inputs
        formData.forEach((value, key) => {
             // We skip 'research' here because we already set its value (0 or 1) correctly above.
             if (key !== 'research') { 
                 data[key] = parseFloat(value);
             }
        });
        
        // 2. Send Data to Flask API
        try {
            const response = await fetch('/predict_api', { // Assuming you use the /predict_api endpoint
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            // 3. Handle Result
            if (response.ok) {
                const predictedChance = result.predicted_chance;
                updateResultDisplay(predictedChance);
            } else {
                message.textContent = `Error: ${result.error || 'Prediction failed.'}`;
                output.textContent = 'N/A';
                output.style.color = 'var(--error-color)';
            }

        } catch (error) {
            console.error('Fetch error:', error);
            message.textContent = 'A network error occurred. Please try again.';
            output.textContent = 'Error';
            output.style.color = 'var(--error-color)';
        } finally {
            // Hide loading state
            spinner.style.display = 'none';
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-arrow-right"></i> Calculate Chance';
        }
    });

    // Initial setup of the status bar (using the CSS variable approach)
    document.documentElement.style.setProperty('--status-bar-width', `0%`);
});
