# Analytics Events Taxonomy - Premium UI Redesign

## Overview

This document defines the comprehensive analytics event taxonomy for TripChoice's premium UI redesign. The taxonomy captures user interactions across the redesigned interface to measure engagement, optimize user experience, and inform product decisions while maintaining strict privacy compliance.

## Event Naming Convention

### Structure
`[action]_[object]_[context]` (snake_case)

### Categories
- **Search Events:** User search and discovery actions
- **Package Events:** Package viewing and interaction events  
- **Filter Events:** Filter application and modification events
- **Engagement Events:** UI interaction and engagement events
- **Conversion Events:** Actions leading toward booking intent

## Core Event Definitions

### 1. Search Events

#### `search_performed`
**Description:** Fired when user executes a search query
**Trigger:** Search input submission or search button click
**Location:** Homepage search band, Explore page search bar

**Payload Schema:**
```json
{
  "event": "search_performed",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "session_id": "sess_abc123",
  "user_id": "user_xyz789", // Optional, only if authenticated
  "page_path": "/",
  "data": {
    "query": "bali honeymoon",
    "query_length": 13,
    "search_type": "text", // "text" | "voice" | "suggestion"
    "filters_applied": {
      "theme": ["honeymoon"],
      "budget_max": 50000,
      "duration_days": null,
      "domestic": false,
      "departure_city": null
    },
    "results_count": 24,
    "search_source": "homepage_hero" // "homepage_hero" | "explore_search" | "header_search"
  }
}
```

**Privacy Notes:**
- Search queries may contain PII - implement data retention policies
- Consider hashing sensitive search terms
- Exclude personal information from query logging

#### `search_suggestion_clicked`
**Description:** User clicks on search autocomplete suggestion
**Trigger:** Click on dropdown suggestion item

**Payload Schema:**
```json
{
  "event": "search_suggestion_clicked",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "session_id": "sess_abc123",
  "data": {
    "suggestion": "bali",
    "suggestion_type": "destination", // "destination" | "theme" | "package"
    "position": 2,
    "partial_query": "ba"
  }
}
```

### 2. Package Events

#### `package_viewed`
**Description:** User views package details
**Trigger:** Click on package tile or navigation to package page
**Location:** Homepage tiles, Explore grid, Search results

**Payload Schema:**
```json
{
  "event": "package_viewed",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "session_id": "sess_abc123",
  "user_id": "user_xyz789", // Optional
  "page_path": "/explore",
  "data": {
    "package_slug": "bali-honeymoon-5d4n",
    "package_id": "pkg_001",
    "package_title": "Bali Honeymoon Escape",
    "destination": "Bali",
    "duration_days": 5,
    "price_inr": 45000,
    "themes": ["honeymoon", "beaches", "luxury"],
    "domestic": false,
    "view_source": "explore_grid", // "homepage_tile" | "explore_grid" | "search_results"
    "position_in_grid": 3,
    "total_results": 24
  }
}
```

#### `package_image_clicked`
**Description:** User clicks on package image in tile
**Trigger:** Click on image area of package tile

**Payload Schema:**
```json
{
  "event": "package_image_clicked",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "session_id": "sess_abc123",
  "data": {
    "package_slug": "bali-honeymoon-5d4n",
    "image_position": 1, // If carousel
    "interaction_type": "click" // "click" | "hover" | "swipe"
  }
}
```

### 3. Variant Selection Events

#### `variant_selected`
**Description:** User selects transport variant (Flight/Train/Bus)
**Trigger:** Click on transport tab in package tile hover state
**Location:** Package tiles on hover

**Payload Schema:**
```json
{
  "event": "variant_selected",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "session_id": "sess_abc123",
  "data": {
    "package_slug": "goa-weekend-3d2n",
    "variant_type": "flight", // "flight" | "train" | "bus"
    "previous_variant": "train",
    "price_difference": 5000,
    "selection_method": "hover_tab" // "hover_tab" | "package_page" | "comparison"
  }
}
```

### 4. WhatsApp Engagement Events

#### `whatsapp_clicked`
**Description:** User clicks WhatsApp CTA button
**Trigger:** Click on WhatsApp button in tiles or package pages
**Location:** Package tiles, Package detail pages

