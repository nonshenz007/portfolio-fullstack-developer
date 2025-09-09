# Error Handling & Fallback States Matrix

## Overview

This document defines comprehensive error handling strategies for the premium UI redesign, covering all failure scenarios with specific user-facing copy, component visuals, ARIA live regions, and retry logic. Each error state maintains the premium brand aesthetic while providing clear user guidance.

## Error State Categories

### 1. Image Load Failures

#### Hero Image Load Failure

**Scenario:** Primary hero background image fails to load

**User-Facing Copy:**
- Primary: "Exploring destinations..."
- Secondary: "Loading your personalized travel experience"

**Component Visual:**
```html
<div class="hero-fallback">
  <!-- Gradient background matching brand -->
  <div class="bg-gradient-to-br from-cool/20 via-ink/40 to-ink/80 min-h-[85vh] md:min-h-[90vh]">
    <!-- Grain texture overlay -->
    <div class="absolute inset-0 opacity-[0.025] bg-[url('/grain.svg')] mix-blend-overlay"></div>
    
    <!-- Content with loading state -->
    <div class="hero-content">
      <p class="text-cool">Hi {name},</p>
      <h1 class="text-surface">Plan less. Travel more.</h1>
      <p class="text-slate">Trips made personal.</p>
      
      <!-- Loading indicator -->
      <div class="mt-8 flex items-center text-cloud">
        <svg class="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
        </svg>
        <span class="text-small">Exploring destinations...</span>
      </div>
    </div>
  </div>
</div>
```

**ARIA Live Region:**
```html
<div aria-live="polite" aria-atomic="true" class="sr-only">
  Hero image loading. Showing fallback background.
</div>
```

**Retry Logic:**
- Automatic retry after 3 seconds
- Maximum 2 retry attempts
- Fallback to gradient background permanently after failures
- Log error for monitoring

#### Editorial Tile Image Failure

**Scenario:** Package tile image fails to load

**User-Facing Copy:**
- Placeholder text: "Image loading..."
- Alt text: "Travel destination preview"

**Component Visual:**
```html
<div class="tile-image-fallback aspect-[4/3] rounded-2xl bg-gradient-to-br from-cloud/20 to-slate/30 flex items-center justify-center">
  <!-- Icon placeholder -->
  <div class="text-center">
    <svg class="w-12 h-12 mx-auto text-slate/60 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" 
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
    </svg>
    <p class="text-small text-slate/80">Image loading...</p>
  </div>
</div>
```

**ARIA Live Region:**
```html
<div aria-live="polite" class="sr-only">
  Package image failed to load. Showing placeholder.
</div>
```

**Retry Logic:**
- Single retry attempt after 2 seconds
- Permanent placeholder if retry fails
- Maintain tile functionality and interactions

### 2. API Failures

#### Package Loading Failure

**Scenario:** API call to fetch packages fails

**User-Facing Copy:**
- Primary: "Unable to load travel packages"
- Secondary: "We're having trouble connecting to our servers. Please check your connection and try again."
- Action: "Try Again"

**Component Visual:**
```html
<div class="error-state py-16 text-center">
  <!-- Error icon -->
  <div class="mb-6">
    <svg class="w-16 h-16 mx-auto text-slate/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" 
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
    </svg>
  </div>
  
  <!-- Error message -->
  <h3 class="text-h3 text-ink mb-4">Unable to load travel packages</h3>
  <p class="text-body text-slate mb-8 max-w-md mx-auto">
    We're having trouble connecting to our servers. Please check your connection and try again.
  </p>
  
  <!-- Retry button -->
  <button type="button" 
          class="btn-warm focus:ring-2 focus:ring-cool"
          onclick="retryPackageLoad()">
    Try Again
  </button>
  
  <!-- Alternative action -->
  <p class="mt-4">
    <a href="/contact" class="text-cool hover:underline focus:ring-2 focus:ring-cool">
      Contact support if the problem persists
    </a>
  </p>
</div>
```

**ARIA Live Region:**
```html
<div role="alert" aria-atomic="true">
  Error loading travel packages. Try again button available.
</div>
```

