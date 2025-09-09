# Accessibility ARIA Map & Keyboard Flow

## Overview

This document defines the ARIA structure, keyboard navigation flows, focus management, and accessibility requirements for the premium UI redesign of TripChoice. All components must meet WCAG 2.1 AA standards with specific attention to the cinematic design elements.

## Component ARIA Maps

### 1. Header Component

**ARIA Structure:**
```html
<header role="banner" aria-label="Site navigation">
  <nav role="navigation" aria-label="Primary navigation">
    <!-- Logo (conditional) -->
    <a href="/" aria-label="TripChoice home" class="focus:ring-2 focus:ring-cool">
      <img src="/logo.svg" alt="TripChoice" />
    </a>
    
    <!-- Right navigation -->
    <div role="group" aria-label="User navigation">
      <a href="/explore" 
         class="focus:ring-2 focus:ring-cool"
         aria-describedby="explore-hint">
        Explore
      </a>
      <span id="explore-hint" class="sr-only">Browse travel packages</span>
      
      <div role="button" 
           tabindex="0"
           aria-label="User menu for {name}"
           aria-expanded="false"
           aria-haspopup="menu"
           class="focus:ring-2 focus:ring-cool">
        Hi {name}
      </div>
    </div>
  </nav>
</header>
```

**Keyboard Navigation:**
- Tab order: Logo → Explore link → User menu
- Focus indicators: 2px cool color ring (`focus:ring-2 focus:ring-cool`)
- Touch targets: Minimum 44px × 44px
- Escape key: Close user menu if expanded

**Focus Management:**
- Initial focus: First focusable element (logo or explore link)
- Focus trap: Within user menu when expanded
- Focus restoration: Return to trigger element on menu close

### 2. Cinematic Hero Section

**ARIA Structure:**
```html
<section role="banner" 
         aria-labelledby="hero-heading"
         aria-describedby="hero-subtitle">
  
  <!-- Background image with proper alt text -->
  <div role="img" 
       aria-label="Cinematic travel destination: Mountain lake at golden hour with traveler silhouette"
       class="hero-background">
    
    <!-- Content overlay -->
    <div class="hero-content">
      <p aria-label="Personalized greeting" class="hero-greeting">
        Hi {name},
      </p>
      
      <h1 id="hero-heading" class="hero-title">
        Plan less. Travel more.
      </h1>
      
      <p id="hero-subtitle" class="hero-subtitle">
        Trips made personal.
      </p>
    </div>
  </div>
  
  <!-- Reduced motion alternative -->
  <div class="sr-only" aria-live="polite">
    Hero section loaded. Main heading: Plan less. Travel more.
  </div>
</section>
```

**Keyboard Navigation:**
- Non-interactive: Hero is informational only
- Skip link: Provided to jump to main content
- Reduced motion: Respects `prefers-reduced-motion`

**Focus Management:**
- No focus stops within hero
- Screen reader announces content on page load
- Proper heading hierarchy (H1 for main title)

### 3. Search Band Component

**ARIA Structure:**
```html
<section role="search" 
         aria-labelledby="search-heading"
         class="search-band">
  
  <h2 id="search-heading" class="sr-only">Search travel packages</h2>
  
  <!-- Search input -->
  <div class="search-input-group">
    <label for="destination-search" class="sr-only">
      Search destinations
    </label>
    <input type="search"
           id="destination-search"
           placeholder="Where do you want to go?"
           aria-describedby="search-help"
           class="focus:ring-2 focus:ring-cool"
           autocomplete="off"
           spellcheck="false" />
    
    <button type="submit" 
            aria-label="Search destinations"
            class="focus:ring-2 focus:ring-cool">
      <svg aria-hidden="true" focusable="false"><!-- search icon --></svg>
    </button>
    
    <div id="search-help" class="sr-only">
      Enter a destination name or select from filter options below
    </div>
  </div>
  
  <!-- Filter chips -->
  <div role="group" 
       aria-labelledby="filter-chips-label"
       class="filter-chips">
    
    <span id="filter-chips-label" class="sr-only">Quick filters</span>
    
    <button type="button"
            role="switch"
            aria-pressed="false"
            aria-describedby="weekend-desc"
            class="filter-chip focus:ring-2 focus:ring-cool">
      Weekend
    </button>
    <span id="weekend-desc" class="sr-only">Filter for weekend trips</span>
    
    <button type="button"
            role="switch"
            aria-pressed="false"
            aria-describedby="budget-desc"
            class="filter-chip focus:ring-2 focus:ring-cool">
      Under ₹15k
    </button>
    <span id="budget-desc" class="sr-only">Filter for trips under 15,000 rupees</span>
    
    <!-- Additional chips follow same pattern -->
  </div>
</section>
```

