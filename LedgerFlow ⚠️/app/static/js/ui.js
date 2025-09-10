/**
 * LedgerFlow UI - Core JavaScript for Apple-style interface
 * Handles theme management, form interactions, and UI components
 */

// Theme Management System
class ThemeManager {
  constructor() {
    this.storageKey = 'lf_dark';
    this.body = document.body;
    this.toggle = document.getElementById('modeToggle');
    this.init();
  }
  
  init() {
    // Load saved preference
    const isDark = localStorage.getItem(this.storageKey) === 'true';
    this.setTheme(isDark);
    
    // Bind toggle event
    this.toggle?.addEventListener('click', () => {
      this.toggleTheme();
    });
  }
  
  setTheme(isDark) {
    this.body.classList.toggle('dark', isDark);
    localStorage.setItem(this.storageKey, isDark.toString());
    this.updateToggleIcon(isDark);
  }
  
  toggleTheme() {
    const isDark = !this.body.classList.contains('dark');
    this.setTheme(isDark);
  }
  
  updateToggleIcon(isDark) {
    if (this.toggle) {
      this.toggle.innerHTML = isDark ? '☀️' : '🌙';
      this.toggle.setAttribute('title', isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode');
    }
  }
}

// Mobile and Responsive Management
class ResponsiveManager {
  constructor() {
    this.sidebar = document.querySelector('.sidebar');
    this.mobileToggle = document.getElementById('mobileMenuToggle');
    this.overlay = document.getElementById('sidebarOverlay');
    this.isMobile = false;
    this.init();
  }
  
  init() {
    this.checkScreenSize();
    this.bindEvents();
    
    // Listen for window resize
    window.addEventListener('resize', () => {
      this.checkScreenSize();
    });
  }
  
  checkScreenSize() {
    const wasMobile = this.isMobile;
    this.isMobile = window.innerWidth <= 480;
    
    if (this.isMobile !== wasMobile) {
      this.updateMobileState();
    }
    
    // Show/hide mobile toggle button
    if (this.mobileToggle) {
      this.mobileToggle.style.display = this.isMobile ? 'block' : 'none';
    }
  }
  
  updateMobileState() {
    if (this.isMobile) {
      // Mobile mode
      this.closeMobileMenu();
    } else {
      // Desktop mode
      this.closeMobileMenu();
      if (this.sidebar) {
        this.sidebar.classList.remove('mobile-open');
      }
    }
  }
  
  bindEvents() {
    // Mobile menu toggle
    if (this.mobileToggle) {
      this.mobileToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        this.toggleMobileMenu();
      });
    }
    
    // Overlay click to close
    if (this.overlay) {
      this.overlay.addEventListener('click', () => {
        this.closeMobileMenu();
      });
    }
    
    // Close menu when clicking nav links on mobile
    document.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        if (this.isMobile) {
          this.closeMobileMenu();
        }
      });
    });
    
    // Close menu on escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isMobile) {
        this.closeMobileMenu();
      }
    });
    
    // Prevent body scroll when mobile menu is open
    document.addEventListener('touchmove', (e) => {
      if (this.isMobile && this.sidebar?.classList.contains('mobile-open')) {
        if (!this.sidebar.contains(e.target)) {
          e.preventDefault();
        }
      }
    }, { passive: false });
  }
  
  toggleMobileMenu() {
    if (!this.isMobile || !this.sidebar) return;
    
    const isOpen = this.sidebar.classList.contains('mobile-open');
    
    if (isOpen) {
      this.closeMobileMenu();
    } else {
      this.openMobileMenu();
    }
  }
  
  openMobileMenu() {
    if (!this.isMobile || !this.sidebar) return;
    
    this.sidebar.classList.add('mobile-open');
    this.overlay?.classList.add('active');
    document.body.style.overflow = 'hidden';
    
    // Update toggle icon
    if (this.mobileToggle) {
      this.mobileToggle.innerHTML = '✕';
      this.mobileToggle.setAttribute('title', 'Close menu');
    }
  }
  
  closeMobileMenu() {
    if (!this.sidebar) return;
    
    this.sidebar.classList.remove('mobile-open');
    this.overlay?.classList.remove('active');
    document.body.style.overflow = '';
    
    // Update toggle icon
    if (this.mobileToggle) {
      this.mobileToggle.innerHTML = '☰';
      this.mobileToggle.setAttribute('title', 'Open menu');
    }
  }
  
  // Touch gesture support for swipe to open/close
  initTouchGestures() {
    let startX = 0;
    let currentX = 0;
    let isDragging = false;
    
    document.addEventListener('touchstart', (e) => {
      if (!this.isMobile) return;
      
      startX = e.touches[0].clientX;
      isDragging = true;
    });
    
    document.addEventListener('touchmove', (e) => {
      if (!this.isMobile || !isDragging) return;
      
      currentX = e.touches[0].clientX;
      const diffX = currentX - startX;
      
      // Swipe right from left edge to open menu
      if (startX < 20 && diffX > 50 && !this.sidebar?.classList.contains('mobile-open')) {
        this.openMobileMenu();
        isDragging = false;
      }
      
      // Swipe left to close menu
      if (diffX < -50 && this.sidebar?.classList.contains('mobile-open')) {
        this.closeMobileMenu();
        isDragging = false;
      }
    });
    
    document.addEventListener('touchend', () => {
      isDragging = false;
    });
  }
}