**Payload Schema:**
```json
{
  "event": "whatsapp_clicked",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "session_id": "sess_abc123",
  "data": {
    "package_slug": "kerala-backwaters-4d3n",
    "click_source": "tile_hover", // "tile_hover" | "package_page" | "price_box"
    "variant_type": "flight",
    "price_inr": 32000,
    "payload": {
      "message_template": "inquiry",
      "package_url": "https://tripchoice.com/package/kerala-backwaters-4d3n",
      "user_preferences": {
        "departure_city": "Mumbai",
        "travel_dates": "2025-03-15"
      }
    }
  }
}
```

### 5. Filter Events

#### `filter_applied`
**Description:** User applies or modifies filters
**Trigger:** Filter chip selection, dropdown changes, slider adjustments
**Location:** Homepage search band, Explore page filter rail

**Payload Schema:**
```json
{
  "event": "filter_applied",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "session_id": "sess_abc123",
  "page_path": "/explore",
  "data": {
    "filter_type": "theme", // "theme" | "budget" | "duration" | "domestic" | "departure_city"
    "filter_value": "honeymoon",
    "action": "add", // "add" | "remove" | "change"
    "previous_value": null,
    "filters_state": {
      "themes": ["honeymoon", "luxury"],
      "budget_max": 75000,
      "duration_days": null,
      "domestic": false,
      "departure_city": "Mumbai"
    },
    "results_count_before": 156,
    "results_count_after": 24,
    "filter_source": "chip_click" // "chip_click" | "dropdown" | "slider" | "toggle"
  }
}
```

#### `filters_cleared`
**Description:** User resets all filters
**Trigger:** Click on "Clear all filters" or "Reset filters" button

**Payload Schema:**
```json
{
  "event": "filters_cleared",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "session_id": "sess_abc123",
  "data": {
    "cleared_filters": {
      "themes": ["honeymoon", "mountains"],
      "budget_max": 50000,
      "duration_days": 7,
      "domestic": true
    },
    "clear_source": "empty_state", // "empty_state" | "filter_rail" | "search_band"
    "results_count_before": 0,
    "results_count_after": 156
  }
}
```

### 6. UI Interaction Events

#### `hero_animation_completed`
**Description:** Cinematic hero animation sequence completes
**Trigger:** Ken Burns animation cycle completion
**Location:** Homepage hero section

**Payload Schema:**
```json
{
  "event": "hero_animation_completed",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "session_id": "sess_abc123",
  "data": {
    "animation_duration": 7000,
    "hero_image": "mountain-lake-golden-hour.webp",
    "user_interaction_during": false, // Did user interact during animation
    "viewport_visible": true // Was hero in viewport during animation
  }
}
```

#### `tile_hover_engaged`
**Description:** User hovers over package tile and reveals transport options
**Trigger:** Hover state activation showing transport tabs and CTAs

**Payload Schema:**
```json
{
  "event": "tile_hover_engaged",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "session_id": "sess_abc123",
  "data": {
    "package_slug": "rajasthan-royal-6d5n",
    "hover_duration": 2300, // milliseconds
    "interactions": ["variant_tab_viewed", "whatsapp_button_visible"],
    "position_in_grid": 5
  }
}
```

#### `flash_deal_clicked`
**Description:** User clicks on flash deals banner
**Trigger:** Click on flash deals strip
**Location:** Homepage flash deals banner

**Payload Schema:**
```json
{
  "event": "flash_deal_clicked",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "session_id": "sess_abc123",
  "data": {
    "deal_id": "flash_2025_jan",
    "time_remaining": "02:14:35:22", // DD:HH:MM:SS
    "deal_discount": 25,
    "packages_count": 12
  }
}
```

### 7. Navigation Events

#### `explore_page_visited`
**Description:** User navigates to explore page
**Trigger:** Page load of /explore
**Location:** Explore page

**Payload Schema:**
```json
{
  "event": "explore_page_visited",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "session_id": "sess_abc123",
  "data": {
    "referrer": "homepage", // "homepage" | "direct" | "search_engine" | "social"
    "entry_filters": {
      "theme": "mountains"
    },
    "device_type": "desktop", // "desktop" | "tablet" | "mobile"
    "initial_results_count": 89
  }
}
```

#### `sort_option_changed`
**Description:** User changes sort order on explore page
**Trigger:** Selection from sort dropdown

