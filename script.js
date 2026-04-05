document.addEventListener("DOMContentLoaded", () => {
    loadHistory();
});

document.getElementById('symptom-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const loader = document.getElementById('loader');
    const placeholderText = document.getElementById('placeholder-text');
    const resultCard = document.getElementById('result-card');
    const predictedDisease = document.getElementById('predicted-disease');

    loader.style.display = 'block';
    placeholderText.style.display = 'none';
    resultCard.style.display = 'none';

    let selectedSymptoms = [];
    let displaySymptoms = []; // For the history UI

    const selects = document.querySelectorAll('.symptom-select');
    
    selects.forEach(select => {
        if (select.value !== "") {
            selectedSymptoms.push(select.value);
            // Get the clean text from the dropdown option
            displaySymptoms.push(select.options[select.selectedIndex].text); 
        }
    });

    if (selectedSymptoms.length === 0) {
        alert("Please select at least one symptom.");
        loader.style.display = 'none';
        placeholderText.style.display = 'block';
        return;
    }

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symptoms: selectedSymptoms })
        });

        const data = await response.json();

        setTimeout(() => {
            loader.style.display = 'none';

            if (data.success) {
                predictedDisease.innerText = data.disease;
                
                // --- NEW: Populate Recommendations ---
                const recList = document.getElementById('recommendations-list');
                const recBox = document.getElementById('recommendations-box');
                
                if (recList && recBox) {
                    recList.innerHTML = ''; // Clear old list
                    
                    if (data.recommendations && data.recommendations.length > 0) {
                        data.recommendations.forEach(rec => {
                            let li = document.createElement('li');
                            li.innerText = rec;
                            recList.appendChild(li);
                        });
                        recBox.style.display = 'block';
                    } else {
                        recBox.style.display = 'none';
                    }
                }

                resultCard.style.display = 'block';
                
                // Add to history
                saveToHistory(displaySymptoms, data.disease);
            } else {
                alert("Error: " + data.error);
                placeholderText.style.display = 'block';
            }
        }, 800);

    } catch (error) {
        console.error("Error:", error);
        loader.style.display = 'none';
        placeholderText.style.display = 'block';
        alert("Failed to connect to the prediction server.");
    }
});

// --- History Management Functions ---

function saveToHistory(symptoms, disease) {
    let history = JSON.parse(localStorage.getItem('healthHistory')) || [];
    
    const newEntry = {
        symptoms: symptoms.join(", "),
        disease: disease,
        date: new Date().toLocaleString()
    };

    // Add new entry to the top of the array
    history.unshift(newEntry);
    
    // Keep only the last 10 entries so it doesn't get too long
    if (history.length > 10) history.pop();

    localStorage.setItem('healthHistory', JSON.stringify(history));
    loadHistory(); // Refresh the UI
}

function loadHistory() {
    const historyList = document.getElementById('history-list');
    if (!historyList) return;

    let history = JSON.parse(localStorage.getItem('healthHistory')) || [];

    if (history.length === 0) {
        historyList.innerHTML = '<p class="empty-history">No past predictions yet.</p>';
        return;
    }

    historyList.innerHTML = ""; // Clear current list

    history.forEach(entry => {
        const item = document.createElement('div');
        item.className = 'history-item';
        
        item.innerHTML = `
            <div>
                <div class="history-symptoms"><strong>Symptoms:</strong> ${entry.symptoms}</div>
                <div class="history-date">${entry.date}</div>
            </div>
            <div class="history-disease">${entry.disease}</div>
        `;
        
        historyList.appendChild(item);
    });
}

const clearHistoryBtn = document.getElementById('clear-history');
if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener('click', () => {
        if(confirm("Are you sure you want to clear your prediction history?")) {
            localStorage.removeItem('healthHistory');
            loadHistory();
        }
    });
}