// Form Components
class FormComponents {
  constructor() {
    this.init();
  }
  
  init() {
    this.initSwitches();
    this.initSegmentedControls();
    this.initRangeSliders();
    this.initFileUploads();
    this.initMultiSelects();
  }
  
  // Initialize Cupertino-style switches
  initSwitches() {
    document.querySelectorAll('.switch input[type="checkbox"]').forEach(checkbox => {
      checkbox.addEventListener('change', () => {
        const switchEl = checkbox.closest('.switch');
        switchEl.classList.toggle('active', checkbox.checked);
      });
      
      // Set initial state
      const switchEl = checkbox.closest('.switch');
      switchEl.classList.toggle('active', checkbox.checked);
    });
  }
  
  // Initialize segmented controls
  initSegmentedControls() {
    document.querySelectorAll('.segmented-control').forEach(control => {
      const segments = control.querySelectorAll('.segment');
      const input = document.getElementById(control.dataset.input);
      
      segments.forEach(segment => {
        segment.addEventListener('click', () => {
          segments.forEach(s => s.classList.remove('active'));
          segment.classList.add('active');
          
          if (input) {
            input.value = segment.dataset.value;
            // Trigger change event
            const event = new Event('change');
            input.dispatchEvent(event);
          }
        });
      });
    });
  }
  
  // Initialize range sliders with live value display and enhanced interactions
  initRangeSliders() {
    document.querySelectorAll('.range-slider-input').forEach(slider => {
      const valueDisplay = document.getElementById(`${slider.id}-value`);
      const unit = slider.dataset.unit || '';
      const container = slider.closest('.range-slider-container');
      
      if (valueDisplay) {
        // Update on input with smooth animation
        slider.addEventListener('input', () => {
          const value = slider.value;
          valueDisplay.textContent = `${value}${unit}`;
          
          // Add visual feedback
          valueDisplay.style.transform = 'scale(1.1)';
          setTimeout(() => {
            valueDisplay.style.transform = 'scale(1)';
          }, 150);
        });
        
        // Set initial value
        valueDisplay.textContent = `${slider.value}${unit}`;
      }
      
      // Add hover effects
      slider.addEventListener('mouseenter', () => {
        if (container) {
          container.style.transform = 'translateY(-1px)';
        }
      });
      
      slider.addEventListener('mouseleave', () => {
        if (container) {
          container.style.transform = 'translateY(0)';
        }
      });
      
      // Add focus effects
      slider.addEventListener('focus', () => {
        if (valueDisplay) {
          valueDisplay.style.boxShadow = '0 0 0 3px rgba(10, 132, 255, 0.2)';
        }
      });
      
      slider.addEventListener('blur', () => {
        if (valueDisplay) {
          valueDisplay.style.boxShadow = '';
        }
      });
    });
  }
  