**Keyboard Navigation:**
- Tab order: Search input → Search button → Filter chips (left to right)
- Arrow keys: Navigate between filter chips
- Space/Enter: Toggle chip selection
- Escape: Clear search input focus

**Focus Management:**
- Initial focus: Search input (when navigating from hero)
- Chip selection: Visual and programmatic state changes
- Screen reader announcements: "Weekend filter activated" / "Weekend filter deactivated"

### 4. Editorial Tiles Component

**ARIA Structure:**
```html
<section aria-labelledby="editorial-heading" class="editorial-section">
  <h2 id="editorial-heading">Featured Destinations</h2>
  <p class="section-subtitle">Curated experiences for every traveler</p>
  
  <div role="grid" 
       aria-label="Travel packages grid"
       class="tiles-grid">
    
    <article role="gridcell"
             tabindex="0"
             aria-labelledby="tile-1-title"
             aria-describedby="tile-1-details"
             class="editorial-tile focus:ring-2 focus:ring-cool">
      
      <!-- Image -->
      <div class="tile-image">
        <img src="/images/destination.jpg"
             alt="Scenic mountain lake with golden hour lighting"
             loading="lazy" />
      </div>
      
      <!-- Content -->
      <div class="tile-content">
        <h3 id="tile-1-title" class="tile-title">Kashmir Valley</h3>
        
        <div id="tile-1-details" class="tile-metadata">
          <span aria-label="Location">
            <svg aria-hidden="true"><!-- pin icon --></svg>
            Srinagar, Kashmir
          </span>
          <span aria-label="Duration">
            <svg aria-hidden="true"><!-- clock icon --></svg>
            5 days
          </span>
          <span aria-label="Group size">
            <svg aria-hidden="true"><!-- pax icon --></svg>
            2-6 people
          </span>
        </div>
        
        <div class="tile-price" aria-label="Starting price">
          <span class="price-amount">₹25,999</span>
          <span class="price-unit">per person</span>
        </div>
      </div>
      
      <!-- Hover reveal content -->
      <div class="tile-actions" 
           aria-hidden="true"
           role="group"
           aria-label="Package options">
        
        <!-- Transport tabs -->
        <div role="tablist" 
             aria-label="Transport options"
             class="transport-tabs">
          <button role="tab"
                  aria-selected="true"
                  aria-controls="flight-content"
                  id="flight-tab"
                  class="focus:ring-2 focus:ring-cool">
            Flight
          </button>
          <button role="tab"
                  aria-selected="false"
                  aria-controls="train-content"
                  id="train-tab"
                  class="focus:ring-2 focus:ring-cool">
            Train
          </button>
        </div>
        
        <!-- Action buttons -->
        <div class="action-buttons">
          <a href="/package/kashmir-valley"
             class="view-details focus:ring-2 focus:ring-cool"
             aria-describedby="tile-1-title">
            View details
          </a>
          <button type="button"
                  class="whatsapp-btn focus:ring-2 focus:ring-cool"
                  aria-label="Contact us on WhatsApp about Kashmir Valley package">
            WhatsApp
          </button>
        </div>
      </div>
    </article>
    
    <!-- Additional tiles follow same pattern -->
  </div>
</section>
```

**Keyboard Navigation:**
- Tab order: Tiles left to right, top to bottom
- Enter/Space: Activate tile (show hover content)
- Arrow keys: Navigate between tiles in grid
- Tab within tile: Transport tabs → Action buttons
- Escape: Hide hover content, return focus to tile

**Focus Management:**
- Tile activation: Show hover content, focus first interactive element
- Tab navigation: Within revealed content (transport tabs → buttons)
- Focus restoration: Return to tile when hover content hidden
- Screen reader: Announce tile content and available actions

### 5. Explore Filters Component