**Retry Logic:**
- Manual retry via button click
- Exponential backoff: 1s, 2s, 4s delays
- Maximum 3 retry attempts
- Show contact support after final failure

#### Search API Failure

**Scenario:** Search request fails or times out

**User-Facing Copy:**
- Primary: "Search temporarily unavailable"
- Secondary: "Please try your search again in a moment."
- Action: "Retry Search"

**Component Visual:**
```html
<div class="search-error bg-surface border border-cloud/30 rounded-2xl p-6 mt-4">
  <div class="flex items-start">
    <!-- Warning icon -->
    <svg class="w-5 h-5 text-warm mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
    </svg>
    
    <!-- Error content -->
    <div class="flex-1">
      <h4 class="text-small font-semibold text-ink mb-1">Search temporarily unavailable</h4>
      <p class="text-small text-slate mb-3">Please try your search again in a moment.</p>
      
      <button type="button" 
              class="text-small text-cool hover:underline focus:ring-2 focus:ring-cool"
              onclick="retrySearch()">
        Retry Search
      </button>
    </div>
  </div>
</div>
```

**ARIA Live Region:**
```html
<div role="alert">
  Search failed. Retry search button available.
</div>
```

**Retry Logic:**
- Automatic retry after 2 seconds
- Manual retry via button
- Clear error state on successful retry
- Maintain search input value

### 3. Network Connectivity Issues

#### Offline State

**Scenario:** User loses internet connection

**User-Facing Copy:**
- Primary: "You're currently offline"
- Secondary: "Some features may not be available. We'll reconnect automatically when your connection is restored."
- Status: "Reconnecting..." (when attempting)

**Component Visual:**
```html
<div class="offline-banner bg-slate text-surface px-4 py-3 text-center">
  <div class="flex items-center justify-center">
    <!-- Offline icon -->
    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
            d="M18.364 5.636l-12.728 12.728m0 0L12 12m-6.364 6.364L12 12m6.364-6.364L12 12"/>
    </svg>
    
    <span class="text-small font-medium">You're currently offline</span>
    
    <!-- Reconnecting indicator (when attempting) -->
    <div class="ml-3 hidden" id="reconnecting-indicator">
      <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
      </svg>
      <span class="ml-2 text-small">Reconnecting...</span>
    </div>
  </div>
</div>
```

**ARIA Live Region:**
```html
<div aria-live="assertive" aria-atomic="true">
  You are currently offline. Some features may not be available.
</div>

<!-- When reconnecting -->
<div aria-live="polite">
  Attempting to reconnect...
</div>

<!-- When back online -->
<div aria-live="polite">
  Connection restored. All features are now available.
</div>
```

**Retry Logic:**
- Automatic connection detection
- Retry network requests when back online
- Cache user actions for replay when connected
- Show reconnection attempts to user

#### Slow Connection Timeout

**Scenario:** Request takes longer than 10 seconds

**User-Facing Copy:**
- Primary: "This is taking longer than usual"
- Secondary: "Your connection seems slow. We're still working on loading your content."
- Actions: "Keep Waiting" | "Try Again"

**Component Visual:**
```html
<div class="slow-connection-notice bg-cloud/10 border border-cloud/30 rounded-2xl p-6 mt-4">
  <div class="text-center">
    <!-- Loading icon -->
    <div class="mb-4">
      <svg class="animate-pulse w-12 h-12 mx-auto text-slate/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" 
              d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707"/>
      </svg>
    </div>
    
    <h4 class="text-small font-semibold text-ink mb-2">This is taking longer than usual</h4>
    <p class="text-small text-slate mb-4">Your connection seems slow. We're still working on loading your content.</p>
    
    <!-- Action buttons -->
    <div class="flex gap-3 justify-center">
      <button type="button" 
              class="btn-outline-cool text-small px-4 py-2"
              onclick="continueWaiting()">
        Keep Waiting
      </button>
      <button type="button" 
              class="btn-warm text-small px-4 py-2"
              onclick="retryRequest()">
        Try Again
      </button>
    </div>
  </div>
</div>
```

**ARIA Live Region:**
```html
<div aria-live="polite" aria-atomic="true">
  Request is taking longer than usual due to slow connection. Keep waiting or try again options available.
</div>
```

