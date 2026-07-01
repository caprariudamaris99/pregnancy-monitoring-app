// Main JavaScript for Pregnancy Monitoring App

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips and popovers
    initializeBootstrapComponents();
    
    // Set up event listeners
    setupEventListeners();
    
    // Load charts if present
    loadCharts();

    // AI assistant widget
    initializeAiChat();
});

/**
 * Initialize Bootstrap components (tooltips, popovers)
 */
function initializeBootstrapComponents() {
    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Setup general event listeners
 */
function setupEventListeners() {
    // Dismiss alerts automatically after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Form validation
    setupFormValidation();
    
    // Dynamic form handling
    setupDynamicForms();
}

/**
 * Setup form validation
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!this.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            this.classList.add('was-validated');
        }, false);
    });
}

/**
 * Setup dynamic forms (e.g., show/hide fields based on selection)
 */
function setupDynamicForms() {
    // Symptom form - show/hide "other" field
    const symptomSelect = document.getElementById('symptom_type');
    if (symptomSelect) {
        symptomSelect.addEventListener('change', function() {
            const otherField = document.getElementById('otherSymptomDiv');
            if (otherField) {
                otherField.style.display = this.value === 'other' ? 'block' : 'none';
            }
        });
    }
}

/**
 * Load and render charts
 */
function loadCharts() {
    // Skip default placeholder charts when dashboard page provides its own chart data.
    if (document.querySelector('[data-dashboard-chart]')) {
        console.log('Skipping default chart initialization for dashboard page.');
        return;
    }

    // Weight Chart
    const weightCtx = document.getElementById('weightChart');
    if (weightCtx) {
        loadWeightChart(weightCtx);
    }
    
    // Blood Pressure Chart
    const bpCtx = document.getElementById('bpChart');
    if (bpCtx) {
        loadBPChart(bpCtx);
    }
    
    // Blood Glucose Chart
    const glucoseCtx = document.getElementById('glucoseChart');
    if (glucoseCtx) {
        loadGlucoseChart(glucoseCtx);
    }
}

function destroyExistingChart(ctx) {
    if (!ctx || typeof Chart === 'undefined') {
        return;
    }
    const existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy();
    }
}

/**
 * Load weight chart
 */
function loadWeightChart(ctx) {
    destroyExistingChart(ctx);
    const data = {
        labels: ['Săpt 1', 'Săpt 2', 'Săpt 3', 'Săpt 4', 'Săpt 5'],
        datasets: [{
            label: 'Greutate (kg)',
            data: [65, 66, 67, 68, 69],
            borderColor: '#28a745',
            backgroundColor: 'rgba(40, 167, 69, 0.1)',
            tension: 0.1,
            fill: true
        }]
    };
    
    new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Evoluția Greutății'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Load blood pressure chart
 */
function loadBPChart(ctx) {
    destroyExistingChart(ctx);
    const data = {
        labels: ['Măs 1', 'Măs 2', 'Măs 3', 'Măs 4', 'Măs 5'],
        datasets: [
            {
                label: 'Sistolă (mmHg)',
                data: [120, 118, 121, 119, 120],
                borderColor: '#dc3545',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                tension: 0.1
            },
            {
                label: 'Diastolă (mmHg)',
                data: [80, 79, 81, 78, 80],
                borderColor: '#17a2b8',
                backgroundColor: 'rgba(23, 162, 184, 0.1)',
                tension: 0.1
            }
        ]
    };
    
    new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Evoluția Tensiunii Arteriale'
                }
            }
        }
    });
}

/**
 * Load blood glucose chart
 */
function loadGlucoseChart(ctx) {
    destroyExistingChart(ctx);
    const data = {
        labels: ['Măs 1', 'Măs 2', 'Măs 3', 'Măs 4', 'Măs 5'],
        datasets: [{
            label: 'Glicemie (mg/dL)',
            data: [100, 102, 98, 105, 100],
            borderColor: '#ffc107',
            backgroundColor: 'rgba(255, 193, 7, 0.1)',
            tension: 0.1,
            fill: true
        }]
    };
    
    new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Evoluția Glicemiei'
                }
            }
        }
    });
}

/**
 * Utility: Format date to DD.MM.YYYY
 */