**ARIA Structure:**
```html
<aside role="complementary" 
       aria-labelledby="filters-heading"
       class="explore-filters">
  
  <h2 id="filters-heading">Filter Options</h2>
  
  <!-- Search within filters -->
  <div class="filter-search">
    <label for="filter-destination" class="filter-label">
      Destination
    </label>
    <input type="search"
           id="filter-destination"
           class="focus:ring-2 focus:ring-cool"
           aria-describedby="filter-search-help" />
    <div id="filter-search-help" class="sr-only">
      Search for specific destinations
    </div>
  </div>
  
  <!-- Domestic/International toggle -->
  <fieldset class="filter-group">
    <legend>Trip Type</legend>
    <div role="radiogroup" aria-labelledby="trip-type-legend">
      <label class="radio-label">
        <input type="radio" 
               name="trip-type" 
               value="all"
               checked
               class="focus:ring-2 focus:ring-cool" />
        <span>All Trips</span>
      </label>
      <label class="radio-label">
        <input type="radio" 
               name="trip-type" 
               value="domestic"
               class="focus:ring-2 focus:ring-cool" />
        <span>Domestic</span>
      </label>
      <label class="radio-label">
        <input type="radio" 
               name="trip-type" 
               value="international"
               class="focus:ring-2 focus:ring-cool" />
        <span>International</span>
      </label>
    </div>
  </fieldset>
  
  <!-- Filter chips -->
  <fieldset class="filter-group">
    <legend>Themes</legend>
    <div role="group" class="filter-chips">
      <label class="chip-label">
        <input type="checkbox" 
               value="weekend"
               class="sr-only focus:ring-2 focus:ring-cool" />
        <span class="chip-visual" aria-hidden="true">Weekend</span>
        <span class="sr-only">Include weekend trips</span>
      </label>
      <!-- Additional chips follow same pattern -->
    </div>
  </fieldset>
  
  <!-- Clear filters -->
  <button type="button"
          class="clear-filters focus:ring-2 focus:ring-cool"
          aria-describedby="clear-help">
    Clear all filters
  </button>
  <div id="clear-help" class="sr-only">
    Remove all applied filters and show all results
  </div>
</aside>

<!-- Results section -->
<main role="main" aria-labelledby="results-heading">
  <div class="results-header">
    <h1 id="results-heading">
      <span aria-live="polite" aria-atomic="true">
        Showing {count} trips
      </span>
    </h1>
    
    <label for="sort-select" class="sort-label">Sort by</label>
    <select id="sort-select" 
            class="focus:ring-2 focus:ring-cool"
            aria-describedby="sort-help">
      <option value="popularity">Popularity</option>
      <option value="price-low">Price: Low to High</option>
      <option value="duration">Duration</option>
    </select>
    <div id="sort-help" class="sr-only">
      Change the order of search results
    </div>
  </div>
  
  <!-- Results grid -->
  <div role="region" 
       aria-label="Search results"
       aria-live="polite"
       class="results-grid">
    <!-- Tiles rendered here -->
  </div>
</main>
```

**Keyboard Navigation:**
- Tab order: Search → Radio buttons → Checkboxes → Clear button → Sort → Results
- Arrow keys: Navigate radio button groups
- Space: Toggle checkboxes
- Enter: Activate buttons and links

**Focus Management:**
- Filter changes: Announce result count changes
- Clear filters: Focus returns to first filter
- Sort changes: Maintain focus on sort dropdown
- Loading states: Announce "Loading results" to screen readers

## Reading Order & Landmarks

### Logical Reading Order
1. **Skip Links** (hidden, keyboard accessible)
   - "Skip to main content"
   - "Skip to navigation"
   - "Skip to search"

2. **Header** (`role="banner"`)
   - Logo (when present)
   - Primary navigation
   - User menu

3. **Hero Section** (`role="banner"` or `role="region"`)
   - Personalized greeting
   - Main heading (H1)
   - Subtitle

4. **Search Section** (`role="search"`)
   - Search input and button
   - Filter chips

5. **Main Content** (`role="main"`)
   - Section headings (H2)
   - Editorial tiles
   - Package grids

6. **Sidebar** (`role="complementary"`) - Explore page only
   - Filter controls
   - Sort options

