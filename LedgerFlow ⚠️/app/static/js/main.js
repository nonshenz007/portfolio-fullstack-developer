// LedgerFlow - Main JavaScript

// Toast notification function
function toast(msg, ok = true) {
    const color = ok ? 'bg-success' : 'bg-danger';
    const t = document.createElement('div');
    t.className = `toast align-items-center text-white ${color} border-0`;
    t.role = 'alert';
    t.innerHTML = `<div class="d-flex"><div class="toast-body">${msg}</div></div>`;
    document.getElementById('toastContainer').appendChild(t);
    new bootstrap.Toast(t, {delay: 3000}).show();
}

// Form submission handler - Exclude generateForm as it has its own handler
document.addEventListener('submit', async (e) => {
    const f = e.target;
    console.log('Global form handler triggered for form:', f.id);
    if (f.id !== 'importForm' && f.id !== 'settingsForm' && f.id !== 'loginForm') return;
    
    e.preventDefault();
    
    const submitBtn = f.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
    submitBtn.disabled = true;
    
    try {
        const fd = new FormData(f);
        const r = await fetch(f.action, {method: 'POST', body: fd});
        const j = await r.json();
        
        if (j.success) {
            toast(j.message || 'Success!', true);
        } else {
            toast(j.error || 'Failed', false);
        }
    } catch (error) {
        toast('Network error: ' + error.message, false);
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
});

// Show generation results
function showGenerationResults(data) {
    const resultsCard = document.getElementById('generationResultsCard');
    const resultsDiv = document.getElementById('generationResults');
    
    if (resultsCard && resultsDiv) {
        resultsDiv.innerHTML = `
            <div class="row">
                <div class="col-md-3">
                    <div class="card bg-light">
                        <div class="card-body text-center">
                            <h4 class="text-primary">${data.invoice_count || 0}</h4>
                            <small class="text-muted">Invoices Generated</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-light">
                        <div class="card-body text-center">
                            <h4 class="text-success">₹${data.total_revenue || 0}</h4>
                            <small class="text-muted">Total Revenue</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-light">
                        <div class="card-body text-center">
                            <h4 class="text-info">${data.batch_id || 'N/A'}</h4>
                            <small class="text-muted">Batch ID</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-light">
                        <div class="card-body text-center">
                            <h4 class="text-warning">${data.execution_time || 0}s</h4>
                            <small class="text-muted">Execution Time</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
        resultsCard.style.display = 'block';
    }
}

// Range slider value display
document.addEventListener('DOMContentLoaded', function() {
    // Update range slider values
    const rangeSliders = document.querySelectorAll('input[type="range"]');
    rangeSliders.forEach(slider => {
        const valueDisplay = document.getElementById(slider.id + 'Value');
        if (valueDisplay) {
            slider.addEventListener('input', function() {
                valueDisplay.textContent = this.value + '%';
            });
        }
    });
    
    // Product selection population
    loadProducts();
});

// Load products for selection
async function loadProducts() {
    try {
        const response = await fetch('/api/products', {
            credentials: 'include'
        });
        const data = await response.json();
        
        if (data.success && data.products) {
            const mostSoldSelect = document.getElementById('mostSoldProducts');
            const leastSoldSelect = document.getElementById('leastSoldProducts');
            const excludedSelect = document.getElementById('excludedProducts');
            
            const options = data.products.map(product => 
                `<option value="${product.id}">${product.name} (${product.code})</option>`
            ).join('');
            
            if (mostSoldSelect) mostSoldSelect.innerHTML = options;
            if (leastSoldSelect) leastSoldSelect.innerHTML = options;
            if (excludedSelect) excludedSelect.innerHTML = options;
        }
    } catch (error) {
        console.error('Failed to load products:', error);
    }
}

// Global variables to store current batch info
let currentBatchId = null;

// Import function
async function importProducts(formData) {
    try {
        const response = await fetch('/api/products/import', {
            method: 'POST',
            credentials: 'include',
            body: formData
        });
        const data = await response.json();
        
        if (data.success) {
            toast(`Successfully imported ${data.products} products!`, true);
            return data;
        } else {
            toast('Import failed: ' + data.error, false);
            return null;
        }
    } catch (error) {
        toast('Import error: ' + error.message, false);
        return null;
    }
}

// Generate function
async function generateInvoices(configData) {
    try {
        const response = await fetch('/api/invoices/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(configData)
        });
        const data = await response.json();
        
        if (data.success) {
            currentBatchId = data.batch_id;
            toast(`Generated ${data.invoices} invoices successfully!`, true);
            showGenerationResults(data);
            return data;
        } else {
            toast('Generation failed: ' + data.error, false);
            return null;
        }
    } catch (error) {
        toast('Generation error: ' + error.message, false);
        return null;
    }
}

// Verify function
async function verifyBatch(batchId) {
    try {
        const response = await fetch(`/api/verification/verify/${batchId}`, {
            credentials: 'include'
        });
        const data = await response.json();
        
        if (data.success) {
            toast(`Verification completed: ${data.passed}/${data.total} passed`, true);
            showVerificationResults(data);
            return data;
        } else {
            toast('Verification failed: ' + data.error, false);
            return null;
        }
    } catch (error) {
        toast('Verification error: ' + error.message, false);
        return null;
    }
}

// Export function
async function exportBatch(batchId) {
    try {
        const response = await fetch(`/api/export/${batchId}`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `invoices_${batchId}.zip`;
            a.click();
            window.URL.revokeObjectURL(url);
            toast('Export successful!', true);
            return true;
        } else {
            const data = await response.json();
            toast('Export failed: ' + data.error, false);
            return false;
        }
    } catch (error) {
        toast('Export error: ' + error.message, false);
        return false;
    }
}

// Legacy export functions (for backward compatibility)
async function exportPDFs() {
    if (currentBatchId) {
        return await exportBatch(currentBatchId);
    } else {
        toast('No batch available for export. Please generate invoices first.', false);
        return false;
    }
}

async function exportExcel() {
    try {
        const response = await fetch('/api/export/excel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({})
        });
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'invoices.xlsx';
            a.click();
            window.URL.revokeObjectURL(url);
            toast('Excel export successful!', true);
        } else {
            toast('Excel export failed', false);
        }
    } catch (error) {
        toast('Export error: ' + error.message, false);
    }
}

// Legacy verification function (for backward compatibility)
async function verifyInvoices() {
    if (currentBatchId) {
        return await verifyBatch(currentBatchId);
    } else {
        toast('No batch available for verification. Please generate invoices first.', false);
        return false;
    }
}

function showVerificationResults(data) {
    const resultsCard = document.getElementById('verificationResultsCard');
    const resultsDiv = document.getElementById('verificationContent');
    
    if (resultsCard && resultsDiv) {
        const successRate = data.success_rate || (data.total > 0 ? Math.round((data.passed / data.total) * 100) : 0);
        resultsDiv.innerHTML = `
            <div class="row">
                <div class="col-md-4">
                    <div class="card bg-success text-white">
                        <div class="card-body text-center">
                            <h4>${successRate}%</h4>
                            <small>Success Rate</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-info text-white">
                        <div class="card-body text-center">
                            <h4>${data.passed || 0}</h4>
                            <small>Passed Invoices</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-warning text-dark">
                        <div class="card-body text-center">
                            <h4>${data.failed || 0}</h4>
                            <small>Failed Invoices</small>
                        </div>
                    </div>
                </div>
            </div>
            ${data.issues && data.issues.length > 0 ? `
                <div class="mt-3">
                    <h6>Common Issues:</h6>
                    <ul class="list-group">
                        ${data.issues.slice(0, 5).map(issue => `<li class="list-group-item">${issue}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
        resultsCard.style.display = 'block';
    }
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-IN');
}

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});