**Retry Logic:**
- Show notice after 10 seconds
- Allow user to continue waiting or retry
- Implement request timeout at 30 seconds
- Provide feedback on retry attempts

### 4. Empty Results States

#### No Search Results

**Scenario:** Search query returns no matching packages

**User-Facing Copy:**
- Primary: "No trips match your search"
- Secondary: "Try adjusting your filters or search terms to find more options."
- Suggestions: "Popular destinations: Kashmir, Goa, Dubai, Thailand"
- Action: "Clear Filters" | "Browse All Trips"

**Component Visual:**
```html
<div class="empty-results py-16 text-center">
  <!-- Background with subtle pattern -->
  <div class="relative">
    <!-- Decorative background -->
    <div class="absolute inset-0 bg-gradient-to-br from-surface to-cloud/10 rounded-3xl"></div>
    
    <!-- Content -->
    <div class="relative px-8">
      <!-- Illustration -->
      <div class="mb-8">
        <svg class="w-24 h-24 mx-auto text-slate/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" 
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
      </div>
      
      <!-- Message -->
      <h3 class="text-h3 text-ink mb-4">No trips match your search</h3>
      <p class="text-body text-slate mb-6 max-w-md mx-auto">
        Try adjusting your filters or search terms to find more options.
      </p>
      
      <!-- Suggestions -->
      <div class="mb-8">
        <p class="text-small text-slate mb-3">Popular destinations:</p>
        <div class="flex flex-wrap gap-2 justify-center">
          <button class="chip-suggestion" onclick="searchDestination('Kashmir')">Kashmir</button>
          <button class="chip-suggestion" onclick="searchDestination('Goa')">Goa</button>
          <button class="chip-suggestion" onclick="searchDestination('Dubai')">Dubai</button>
          <button class="chip-suggestion" onclick="searchDestination('Thailand')">Thailand</button>
        </div>
      </div>
      
      <!-- Actions -->
      <div class="flex gap-3 justify-center">
        <button type="button" 
                class="btn-outline-cool"
                onclick="clearAllFilters()">
          Clear Filters
        </button>
        <a href="/explore" class="btn-warm">
          Browse All Trips
        </a>
      </div>
    </div>
  </div>
</div>
```

**ARIA Live Region:**
```html
<div aria-live="polite" aria-atomic="true">
  No trips found matching your search criteria. Suggestions and filter options available.
</div>
```

**Retry Logic:**
- Suggest popular destinations
- Offer to clear filters
- Track empty result queries for improvement

#### No Packages Available

**Scenario:** No packages exist in the system (rare edge case)

**User-Facing Copy:**
- Primary: "We're preparing amazing trips for you"
- Secondary: "Our travel experts are curating new destinations. Check back soon for exciting packages!"
- Action: "Notify Me" | "Contact Us"

**Component Visual:**
```html
<div class="no-packages py-20 text-center">
  <div class="max-w-lg mx-auto">
    <!-- Illustration -->
    <div class="mb-8">
      <svg class="w-32 h-32 mx-auto text-cool/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" 
              d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064"/>
      </svg>
    </div>
    
    <h2 class="text-h2 text-ink mb-4">We're preparing amazing trips for you</h2>
    <p class="text-body text-slate mb-8">
      Our travel experts are curating new destinations. Check back soon for exciting packages!
    </p>
    
    <!-- Actions -->
    <div class="flex gap-3 justify-center">
      <button type="button" 
              class="btn-warm"
              onclick="subscribeToUpdates()">
        Notify Me
      </button>
      <a href="/contact" class="btn-outline-cool">
        Contact Us
      </a>
    </div>
  </div>
</div>
```

**ARIA Live Region:**
```html
<div aria-live="polite">
  No packages currently available. Notification signup and contact options provided.
</div>
```

### 5. Reduced Motion Preferences

#### Animation Fallbacks

**Scenario:** User has `prefers-reduced-motion: reduce` set

**User-Facing Copy:**
- No specific copy needed
- Maintain all text content