7. **Footer** (`role="contentinfo"`)
   - Footer navigation
   - Legal information

### ARIA Landmarks Map
```html
<!-- Page structure -->
<body>
  <!-- Skip links -->
  <a href="#main-content" class="skip-link">Skip to main content</a>
  <a href="#search" class="skip-link">Skip to search</a>
  
  <!-- Header -->
  <header role="banner">
    <nav role="navigation" aria-label="Primary">
      <!-- Navigation content -->
    </nav>
  </header>
  
  <!-- Hero (homepage) -->
  <section role="banner" aria-labelledby="hero-heading">
    <!-- Hero content -->
  </section>
  
  <!-- Search -->
  <section role="search" id="search">
    <!-- Search content -->
  </section>
  
  <!-- Main content -->
  <main role="main" id="main-content">
    <!-- Page content -->
  </main>
  
  <!-- Sidebar (explore page) -->
  <aside role="complementary" aria-labelledby="filters-heading">
    <!-- Filter content -->
  </aside>
  
  <!-- Footer -->
  <footer role="contentinfo">
    <!-- Footer content -->
  </footer>
</body>
```

## Name, Role, Value Rules

### Interactive Elements

**Buttons:**
- **Name:** Visible text or `aria-label`
- **Role:** `button` (implicit or explicit)
- **Value:** Current state (`aria-pressed` for toggles)

```html
<!-- Filter chip example -->
<button type="button"
        role="switch"
        aria-pressed="false"
        aria-label="Weekend trips filter">
  Weekend
</button>
```

**Links:**
- **Name:** Link text or `aria-label`
- **Role:** `link` (implicit)
- **Value:** Current page indicator (`aria-current="page"`)

```html
<!-- Navigation link -->
<a href="/explore" 
   aria-current="page"
   aria-describedby="explore-desc">
  Explore
</a>
<span id="explore-desc" class="sr-only">Currently viewing explore page</span>
```

**Form Controls:**
- **Name:** Associated label or `aria-labelledby`
- **Role:** Input type (`textbox`, `checkbox`, `radio`)
- **Value:** Current input value or selection state

```html
<!-- Search input -->
<label for="search-input">Search destinations</label>
<input type="search"
       id="search-input"
       value=""
       aria-describedby="search-help" />
```

### Non-Interactive Elements

**Images:**
- **Name:** `alt` attribute or `aria-label`
- **Role:** `img` (implicit) or `presentation` for decorative

```html
<!-- Informative image -->
<img src="/hero-image.jpg"
     alt="Mountain lake at sunrise with traveler silhouette gazing at the horizon" />

<!-- Decorative image -->
<img src="/decoration.svg" 
     alt="" 
     role="presentation" />
```

**Headings:**
- **Name:** Heading text
- **Role:** `heading` with appropriate level
- **Value:** Heading level (`aria-level`)

```html
<h2 id="section-heading">Featured Destinations</h2>
<!-- or -->
<div role="heading" aria-level="2">Featured Destinations</div>
```

## Tab/Shift+Tab Test Plan

### Test Scenarios

#### 1. Homepage Navigation Flow
**Test Steps:**
1. Load homepage
2. Press Tab repeatedly
3. Verify focus order and visual indicators
4. Press Shift+Tab to reverse

**Expected Tab Order:**
1. Skip link (if keyboard user)
2. Logo (if present)
3. Explore link
4. User menu button
5. Search input
6. Search button
7. Filter chip: Weekend
8. Filter chip: Under ₹15k
9. Filter chip: Visa-free
10. Filter chip: Honeymoon
11. Filter chip: Mountains
12. First editorial tile
13. Second editorial tile
14. Continue through all tiles
15. Footer links

**Pass Criteria:**
- ✅ All interactive elements receive focus
- ✅ Focus indicators are visible (2px cool ring)
- ✅ Focus order is logical and predictable
- ✅ No focus traps (except intentional modals)
- ✅ Shift+Tab reverses order exactly

#### 2. Editorial Tile Interaction
**Test Steps:**
1. Tab to editorial tile
2. Press Enter to activate
3. Tab through revealed content
4. Press Escape to close
5. Verify focus restoration

