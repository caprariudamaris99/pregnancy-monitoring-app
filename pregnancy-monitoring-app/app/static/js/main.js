// Main JavaScript for Pregnancy Monitoring App

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips and popovers
    initializeBootstrapComponents();
    
    // Set up event listeners
    setupEventListeners();
    
    // Load charts if present
    loadCharts();
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

/**
 * Load weight chart
 */
function loadWeightChart(ctx) {
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