**Component Visual:**
```css
/* Reduced motion styles */
@media (prefers-reduced-motion: reduce) {
  /* Disable Ken Burns effect */
  .hero-background {
    animation: none;
    transform: scale(1.01); /* Slight scale for depth */
  }
  
  /* Simplify transitions */
  .tile-hover-content {
    transition: opacity 0.15s ease;
    transform: none;
  }
  
  /* Remove complex animations */
  .loading-spinner {
    animation: none;
  }
  
  /* Keep essential feedback */
  .focus-ring {
    transition: box-shadow 0.15s ease;
  }
}
```

**ARIA Live Region:**
```html
<!-- No specific announcements needed -->
<!-- Existing content remains accessible -->
```

**Implementation Notes:**
- Maintain all functionality
- Reduce animation duration and complexity
- Keep essential visual feedback (focus rings, state changes)
- Test with motion preferences enabled

### 6. Slow Device Performance

#### Performance Degradation

**Scenario:** Device struggles with animations or complex layouts

**User-Facing Copy:**
- Subtle notification: "Optimizing experience for your device"
- No prominent error messaging

**Component Visual:**
```html
<!-- Simplified tile layout for slow devices -->
<div class="tile-simplified" data-performance-mode="reduced">
  <!-- Reduced shadow complexity -->
  <div class="tile-image shadow-e1"> <!-- Instead of e2 -->
    <img loading="lazy" decoding="async" />
  </div>
  
  <!-- Simplified hover states -->
  <div class="tile-content">
    <!-- Static content, no complex animations -->
  </div>
</div>
```

**ARIA Live Region:**
```html
<div aria-live="polite" class="sr-only">
  Experience optimized for your device performance.
</div>
```

**Performance Adaptations:**
- Reduce animation complexity
- Simplify shadow effects
- Lazy load more aggressively
- Reduce image quality on slow devices
- Disable non-essential animations

## Error Recovery Patterns

### Progressive Enhancement Strategy

1. **Core Functionality First**
   - Ensure basic navigation works without JavaScript
   - Provide fallback styles for CSS failures
   - Maintain semantic HTML structure

2. **Graceful Degradation**
   - Advanced features fail silently
   - Core content remains accessible
   - Alternative interaction methods available

3. **Error Boundary Implementation**
```javascript
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log error for monitoring
    console.error('Component error:', error, errorInfo);
    
    // Send to error tracking service
    trackError(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary p-8 text-center">
          <h3 className="text-h3 text-ink mb-4">Something went wrong</h3>
          <p className="text-body text-slate mb-6">
            We're sorry for the inconvenience. Please refresh the page to try again.
          </p>
          <button 
            className="btn-warm"
            onClick={() => window.location.reload()}>
            Refresh Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### Retry Logic Specifications

**Exponential Backoff Pattern:**
```javascript
const retryWithBackoff = async (fn, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      
      const delay = Math.pow(2, i) * 1000; // 1s, 2s, 4s
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
};
```

**User-Initiated Retry:**
```javascript
const handleRetry = async (retryFunction, errorStateId) => {
  // Show loading state
  updateErrorState(errorStateId, { loading: true });
  
  // Announce to screen readers
  announceToScreenReader('Retrying request...');
  
  try {
    await retryFunction();
    
    // Clear error state
    clearErrorState(errorStateId);
    announceToScreenReader('Request successful');
    
  } catch (error) {
    // Update error state
    updateErrorState(errorStateId, { 
      loading: false, 
      error: error.message,
      retryCount: (state.retryCount || 0) + 1
    });
    
    announceToScreenReader('Request failed. Please try again.');
  }
};
```

## Monitoring and Analytics

### Error Tracking Requirements

**Essential Error Data:**
- Error type and message
- Component/page where error occurred
- User agent and device information
- Network conditions (if available)
- User actions leading to error
- Recovery success rate

**Performance Monitoring:**
- Image load failure rates
- API response times and failure rates
- Client-side error frequency
- User retry behavior patterns

**Accessibility Monitoring:**
- Screen reader usage patterns
- Keyboard navigation success rates
- Focus management issues
- Reduced motion preference adoption

This comprehensive error matrix ensures that the premium UI redesign handles all failure scenarios gracefully while maintaining the sophisticated brand experience and accessibility standards.