  // Initialize file uploads
  initFileUploads() {
    document.querySelectorAll('.file-upload').forEach(upload => {
      const input = upload.querySelector('input[type="file"]');
      const label = upload.querySelector('.file-upload-text');
      const defaultText = label?.textContent;
      
      if (input && label) {
        input.addEventListener('change', () => {
          if (input.files.length) {
            const fileNames = Array.from(input.files).map(file => file.name).join(', ');
            label.textContent = fileNames;
          } else {
            label.textContent = defaultText;
          }
        });
        
        // Drag and drop support
        upload.addEventListener('dragover', (e) => {
          e.preventDefault();
          upload.classList.add('dragover');
        });
        
        upload.addEventListener('dragleave', () => {
          upload.classList.remove('dragover');
        });
        
        upload.addEventListener('drop', (e) => {
          e.preventDefault();
          upload.classList.remove('dragover');
          
          if (e.dataTransfer.files.length) {
            input.files = e.dataTransfer.files;
            
            // Trigger change event
            const event = new Event('change');
            input.dispatchEvent(event);
          }
        });
      }
    });
  }
  
  // Initialize multi-select components for product selection
  initMultiSelects() {
    document.querySelectorAll('.multi-select').forEach(multiSelect => {
      new MultiSelectComponent(multiSelect);
    });
  }
}

// Multi-Select Component Class
class MultiSelectComponent {
  constructor(element) {
    this.element = element;
    this.trigger = element.querySelector('.multi-select-trigger');
    this.dropdown = element.querySelector('.multi-select-dropdown');
    this.search = element.querySelector('.multi-select-search');
    this.options = element.querySelector('.multi-select-options');
    this.selectedContainer = element.querySelector('.multi-select-selected');
    this.placeholder = element.querySelector('.multi-select-placeholder');
    this.arrow = element.querySelector('.multi-select-arrow');
    this.hiddenInput = element.querySelector('input[type="hidden"]');
    
    this.selectedValues = [];
    this.allOptions = [];
    this.filteredOptions = [];
    this.isOpen = false;
    
    this.init();
  }
  
  init() {
    this.loadOptions();
    this.bindEvents();
    this.updateDisplay();
  }
  
  async loadOptions() {
    const dataSource = this.element.dataset.source;
    
    if (dataSource) {
      try {
        const response = await fetch(dataSource);
        const data = await response.json();
        
        if (data.success && data.products) {
          this.allOptions = data.products.map(product => ({
            value: product.id || product.name,
            label: product.name,
            description: product.description || ''
          }));
        }
      } catch (error) {
        console.error('Failed to load multi-select options:', error);
        // Fallback to static options if API fails
        this.loadStaticOptions();
      }
    } else {
      this.loadStaticOptions();
    }
    
    this.filteredOptions = [...this.allOptions];
    this.renderOptions();
  }
  
  loadStaticOptions() {
    // Fallback static options for product selection
    this.allOptions = [
      { value: 'laptop', label: 'Laptop Computer', description: 'High-performance laptop' },
      { value: 'mouse', label: 'Wireless Mouse', description: 'Ergonomic wireless mouse' },
      { value: 'keyboard', label: 'Mechanical Keyboard', description: 'RGB mechanical keyboard' },
      { value: 'monitor', label: '4K Monitor', description: '27-inch 4K display' },
      { value: 'headphones', label: 'Noise-Canceling Headphones', description: 'Premium audio headphones' },
      { value: 'webcam', label: 'HD Webcam', description: '1080p webcam with microphone' },
      { value: 'tablet', label: 'Tablet Device', description: '10-inch tablet with stylus' },
      { value: 'smartphone', label: 'Smartphone', description: 'Latest model smartphone' },
      { value: 'charger', label: 'USB-C Charger', description: 'Fast charging adapter' },
      { value: 'cable', label: 'HDMI Cable', description: '6ft HDMI cable' }
    ];
  }
  