function formatDate(date) {
    const d = new Date(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    return `${day}.${month}.${year}`;
}

/**
 * Utility: Calculate pregnancy week
 */
function calculatePregnancyWeek(lmpDate) {
    const today = new Date();
    const lmp = new Date(lmpDate);
    const diff = today - lmp;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const weeks = Math.floor(days / 7);
    const dayOfWeek = days % 7;
    return { weeks, days: dayOfWeek };
}

/**
 * Show loading spinner
 */
function showLoadingSpinner(element) {
    const spinner = document.createElement('div');
    spinner.className = 'spinner-border text-primary';
    spinner.role = 'status';
    element.appendChild(spinner);
}

/**
 * Hide loading spinner
 */
function hideLoadingSpinner(element) {
    const spinner = element.querySelector('.spinner-border');
    if (spinner) {
        spinner.remove();
    }
}

/**
 * Export function (placeholder)
 */
function exportToCSV(filename) {
    console.log('Exporting to CSV: ' + filename);
    // Implementation would depend on the backend
}

/**
 * Export function to PDF (placeholder)
 */
function exportToPDF(filename) {
    console.log('Exporting to PDF: ' + filename);
    // Implementation would depend on the backend and a library like jsPDF
}

function initializeAiChat() {
    console.log('initializeAiChat called');
    const shell = document.querySelector('[data-ai-chat]');
    if (!shell) {
        console.log('AI chat shell not found');
        return;
    }

    console.log('AI chat shell found, initializing...');
    const endpoint = shell.dataset.endpoint;
    const toggle = shell.querySelector('[data-ai-chat-toggle]');
    const close = shell.querySelector('[data-ai-chat-close]');
    let panel = shell.querySelector('[data-ai-chat-panel]');
    let messagesContainer = shell.querySelector('[data-ai-chat-messages]');
    let form = shell.querySelector('[data-ai-chat-form]');
    let input = shell.querySelector('[data-ai-chat-input]');
    let submit = shell.querySelector('[data-ai-chat-submit]');
    const storageKey = 'patient_ai_chat_history_v1';

    const missing = [];
    if (!toggle) missing.push('toggle');
    if (!close) missing.push('close');
    if (!panel) missing.push('panel');
    if (!messagesContainer) missing.push('messagesContainer');
    if (!form) missing.push('form');
    if (!input) missing.push('input');
    if (!submit) missing.push('submit');
    if (missing.length) {
        console.warn('AI chat widget: missing sub-elements -> ' + missing.join(', '));
    }

    let history = [];
    try {
        history = JSON.parse(sessionStorage.getItem(storageKey) || '[]');
    } catch (error) {
        history = [];
    }

    if (messagesContainer) {
        history.forEach(item => appendAiMessage(messagesContainer, item.role, item.content, item.timestamp));
    }

    function persistHistory() {
        sessionStorage.setItem(storageKey, JSON.stringify(history.slice(-12)));
    }

    function openPanel() {
        if (!panel) {
            panel = document.createElement('section');
            panel.className = 'ai-chat-panel';
            panel.setAttribute('data-ai-chat-panel', '');
            panel.innerHTML = '<div class="ai-chat-header"><strong>Asistent medical AI</strong></div><div class="ai-chat-body" data-ai-chat-messages></div>';
            shell.appendChild(panel);
            messagesContainer = panel.querySelector('[data-ai-chat-messages]');
        }
        panel.hidden = false;
        shell.classList.add('is-open');
        if (input) input.focus();
    }

    function closePanel() {
        if (panel) panel.hidden = true;
        shell.classList.remove('is-open');
    }

    if (toggle) {
        toggle.addEventListener('click', function() {
            const isHidden = !panel || panel.hidden;
            if (isHidden) {
                openPanel();
            } else {
                closePanel();
            }
        });
    }

    if (close) {
        close.addEventListener('click', closePanel);
    }

    if (form) {
        form.addEventListener('submit', async function(event) {
            event.preventDefault();
            if (!input) return;
            const message = input.value.trim();
            if (!message) {
                return;
            }

            const userItem = {
                role: 'user',
                content: message,
                timestamp: new Date().toLocaleString('ro-RO'),
            };
            history.push(userItem);
            if (messagesContainer) appendAiMessage(messagesContainer, userItem.role, userItem.content, userItem.timestamp);
            persistHistory();
            input.value = '';
            if (input) input.disabled = true;
            if (submit) submit.disabled = true;

            const loadingNode = messagesContainer ? appendAiMessage(messagesContainer, 'assistant', 'Se genereaza raspunsul...', '') : null;

            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message,
                        conversation: history.slice(-8),
                    }),
                });
                const data = await response.json();
                if (loadingNode) loadingNode.remove();

                const replyText = data.reply || data.error || 'Nu am primit un raspuns.';
                const assistantItem = {
                    role: 'assistant',
                    content: replyText,
                    timestamp: data.timestamp || new Date().toLocaleString('ro-RO'),
                };
                history.push(assistantItem);
                if (messagesContainer) appendAiMessage(messagesContainer, assistantItem.role, assistantItem.content, assistantItem.timestamp);
                persistHistory();
            } catch (error) {
                if (loadingNode) loadingNode.remove();
                const assistantItem = {
                    role: 'assistant',
                    content: 'Asistentul AI nu este disponibil momentan. Incearca din nou sau contacteaza medicul pentru o recomandare sigura.',
                    timestamp: new Date().toLocaleString('ro-RO'),
                };
                history.push(assistantItem);
                if (messagesContainer) appendAiMessage(messagesContainer, assistantItem.role, assistantItem.content, assistantItem.timestamp);
                persistHistory();
            } finally {
                if (input) input.disabled = false;
                if (submit) submit.disabled = false;
                if (input) input.focus();
            }
        });
    }
}

function appendAiMessage(container, role, content, timestamp) {
    const bubble = document.createElement('div');
    bubble.className = `ai-chat-bubble ${role === 'user' ? 'ai-chat-bubble-user' : 'ai-chat-bubble-assistant'}`;
    bubble.textContent = content;

    if (timestamp) {
        const meta = document.createElement('small');
        meta.className = 'ai-chat-meta';
        meta.textContent = timestamp;
        bubble.appendChild(meta);
    }

    container.appendChild(bubble);
    container.scrollTop = container.scrollHeight;
    return bubble;
}