**Expected Behavior:**
1. Tile receives focus with visible ring
2. Enter reveals hover content
3. Focus moves to first transport tab
4. Tab navigates: Flight tab → Train tab → View details → WhatsApp
5. Escape hides content, focus returns to tile

**Pass Criteria:**
- ✅ Hover content is keyboard accessible
- ✅ Tab order within tile is logical
- ✅ Focus restoration works correctly
- ✅ Screen reader announces state changes

#### 3. Explore Page Filter Navigation
**Test Steps:**
1. Navigate to explore page
2. Tab through filter sidebar
3. Test radio button arrow navigation
4. Test checkbox interactions
5. Apply filters and verify results

**Expected Tab Order:**
1. Destination search input
2. All trips radio button
3. Domestic radio button  
4. International radio button
5. Weekend checkbox
6. Under ₹15k checkbox
7. (Continue through all filter options)
8. Clear all filters button
9. Sort dropdown
10. First result tile

**Pass Criteria:**
- ✅ Arrow keys navigate radio groups
- ✅ Space toggles checkboxes
- ✅ Filter changes announce result updates
- ✅ Clear button resets all filters

#### 4. Mobile Navigation Test
**Test Steps:**
1. Resize to mobile viewport
2. Test touch targets
3. Verify focus indicators on mobile
4. Test filter sheet interaction

**Expected Behavior:**
- Touch targets ≥44px × 44px
- Focus rings visible on external keyboards
- Filter sheet opens/closes properly
- Horizontal chip scrolling works

**Pass Criteria:**
- ✅ All touch targets meet size requirements
- ✅ Focus management works on mobile
- ✅ Sheet modal traps focus appropriately
- ✅ Horizontal scrolling is keyboard accessible

### Automated Testing Integration

```javascript
// Example test with Testing Library
describe('Keyboard Navigation', () => {
  test('homepage tab order', async () => {
    render(<Homepage />);
    
    const user = userEvent.setup();
    
    // Test tab order
    await user.tab();
    expect(screen.getByRole('link', { name: /explore/i })).toHaveFocus();
    
    await user.tab();
    expect(screen.getByRole('button', { name: /user menu/i })).toHaveFocus();
    
    await user.tab();
    expect(screen.getByRole('searchbox')).toHaveFocus();
    
    // Continue testing full tab order...
  });
  
  test('tile keyboard interaction', async () => {
    render(<EditorialTile {...mockTileProps} />);
    
    const user = userEvent.setup();
    const tile = screen.getByRole('gridcell');
    
    // Focus tile and activate
    tile.focus();
    await user.keyboard('{Enter}');
    
    // Verify hover content is revealed and focusable
    expect(screen.getByRole('tab', { name: /flight/i })).toBeVisible();
    expect(screen.getByRole('tab', { name: /flight/i })).toHaveFocus();
  });
});
```

## Focus Management Specifications

### Focus Ring Standards
- **Color:** Cool (#0647AE)
- **Width:** 2px
- **Style:** Solid ring with 2px offset
- **Implementation:** `focus:ring-2 focus:ring-cool focus:ring-offset-2`

### Focus Trap Requirements
- **User Menu:** When expanded, trap focus within menu
- **Filter Sheet (Mobile):** Trap focus within sheet modal
- **Search Suggestions:** Trap focus within suggestion dropdown

### Focus Restoration Rules
- **Modal Close:** Return focus to trigger element
- **Tile Hover Close:** Return focus to tile
- **Filter Clear:** Return focus to first filter control
- **Page Navigation:** Focus main heading or skip link target

### Screen Reader Announcements

**State Changes:**
```html
<!-- Filter activation -->
<div aria-live="polite" aria-atomic="true">
  Weekend filter activated. Showing 24 trips.
</div>

<!-- Loading states -->
<div aria-live="assertive">
  Loading search results...
</div>

<!-- Error states -->
<div role="alert">
  Search failed. Please try again.
</div>
```

**Dynamic Content:**
- Use `aria-live="polite"` for non-urgent updates
- Use `aria-live="assertive"` for important changes
- Use `role="alert"` for errors and warnings
- Use `aria-atomic="true"` when entire region should be re-read

This comprehensive ARIA map ensures the premium UI redesign maintains excellent accessibility while delivering the sophisticated visual experience. All interactive elements follow consistent patterns for keyboard navigation, screen reader support, and focus management.