  bindEvents() {
    // Toggle dropdown
    this.trigger.addEventListener('click', (e) => {
      e.preventDefault();
      this.toggle();
    });
    
    // Search functionality
    if (this.search) {
      this.search.addEventListener('input', (e) => {
        this.filterOptions(e.target.value);
      });
      
      this.search.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          this.close();
        }
      });
    }
    
    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!this.element.contains(e.target)) {
        this.close();
      }
    });
    
    // Keyboard navigation
    this.element.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.close();
      } else if (e.key === 'Enter' || e.key === ' ') {
        if (!this.isOpen) {
          e.preventDefault();
          this.open();
        }
      }
    });
  }
  
  toggle() {
    if (this.isOpen) {
      this.close();
    } else {
      this.open();
    }
  }
  
  open() {
    this.isOpen = true;
    this.element.classList.add('open');
    
    if (this.search) {
      setTimeout(() => {
        this.search.focus();
      }, 100);
    }
    
    // Add animation class
    this.dropdown.classList.add('fade-in');
  }
  
  close() {
    this.isOpen = false;
    this.element.classList.remove('open');
    
    if (this.search) {
      this.search.value = '';
      this.filterOptions('');
    }
  }
  
  filterOptions(searchTerm) {
    const term = searchTerm.toLowerCase();
    this.filteredOptions = this.allOptions.filter(option => 
      option.label.toLowerCase().includes(term) || 
      option.description.toLowerCase().includes(term)
    );
    this.renderOptions();
  }
  
  renderOptions() {
    if (!this.options) return;
    
    this.options.innerHTML = '';
    
    if (this.filteredOptions.length === 0) {
      const noResults = document.createElement('div');
      noResults.className = 'multi-select-no-results';
      noResults.textContent = 'No products found';
      this.options.appendChild(noResults);
      return;
    }
    
    this.filteredOptions.forEach(option => {
      const optionEl = document.createElement('div');
      optionEl.className = 'multi-select-option';
      optionEl.dataset.value = option.value;
      
      if (this.selectedValues.includes(option.value)) {
        optionEl.classList.add('selected');
      }
      
      optionEl.innerHTML = `
        <div class="multi-select-checkbox"></div>
        <div>
          <div>${option.label}</div>
          ${option.description ? `<div style="font-size: 0.8rem; color: var(--gray-600);">${option.description}</div>` : ''}
        </div>
      `;
      
      optionEl.addEventListener('click', () => {
        this.toggleOption(option.value);
      });
      
      this.options.appendChild(optionEl);
    });
  }
  
  toggleOption(value) {
    const index = this.selectedValues.indexOf(value);
    
    if (index > -1) {
      this.selectedValues.splice(index, 1);
    } else {
      this.selectedValues.push(value);
    }
    
    this.updateDisplay();
    this.updateHiddenInput();
    this.renderOptions();
    
    // Trigger change event
    const event = new CustomEvent('change', {
      detail: { selectedValues: this.selectedValues }
    });
    this.element.dispatchEvent(event);
  }
  
  updateDisplay() {
    if (!this.selectedContainer || !this.placeholder) return;
    
    // Clear current display
    this.selectedContainer.innerHTML = '';
    
    if (this.selectedValues.length === 0) {
      this.placeholder.style.display = 'block';
      this.selectedContainer.style.display = 'none';
    } else {
      this.placeholder.style.display = 'none';
      this.selectedContainer.style.display = 'flex';
      
      this.selectedValues.forEach(value => {
        const option = this.allOptions.find(opt => opt.value === value);
        if (option) {
          const tag = document.createElement('div');
          tag.className = 'multi-select-tag';
          tag.innerHTML = `
            ${option.label}
            <button type="button" class="multi-select-tag-remove" data-value="${value}">×</button>
          `;
          
          const removeBtn = tag.querySelector('.multi-select-tag-remove');
          removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleOption(value);
          });
          
          this.selectedContainer.appendChild(tag);
        }
      });
    }
  }
  
  updateHiddenInput() {
    if (this.hiddenInput) {
      this.hiddenInput.value = this.selectedValues.join(',');
    }
  }
  
  // Public methods
  getSelectedValues() {
    return [...this.selectedValues];
  }
  
  setSelectedValues(values) {
    this.selectedValues = Array.isArray(values) ? [...values] : [];
    this.updateDisplay();
    this.updateHiddenInput();
    this.renderOptions();
  }
  
  clearSelection() {
    this.selectedValues = [];
    this.updateDisplay();
    this.updateHiddenInput();
    this.renderOptions();
  }
}

