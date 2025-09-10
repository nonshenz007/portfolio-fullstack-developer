/**
 * LedgerFlow Form Submission Handler
 * Handles form validation, submission, and API integration
 */

class FormSubmissionHandler {
  constructor() {
    this.form = document.getElementById('generateForm');
    this.resultsPanel = document.getElementById('resultsPanel');
    this.resultsContent = document.getElementById('resultsContent');
    this.toastManager = window.toastManager || this.createFallbackToastManager();
    this.init();
  }

  init() {
    if (!this.form) return;
    
    // Add form submission handler
    this.form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      // Validate form
      if (!this.validateForm()) {
        return;
      }
      
      // Submit form
      await this.submitForm();
    });
    
    // Add input validation handlers
    this.setupValidation();
  }
  
  /**
   * Create a fallback toast manager if the global one isn't available
   */
  createFallbackToastManager() {
    return {
      success: (title, message) => {
        console.log(`Success: ${title} - ${message}`);
        this.showFallbackNotification(title, message, 'success');
      },
      error: (title, message) => {
        console.error(`Error: ${title} - ${message}`);
        this.showFallbackNotification(title, message, 'error');
      },
      warning: (title, message) => {
        console.warn(`Warning: ${title} - ${message}`);
        this.showFallbackNotification(title, message, 'warning');
      }
    };
  }
  
  /**
   * Show a fallback notification if toast manager is not available
   */
  showFallbackNotification(title, message, type) {
    // Create a simple notification element
    const notification = document.createElement('div');
    notification.className = `fallback-notification ${type}`;
    notification.innerHTML = `
      <div class="notification-content">
        <strong>${title}</strong>
        ${message ? `<p>${message}</p>` : ''}
      </div>
      <button class="notification-close">×</button>
    `;
    
    // Add styles
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: ${type === 'success' ? '#34c759' : type === 'error' ? '#ff3b30' : '#ff9500'};
      color: white;
      padding: 16px;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 10000;
      max-width: 400px;
      animation: slideIn 0.3s ease;
    `;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Close button functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
      notification.remove();
    });
    
    // Auto remove after 4 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.remove();
      }
    }, 4000);
  }
  
  /**
   * Setup validation handlers for form inputs
   */
  setupValidation() {
    // Add validation for required fields
    const requiredFields = this.form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
      field.addEventListener('blur', () => {
        this.validateField(field);
      });
      
      field.addEventListener('input', () => {
        // Remove error state when user starts typing
        if (field.classList.contains('error')) {
          field.classList.remove('error');
          
          // Remove error class from form group
          const formGroup = field.closest('.form-group');
          if (formGroup) {
            formGroup.classList.remove('has-error');
          }
          
          const errorElement = field.parentNode.querySelector('.field-error');
          if (errorElement) {
            errorElement.remove();
          }
        }
      });
    });
    
    // Add validation for numeric fields
    const numericFields = this.form.querySelectorAll('input[type="number"]');
    numericFields.forEach(field => {
      field.addEventListener('blur', () => {
        this.validateNumericField(field);
      });
    });
  }
  
  /**
   * Validate a single form field
   * @param {HTMLElement} field - The field to validate
   * @returns {boolean} - Whether the field is valid
   */
  validateField(field) {
    // Check if field is empty
    if (field.required && !field.value.trim()) {
      this.showFieldError(field, 'This field is required');
      return false;
    }
    
    // Check if field is a number and has min/max constraints
    if (field.type === 'number') {
      return this.validateNumericField(field);
    }
    
    // Field is valid
    return true;
  }
  
  /**
   * Validate a numeric field
   * @param {HTMLElement} field - The numeric field to validate
   * @returns {boolean} - Whether the field is valid
   */
  validateNumericField(field) {
    const value = parseFloat(field.value);
    
    // Check if value is a number
    if (isNaN(value) && field.required) {
      this.showFieldError(field, 'Please enter a valid number');
      return false;
    }
    
    // Check min constraint
    if (field.min !== undefined && value < parseFloat(field.min)) {
      this.showFieldError(field, `Value must be at least ${field.min}`);
      return false;
    }
    
    // Check max constraint
    if (field.max !== undefined && value > parseFloat(field.max)) {
      this.showFieldError(field, `Value must be at most ${field.max}`);
      return false;
    }
    
    // Field is valid
    return true;
  }
  
  /**
   * Show an error message for a field with Apple-style error states
   * @param {HTMLElement} field - The field with the error
   * @param {string} message - The error message to display
   */
  showFieldError(field, message) {
    // Add Apple-style error class to field
    field.classList.add('error');
    
    // Add error class to form group for additional styling
    const formGroup = field.closest('.form-group');
    if (formGroup) {
      formGroup.classList.add('has-error');
    }
    
    // Remove any existing error message
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
      existingError.remove();
    }
    
    // Create Apple-style error message element
    const errorElement = document.createElement('div');
    errorElement.className = 'field-error';
    errorElement.innerHTML = `
      <span class="error-icon">⚠️</span>
      <span class="error-text">${message}</span>
    `;
    
    // Add error message after the field
    field.parentNode.appendChild(errorElement);
    
    // Add shake animation to field
    field.style.animation = 'shake 0.5s ease-in-out';
    setTimeout(() => {
      field.style.animation = '';
    }, 500);
    
    // Focus the field with smooth scroll
    field.focus();
    field.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
  
  /**
   * Validate the entire form
   * @returns {boolean} - Whether the form is valid
   */
  validateForm() {
    let isValid = true;
    
    // Validate required fields
    const requiredFields = this.form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
      if (!this.validateField(field)) {
        isValid = false;
      }
    });
    
    // Validate numeric fields
    const numericFields = this.form.querySelectorAll('input[type="number"]');
    numericFields.forEach(field => {
      if (!this.validateNumericField(field)) {
        isValid = false;
      }
    });
    
    // Show toast if form is invalid
    if (!isValid) {
      this.toastManager.error('Validation Error', 'Please correct the highlighted fields');
    }
    
    return isValid;
  }
  
  /**
   * Get form data as JSON object with proper API parameter mapping
   * @returns {Object} - Form data as JSON mapped to API parameters
   */
  getFormData() {
    const formData = new FormData(this.form);
    const data = {};
    
    // Convert FormData to JSON
    for (const [key, value] of formData.entries()) {
      // Handle multi-select fields
      if (key.endsWith('[]')) {
        const cleanKey = key.slice(0, -2);
        if (!data[cleanKey]) {
          data[cleanKey] = [];
        }
        data[cleanKey].push(value);
      } else {
        // Handle checkbox values
        const field = this.form.querySelector(`[name="${key}"]`);
        if (field && field.type === 'checkbox') {
          data[key] = field.checked;
        } else if (field && field.type === 'number') {
          // Convert numeric values to proper types
          const numValue = parseFloat(value);
          data[key] = isNaN(numValue) ? value : numValue;
        } else {
          data[key] = value;
        }
      }
    }
    
    // Handle segmented controls (hidden inputs)
    const segmentedControls = this.form.querySelectorAll('.segmented-control');
    segmentedControls.forEach(control => {
      const activeSegment = control.querySelector('.segment.active');
      const inputId = control.dataset.input;
      
      if (activeSegment && inputId) {
        const input = document.getElementById(inputId);
        if (input) {
          data[input.name] = activeSegment.dataset.value;
        }
      }
    });
    
    // Handle range sliders - ensure they're included
    const rangeSliders = this.form.querySelectorAll('input[type="range"]');
    rangeSliders.forEach(slider => {
      data[slider.name] = parseInt(slider.value);
    });
    
    // Handle multi-select fields properly
    const multiSelects = this.form.querySelectorAll('select[multiple]');
    multiSelects.forEach(select => {
      const selectedValues = Array.from(select.selectedOptions).map(option => option.value);
      data[select.name] = selectedValues;
    });
    
    // Map form field names to API parameter names if needed
    const parameterMapping = {
      'min_items_per_invoice': 'min_items',
      'max_items_per_invoice': 'max_items',
      'min_invoice_amount': 'min_bill_amount',
      'max_invoice_amount': 'max_bill_amount',
      'customer_type_mix': 'customer_type'
    };
    
    // Apply parameter mapping
    Object.keys(parameterMapping).forEach(formKey => {
      if (data.hasOwnProperty(formKey)) {
        data[parameterMapping[formKey]] = data[formKey];
        delete data[formKey];
      }
    });
    
    // Ensure required fields have default values
    const defaults = {
      invoice_count: 100,
      template_type: 'gst_einvoice',
      business_style: 'retail_shop',
      country: 'India',
      invoice_type: 'gst',
      reality_buffer: 75,
      believability_stress: 50,
      customer_repeat_rate: 30,
      min_items: 1,
      max_items: 8,
      min_bill_amount: 100,
      max_bill_amount: 50000,
      customer_region: 'generic_indian',
      customer_type: 'mixed',
      timeflow_mode: 'realistic',
      entropy_mode: 'smart',
      audit_risk: 'medium'
    };
    
    // Apply defaults for missing values
    Object.keys(defaults).forEach(key => {
      if (!data.hasOwnProperty(key) || data[key] === '' || data[key] === null) {
        data[key] = defaults[key];
      }
    });
    
    return data;
  }
  
  /**
   * Submit the form to the API
   */
  async submitForm() {
    console.log('FormSubmissionHandler.submitForm() called');
    // Get form data
    const data = this.getFormData();
    
    // Show loading state
    const submitBtn = this.form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="btn-icon">⏳</span> Generating...';
    
    try {
      // Submit form to API
      const response = await fetch('/api/invoices/generate', {
        credentials: 'include',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
      
      // Parse response
      const result = await response.json();
      
      // Debug logging
      console.log('API Response:', result);
      console.log('Response success:', result.success);
      
      // Handle response
      if (result.success) {
        this.handleSuccess(result);
      } else {
        this.handleError(result);
      }
    } catch (error) {
      // Debug logging
      console.log('❌ Exception caught:', error);
      console.log('Error type:', typeof error);
      console.log('Error message:', error.message);
      
      // Handle network error
      this.handleError({ error: 'Network error occurred. Please try again.' });
    } finally {
      // Reset button state
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
    }
  }
  
  /**
   * Handle successful form submission with Apple-style feedback
   * @param {Object} result - API response
   */
  handleSuccess(result) {
    // Show success toast with Apple-style messaging
    this.toastManager.success(
      'Invoices Generated Successfully', 
      `Created ${result.count || 0} invoices${result.batch_id ? ` (Batch: ${result.batch_id.slice(-8)})` : ''}`
    );
    
    // Show results panel with enhanced Apple-style design
    if (this.resultsPanel && this.resultsContent) {
      // Create Apple-style results content
      let content = `
        <div class="result-item result-success">
          <div class="result-header">
            <div class="result-icon success-icon">✅</div>
            <div class="result-title">
              <h3>Generation Successful</h3>
              <p class="result-subtitle">Your invoices are ready for export</p>
            </div>
          </div>
          
          <div class="result-details">
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">Invoices Created</span>
                <span class="detail-value">${result.count || 0}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Batch ID</span>
                <span class="detail-value">${result.batch_id || 'N/A'}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Status</span>
                <span class="detail-value status-ready">Ready for Export</span>
              </div>
            </div>
          </div>
          
          <div class="result-actions">
            <a href="/export" class="btn btn-primary">
              <span class="btn-icon">📄</span>
              Export Invoices
            </a>
            <button class="btn btn-secondary" onclick="this.closest('#resultsPanel').style.display='none'">
              <span class="btn-icon">✕</span>
              Close
            </button>
          </div>
        </div>
      `;
      
      // Update results panel with smooth animation
      this.resultsContent.innerHTML = content;
      this.resultsPanel.style.display = 'block';
      
      // Add entrance animation
      setTimeout(() => {
        this.resultsPanel.classList.add('show');
      }, 10);
      
      // Scroll to results with smooth behavior
      this.resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    // Reset form to clean state (optional)
    this.clearFormErrors();
  }
  
  /**
   * Handle form submission error with Apple-style error feedback
   * @param {Object} result - API error response
   */
  handleError(result) {
    // Show error toast with Apple-style messaging
    this.toastManager.error(
      'Generation Failed', 
      result.error || 'An error occurred during invoice generation.'
    );
    
    // Show error in results panel with Apple-style design
    if (this.resultsPanel && this.resultsContent) {
      // Create Apple-style error content
      let content = `
        <div class="result-item result-error">
          <div class="result-header">
            <div class="result-icon error-icon">❌</div>
            <div class="result-title">
              <h3>Generation Failed</h3>
              <p class="result-subtitle">Please review the error and try again</p>
            </div>
          </div>
          
          <div class="result-details">
            <div class="error-message">
              <p>${result.error || 'An error occurred during invoice generation.'}</p>
            </div>
            
            ${result.details ? `
              <div class="error-details">
                <h4>Additional Details:</h4>
                <ul class="error-list">
                  ${Array.isArray(result.details) 
                    ? result.details.map(detail => `<li>${detail}</li>`).join('') 
                    : `<li>${result.details}</li>`}
                </ul>
              </div>
            ` : ''}
          </div>
          
          <div class="result-actions">
            <button class="btn btn-primary" onclick="this.closest('#resultsPanel').style.display='none'; document.getElementById('generateForm').scrollIntoView({behavior: 'smooth'});">
              <span class="btn-icon">🔄</span>
              Try Again
            </button>
            <button class="btn btn-secondary" onclick="this.closest('#resultsPanel').style.display='none'">
              <span class="btn-icon">✕</span>
              Close
            </button>
          </div>
        </div>
      `;
      
      // Update results panel with smooth animation
      this.resultsContent.innerHTML = content;
      this.resultsPanel.style.display = 'block';
      
      // Add entrance animation
      setTimeout(() => {
        this.resultsPanel.classList.add('show');
      }, 10);
      
      // Scroll to results with smooth behavior
      this.resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }
  
  /**
   * Clear all form errors
   */
  clearFormErrors() {
    // Remove error classes from all fields
    this.form.querySelectorAll('.error').forEach(field => {
      field.classList.remove('error');
    });
    
    // Remove error classes from form groups
    this.form.querySelectorAll('.has-error').forEach(group => {
      group.classList.remove('has-error');
    });
    
    // Remove all error messages
    this.form.querySelectorAll('.field-error').forEach(error => {
      error.remove();
    });
  }
}

// Initialize form submission handler when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.formSubmissionHandler = new FormSubmissionHandler();
});