**Payload Schema:**
```json
{
  "event": "sort_option_changed",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "session_id": "sess_abc123",
  "data": {
    "sort_option": "price_low_high", // "popularity" | "price_low_high" | "price_high_low" | "duration"
    "previous_sort": "popularity",
    "results_count": 45
  }
}
```

## Privacy & Compliance

### Data Retention Policies
- **Session Data:** 90 days retention
- **Search Queries:** 30 days retention (hash sensitive terms)
- **User Interactions:** 1 year retention for authenticated users
- **Anonymous Analytics:** 2 years retention

### PII Avoidance Guidelines
- **Never Log:** Email addresses, phone numbers, full names, payment info
- **Hash When Necessary:** Search queries containing personal information
- **Anonymize:** IP addresses after geolocation extraction
- **Consent Required:** For authenticated user tracking

### GDPR Compliance
- Implement data subject deletion requests
- Provide data export functionality
- Maintain consent records
- Regular data audit and cleanup

## Implementation Guidelines

### Event Firing Timing
- **Immediate:** User clicks, form submissions, navigation
- **Debounced:** Search input (300ms delay), filter changes
- **Batched:** Scroll events, hover interactions (send every 5 seconds)
- **Session End:** Aggregate session metrics

### Error Handling
```javascript
// Graceful analytics failure
function trackEvent(eventName, payload) {
  try {
    analytics.track(eventName, payload);
  } catch (error) {
    console.warn('Analytics tracking failed:', error);
    // Don't break user experience
  }
}
```

### Testing Strategy
- **Development:** Use analytics debug mode
- **Staging:** Separate analytics property
- **Production:** Implement sampling for high-volume events
- **Validation:** Regular data quality audits

## Sample Implementation

### React Hook Example
```javascript
import { useAnalytics } from '@/hooks/useAnalytics';

function PackageTile({ package }) {
  const { track } = useAnalytics();
  
  const handlePackageClick = () => {
    track('package_viewed', {
      package_slug: package.slug,
      package_id: package.id,
      package_title: package.title,
      destination: package.destination,
      duration_days: package.duration,
      price_inr: package.price,
      themes: package.themes,
      domestic: package.domestic,
      view_source: 'explore_grid',
      position_in_grid: package.position,
      total_results: package.totalResults
    });
  };
  
  const handleWhatsAppClick = () => {
    track('whatsapp_clicked', {
      package_slug: package.slug,
      click_source: 'tile_hover',
      variant_type: selectedVariant,
      price_inr: package.variants[selectedVariant].price,
      payload: {
        message_template: 'inquiry',
        package_url: `${window.location.origin}/package/${package.slug}`
      }
    });
  };
  
  return (
    <div onClick={handlePackageClick}>
      {/* Tile content */}
      <button onClick={handleWhatsAppClick}>
        WhatsApp
      </button>
    </div>
  );
}
```

### Analytics Context Provider
```javascript
const AnalyticsContext = createContext();

export function AnalyticsProvider({ children }) {
  const track = useCallback((event, data) => {
    const payload = {
      event,
      timestamp: new Date().toISOString(),
      session_id: getSessionId(),
      user_id: getCurrentUserId(), // Optional
      page_path: window.location.pathname,
      data
    };
    
    // Send to analytics service
    sendAnalyticsEvent(payload);
  }, []);
  
  return (
    <AnalyticsContext.Provider value={{ track }}>
      {children}
    </AnalyticsContext.Provider>
  );
}
```

## Quality Assurance Checklist

### Event Validation
- [ ] All required fields present in payload
- [ ] Data types match schema definitions
- [ ] No PII in event data
- [ ] Timestamp format consistent (ISO 8601)
- [ ] Session ID properly maintained

### Privacy Compliance
- [ ] User consent obtained for tracking
- [ ] Data retention policies implemented
- [ ] PII scrubbing functions active
- [ ] GDPR deletion requests supported
- [ ] Analytics opt-out functionality working

### Performance Impact
- [ ] Event batching implemented for high-frequency events
- [ ] Analytics failures don't break user experience
- [ ] Network requests optimized and compressed
- [ ] Client-side buffering for offline scenarios

### Testing Coverage
- [ ] All events fire correctly in development
- [ ] Staging environment receives test events
- [ ] Production sampling rates configured
- [ ] Data quality monitoring alerts set up
- [ ] Regular analytics data audits scheduled

This analytics taxonomy provides comprehensive tracking for the premium UI redesign while maintaining user privacy and optimal performance.