// Toast Notification System
class ToastManager {
  constructor() {
    this.container = this.createContainer();
  }
  
  createContainer() {
    let container = document.querySelector('.toast-container');
    
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    
    return container;
  }
  
  show(options) {
    const { title, message, type = 'info', duration = 3000, persistent = false, actions = [] } = options;
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Set icon based on type
    let icon = '';
    switch (type) {
      case 'success':
        icon = '✅';
        break;
      case 'error':
        icon = '❌';
        break;
      case 'warning':
        icon = '⚠️';
        break;
      default:
        icon = 'ℹ️';
    }
    
    // Build toast content
    let actionsHtml = '';
    if (actions.length > 0) {
      actionsHtml = `
        <div class="toast-actions">
          ${actions.map(action => `
            <button class="toast-action-btn" data-action="${action.id}">${action.label}</button>
          `).join('')}
        </div>
      `;
    }
    
    toast.innerHTML = `
      <div class="toast-icon">${icon}</div>
      <div class="toast-content">
        <div class="toast-title">${title}</div>
        ${message ? `<div class="toast-message">${message}</div>` : ''}
        ${actionsHtml}
      </div>
      ${!persistent ? '<button class="toast-close">×</button>' : ''}
    `;
    
    // Add to container with stagger animation
    this.container.appendChild(toast);
    
    // Add entrance animation
    toast.classList.add('bounce-in');
    
    // Show with smooth animation
    setTimeout(() => {
      toast.classList.add('show');
    }, 10);
    
    // Close button functionality
    const closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        this.close(toast);
      });
    }
    
    // Action button functionality
    const actionBtns = toast.querySelectorAll('.toast-action-btn');
    actionBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const actionId = btn.dataset.action;
        const action = actions.find(a => a.id === actionId);
        if (action && action.callback) {
          action.callback();
        }
        if (!action || action.closeOnClick !== false) {
          this.close(toast);
        }
      });
    });
    
    // Auto close after duration (unless persistent)
    if (duration > 0 && !persistent) {
      const timeoutId = setTimeout(() => {
        this.close(toast);
      }, duration);
      
      // Pause auto-close on hover
      toast.addEventListener('mouseenter', () => {
        clearTimeout(timeoutId);
      });
      
      toast.addEventListener('mouseleave', () => {
        setTimeout(() => {
          this.close(toast);
        }, 1000); // Give 1 second after mouse leave
      });
    }
    
    // Add swipe to dismiss on mobile
    this.addSwipeGesture(toast);
    
    return toast;
  }
  
  addSwipeGesture(toast) {
    let startX = 0;
    let currentX = 0;
    let isDragging = false;
    
    toast.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
      isDragging = true;
      toast.style.transition = 'none';
    });
    
    toast.addEventListener('touchmove', (e) => {
      if (!isDragging) return;
      
      currentX = e.touches[0].clientX;
      const diffX = currentX - startX;
      
      if (diffX > 0) {
        toast.style.transform = `translateX(${diffX}px)`;
        toast.style.opacity = Math.max(0.3, 1 - (diffX / 200));
      }
    });
    
    toast.addEventListener('touchend', () => {
      if (!isDragging) return;
      
      const diffX = currentX - startX;
      toast.style.transition = 'transform 0.3s ease, opacity 0.3s ease';
      
      if (diffX > 100) {
        // Swipe right to dismiss
        this.close(toast);
      } else {
        // Snap back
        toast.style.transform = 'translateX(0)';
        toast.style.opacity = '1';
      }
      
      isDragging = false;
    });
  }
  
  close(toast) {
    toast.classList.remove('show');
    
    // Remove after animation completes
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }
  
  // Convenience methods
  success(title, message = '', duration = 3000) {
    return this.show({ title, message, type: 'success', duration });
  }
  
  error(title, message = '', duration = 4000) {
    return this.show({ title, message, type: 'error', duration });
  }
  
  warning(title, message = '', duration = 3500) {
    return this.show({ title, message, type: 'warning', duration });
  }
  
  info(title, message = '', duration = 3000) {
    return this.show({ title, message, type: 'info', duration });
  }
}

// API Communication
class ApiClient {
  async post(url, data, options = {}) {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        body: JSON.stringify(data)
      });
      
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      return { success: false, error: 'Network error occurred' };
    }
  }
  
  async postForm(form) {
    try {
      const formData = new FormData(form);
      
      const response = await fetch(form.action, {
        method: 'POST',
        body: formData
      });
      
      return await response.json();
    } catch (error) {
      console.error('Form Submission Error:', error);
      return { success: false, error: 'Network error occurred' };
    }
  }
  
  async get(url, options = {}) {
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: options.headers || {}
      });
      
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      return { success: false, error: 'Network error occurred' };
    }
  }
}

// Form Submission Handler
class FormHandler {
  constructor() {
    this.api = new ApiClient();
    this.toast = new ToastManager();
    this.init();
  }
  
  init() {
    // Handle generate form submission
    const genForm = document.getElementById('genForm');
    if (genForm) {
      genForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.handleGenerateForm(genForm);
      });
    }
    
    // Handle import form submission
    const importForm = document.getElementById('importForm');
    if (importForm) {
      importForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.handleImportForm(importForm);
      });
    }
    
    // Handle settings form submission
    const settingsForm = document.getElementById('settingsForm');
    if (settingsForm) {
      settingsForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.handleSettingsForm(settingsForm);
      });
    }
    
    // Handle login form submission
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.handleLoginForm(loginForm);
      });
    }
  }
  
  async handleGenerateForm(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = 'Generating...';
    
    // Submit form
    const response = await this.api.postForm(form);
    
    // Reset button
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalText;
    
    // Handle response
    if (response.success) {
      this.toast.success('Invoices Generated', `Successfully created ${response.count || ''} invoices.`);
    } else {
      this.toast.error('Generation Failed', response.error || 'An error occurred during invoice generation.');
    }
  }
  
  async handleImportForm(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = 'Importing...';
    
    // Submit form
    const response = await this.api.postForm(form);
    
    // Reset button
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalText;
    
    // Handle response
    if (response.success) {
      this.toast.success('Import Successful', `Successfully imported ${response.count || ''} records.`);
    } else {
      this.toast.error('Import Failed', response.error || 'An error occurred during import.');
    }
  }
  
  async handleSettingsForm(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = 'Saving...';
    
    // Submit form
    const response = await this.api.postForm(form);
    
    // Reset button
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalText;
    
    // Handle response
    if (response.success) {
      this.toast.success('Settings Saved', 'Your settings have been updated successfully.');
    } else {
      this.toast.error('Save Failed', response.error || 'An error occurred while saving settings.');
    }
  }
  
  async handleLoginForm(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = 'Logging in...';
    
    // Submit form
    const response = await this.api.postForm(form);
    
    // Handle response
    if (response.success) {
      // Redirect to dashboard on success
      window.location.href = response.redirect || '/dashboard';
    } else {
      // Reset button
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
      
      // Show error
      this.toast.error('Login Failed', response.error || 'Invalid credentials.');
      
      // Highlight password field
      const passcodeField = form.querySelector('input[type="password"]');
      if (passcodeField) {
        passcodeField.classList.add('error');
        passcodeField.focus();
        
        // Remove error class after a delay
        setTimeout(() => {
          passcodeField.classList.remove('error');
        }, 3000);
      }
    }
  }
}

// Initialize all components when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  // Initialize theme manager
  window.themeManager = new ThemeManager();
  
  // Initialize responsive manager (replaces sidebar manager)
  window.responsiveManager = new ResponsiveManager();
  
  // Initialize form components
  window.formComponents = new FormComponents();
  
  // Initialize toast manager
  window.toastManager = new ToastManager();
  
  // Initialize form handler
  window.formHandler = new FormHandler();
  
  // Set active navigation item
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(item => {
    const href = item.getAttribute('href');
    if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
      item.classList.add('active');
    }
  });
  
  // Initialize touch gestures for mobile
  if (window.responsiveManager) {
    window.responsiveManager.initTouchGestures();
  }
});