# Accessibility & Usability Testing Protocol

## Overview

This document provides comprehensive testing protocols for accessibility and usability validation of the premium UI redesign. It includes screen reader testing procedures, keyboard navigation scenarios, focus management verification, and reduced motion testing with specific pass/fail criteria and remediation priority levels.

## Testing Environment Setup

### Required Tools & Software

**Screen Readers:**
- **NVDA** (Windows) - Version 2023.1 or later
- **JAWS** (Windows) - Version 2023 or later  
- **VoiceOver** (macOS) - Built-in, latest version
- **Orca** (Linux) - Version 42 or later
- **TalkBack** (Android) - For mobile testing
- **VoiceOver** (iOS) - For mobile testing

**Browsers:**
- Chrome 115+ (primary testing)
- Firefox 115+ (secondary)
- Safari 16+ (macOS/iOS)
- Edge 115+ (Windows)

**Testing Devices:**
- Desktop: 1920×1080, 1366×768 resolutions
- Tablet: iPad (1024×768), Android tablet (1280×800)
- Mobile: iPhone 14 (390×844), Android (360×640)

**Additional Tools:**
- **axe DevTools** browser extension
- **WAVE** browser extension
- **Colour Contrast Analyser** desktop app
- **Keyboard navigation tester** (custom script)
- **Focus ring visibility checker** (custom CSS)

### Test Data Setup

```javascript
// Test user personas for personalization testing
const testPersonas = {
  screenReader: {
    name: "Alex",
    preferences: { reducedMotion: true, highContrast: false },
    assistiveTech: "NVDA"
  },
  keyboardOnly: {
    name: "Jordan",
    preferences: { reducedMotion: false, highContrast: false },
    assistiveTech: "keyboard"
  },
  lowVision: {
    name: "Sam",
    preferences: { reducedMotion: true, highContrast: true },
    assistiveTech: "screen magnifier"
  }
};
```

## Screen Reader Testing Scripts

### 1. NVDA Testing Protocol

**Pre-test Setup:**
1. Install NVDA 2023.1+
2. Configure speech rate to 50% for testing
3. Enable developer mode in NVDA settings
4. Clear browser cache and cookies

**Test Script - Homepage Navigation:**

```
Test ID: NVDA-HOME-001
Objective: Verify homepage content structure and navigation with NVDA

Steps:
1. Open Chrome and navigate to http://localhost:3000/
2. Start NVDA (Ctrl + Alt + N)
3. Press H to navigate by headings
4. Document heading structure and content

Expected Results:
- H1: "Plan less. Travel more." (announced clearly)
- H2: Section headings for editorial content
- Logical heading hierarchy (no skipped levels)
- Personalized greeting "Hi Alex," announced before H1

Pass Criteria:
✅ All headings announced with correct level
✅ Heading text matches visual content
✅ No empty or duplicate headings
✅ Logical reading order maintained

Fail Criteria:
❌ Missing or incorrect heading levels
❌ Headings not announced or garbled
❌ Illogical heading sequence
❌ Personalization not announced

Priority: P0 (Critical)
```

**Test Script - Search Band Interaction:**

```
Test ID: NVDA-SEARCH-001
Objective: Verify search functionality with NVDA

Steps:
1. Navigate to search section (press R for regions)
2. Tab to search input field
3. Type "Kashmir" in search field
4. Tab through filter chips
5. Activate Weekend chip (Space key)
6. Submit search (Enter key)

Expected Results:
- Search region announced: "Search travel packages"
- Input field: "Search destinations, edit text"
- Filter chips announced as "Weekend trips filter, switch, not pressed"
- Chip activation: "Weekend trips filter, switch, pressed"
- Results update announced: "Showing 12 trips"

Pass Criteria:
✅ Search region properly identified
✅ Input field has accessible name
✅ Filter chips have clear labels and states
✅ State changes announced immediately
✅ Results update communicated

Fail Criteria:
❌ Search region not identified
❌ Input field unlabeled or unclear
❌ Filter chips missing labels or states
❌ State changes not announced
❌ Results update not communicated

Priority: P0 (Critical)
```

**Test Script - Editorial Tiles Navigation:**

```
Test ID: NVDA-TILES-001
Objective: Verify editorial tile content and interactions

Steps:
1. Navigate to main content region
2. Use arrow keys to navigate through tiles
3. Press Enter on first tile to reveal hover content
4. Tab through transport options and action buttons
5. Press Escape to close hover content

Expected Results:
- Tiles announced as "Travel packages grid"
- Each tile: "Kashmir Valley, article, Srinagar Kashmir, 5 days, 2-6 people, ₹25,999 per person"
- Hover content: Transport tabs and action buttons properly labeled
- Focus management: Focus moves to first interactive element in hover content
- Escape: Focus returns to tile, hover content hidden

Pass Criteria:
✅ Grid structure communicated
✅ Tile content fully announced
✅ Interactive elements properly labeled
✅ Focus management works correctly
✅ Escape key functionality works

Fail Criteria:
❌ Grid structure unclear or missing
❌ Tile content incomplete or unclear
❌ Interactive elements unlabeled
❌ Focus management broken
❌ Escape key doesn't work

Priority: P0 (Critical)
```

### 2. JAWS Testing Protocol

**Test Script - Explore Page Filters:**

```
Test ID: JAWS-EXPLORE-001
Objective: Verify explore page filter functionality with JAWS

Steps:
1. Navigate to /explore page
2. Use JAWS virtual cursor (arrow keys) to explore filter sidebar
3. Use Tab key to navigate interactive elements
4. Test radio button group navigation (arrow keys)
5. Test checkbox interactions (Space key)
6. Apply multiple filters and verify results

Expected Results:
- Sidebar announced as "Filter Options, complementary"
- Radio groups: "Trip Type, radio group, All Trips, 1 of 3"
- Checkboxes: "Weekend trips, checkbox, not checked"
- Filter application: "Showing 8 trips" announced
- Clear filters: "Clear all filters, button"

Pass Criteria:
✅ Sidebar role and purpose clear
✅ Radio groups properly structured
✅ Checkboxes have clear labels and states
✅ Filter results communicated
✅ Clear functionality works

Fail Criteria:
❌ Sidebar role unclear or missing
❌ Radio groups not properly grouped
❌ Checkboxes missing labels or states
❌ Filter results not communicated
❌ Clear functionality broken

Priority: P0 (Critical)
```

### 3. VoiceOver Testing Protocol (macOS)

**Test Script - Mobile Navigation:**

```
Test ID: VO-MOBILE-001
Objective: Verify mobile experience with VoiceOver on Safari

Steps:
1. Open Safari on iPhone/iPad
2. Navigate to homepage
3. Enable VoiceOver (triple-click home button)
4. Use swipe gestures to navigate
5. Test filter sheet interaction
6. Verify touch target sizes

Expected Results:
- Swipe navigation follows logical order
- Touch targets ≥44px announced as "large enough"
- Filter sheet: "Sheet, showing filters" when opened
- Gesture navigation works smoothly
- No focus traps or dead ends

Pass Criteria:
✅ Logical swipe navigation order
✅ Touch targets meet size requirements
✅ Sheet modal properly announced
✅ Gesture navigation responsive
✅ No navigation dead ends

Fail Criteria:
❌ Illogical or broken swipe order
❌ Touch targets too small
❌ Sheet modal not announced
❌ Gesture navigation unresponsive
❌ Navigation dead ends exist

Priority: P1 (High)
```

## Keyboard Navigation Testing Scenarios

### 1. Full Keyboard Navigation Flow

**Test Scenario: Complete Homepage Journey**

```
Test ID: KBD-FLOW-001
Objective: Complete keyboard-only navigation through homepage

Pre-conditions:
- Mouse disconnected or disabled
- Browser zoom at 100%
- No browser extensions affecting focus

Test Steps:
1. Load homepage (http://localhost:3000/)
2. Press Tab repeatedly to navigate through all interactive elements
3. Use Enter/Space to activate elements as appropriate
4. Use Escape to close any opened content
5. Use Shift+Tab to navigate backwards
6. Document focus order and any issues

Expected Tab Order:
1. Skip link (if present)
2. Logo (if on non-homepage)
3. Explore link
4. User menu button
5. Search input field
6. Search submit button
7. Weekend filter chip
8. Under ₹15k filter chip
9. Visa-free filter chip
10. Honeymoon filter chip
11. Mountains filter chip
12. First editorial tile
13. Second editorial tile
14. [Continue through all tiles]
15. Footer links

Pass Criteria:
✅ All interactive elements receive focus
✅ Focus order is logical and predictable
✅ Focus indicators clearly visible (2px cool ring)
✅ No focus traps (except intentional modals)
✅ Shift+Tab reverses order exactly
✅ Enter/Space activate elements appropriately
✅ Escape closes opened content

Fail Criteria:
❌ Interactive elements not focusable
❌ Illogical or unpredictable focus order
❌ Focus indicators invisible or unclear
❌ Unintentional focus traps
❌ Shift+Tab doesn't reverse order
❌ Enter/Space don't work as expected
❌ Escape doesn't close content

Priority: P0 (Critical)
Remediation: Fix immediately before release
```

### 2. Complex Component Interactions

**Test Scenario: Editorial Tile Keyboard Interaction**

```
Test ID: KBD-TILE-001
Objective: Verify keyboard interaction with editorial tiles

Test Steps:
1. Tab to first editorial tile
2. Press Enter to activate tile (show hover content)
3. Verify focus moves to first interactive element
4. Tab through transport tabs (Flight, Train, Bus)
5. Tab to action buttons (View details, WhatsApp)
6. Press Escape to close hover content
7. Verify focus returns to tile
8. Repeat with arrow key navigation between tiles

Expected Behavior:
- Tile activation: Enter key shows hover content
- Focus management: Focus moves to Flight tab
- Tab navigation: Flight → Train → Bus → View details → WhatsApp
- Arrow keys: Navigate between tiles in grid
- Escape: Close hover content, return focus to tile

Pass Criteria:
✅ Enter key activates tile correctly
✅ Focus moves to first interactive element
✅ Tab order within tile is logical
✅ Arrow keys navigate between tiles
✅ Escape closes content and restores focus
✅ All interactions work consistently

Fail Criteria:
❌ Enter key doesn't activate tile
❌ Focus doesn't move or moves incorrectly
❌ Tab order within tile is broken
❌ Arrow keys don't work
❌ Escape doesn't work or breaks focus
❌ Inconsistent behavior across tiles

Priority: P0 (Critical)
Remediation: Fix before release
```

### 3. Filter and Search Interactions

**Test Scenario: Explore Page Filter Navigation**

```
Test ID: KBD-FILTER-001
Objective: Verify keyboard navigation through explore page filters

Test Steps:
1. Navigate to /explore page
2. Tab through filter sidebar elements
3. Test radio button group navigation (arrow keys)
4. Test checkbox interactions (Space key)
5. Apply filters and verify results update
6. Use keyboard to clear filters

Expected Navigation:
1. Destination search input
2. Trip type radio group (use arrows within group)
3. Theme checkboxes (Space to toggle)
4. Date selectors
5. Pax selectors
6. Clear all filters button
7. Sort dropdown
8. Results grid

Pass Criteria:
✅ Tab order follows logical flow
✅ Arrow keys navigate radio button groups
✅ Space key toggles checkboxes
✅ Filter changes update results
✅ Clear button resets all filters
✅ Sort dropdown works with keyboard
✅ Results grid receives focus after filtering

Fail Criteria:
❌ Tab order is illogical
❌ Arrow keys don't work in radio groups
❌ Space key doesn't toggle checkboxes
❌ Filter changes don't update results
❌ Clear button doesn't work
❌ Sort dropdown not keyboard accessible
❌ Results grid doesn't receive focus

Priority: P0 (Critical)
Remediation: Fix before release
```

## Focus Ring Visibility Testing

### 1. Focus Indicator Standards

**Test Specification: Focus Ring Visibility**

```
Test ID: FOCUS-VIS-001
Objective: Verify focus indicators meet visibility standards

Requirements:
- Color: Cool (#0647AE)
- Width: 2px minimum
- Style: Solid ring with 2px offset
- Contrast: ≥3:1 against all backgrounds
- Visibility: Clear on all interactive elements

Test Procedure:
1. Navigate through all interactive elements using Tab
2. Take screenshots of each focused element
3. Measure focus ring contrast using Colour Contrast Analyser
4. Verify focus ring appears on all element types:
   - Links
   - Buttons
   - Form inputs
   - Filter chips
   - Tiles
   - Dropdown menus

Pass Criteria:
✅ Focus ring visible on all interactive elements
✅ Contrast ratio ≥3:1 against all backgrounds
✅ Ring width ≥2px
✅ Consistent styling across all elements
✅ Ring doesn't interfere with content readability

Fail Criteria:
❌ Focus ring missing on any interactive element
❌ Contrast ratio <3:1 on any background
❌ Ring width <2px
❌ Inconsistent styling
❌ Ring interferes with content

Priority: P0 (Critical)
Remediation: Fix immediately
```

### 2. High Contrast Mode Testing

**Test Scenario: Windows High Contrast Mode**

```
Test ID: FOCUS-HC-001
Objective: Verify focus indicators work in high contrast mode

Test Steps:
1. Enable Windows High Contrast mode
2. Navigate through all interactive elements
3. Verify focus indicators remain visible
4. Test with different high contrast themes

Expected Results:
- Focus indicators adapt to high contrast colors
- All interactive elements remain focusable
- Content remains readable and accessible
- Brand colors may change but functionality preserved

Pass Criteria:
✅ Focus indicators visible in all high contrast themes
✅ All interactive elements remain accessible
✅ Content readability maintained
✅ No functionality lost

Fail Criteria:
❌ Focus indicators invisible in high contrast
❌ Interactive elements become inaccessible
❌ Content becomes unreadable
❌ Functionality breaks

Priority: P1 (High)
Remediation: Fix before release
```

## Reduced Motion Testing

### 1. Motion Preference Verification

**Test Scenario: Prefers-Reduced-Motion Support**

```
Test ID: MOTION-001
Objective: Verify reduced motion preferences are respected

Test Setup:
1. Enable reduced motion in OS settings:
   - macOS: System Preferences → Accessibility → Display → Reduce motion
   - Windows: Settings → Ease of Access → Display → Show animations
   - Linux: gsettings set org.gnome.desktop.interface enable-animations false

Test Steps:
1. Load homepage with reduced motion enabled
2. Observe hero section behavior
3. Interact with tiles and check hover animations
4. Navigate through site and observe transitions
5. Verify essential functionality remains intact

Expected Behavior:
- Ken Burns effect disabled (hero image static)
- Tile hover animations simplified or removed
- Page transitions reduced or eliminated
- Loading spinners may be simplified
- Focus indicators still animate (essential feedback)

Pass Criteria:
✅ Hero Ken Burns animation disabled
✅ Complex tile animations simplified
✅ Page transitions reduced
✅ Essential functionality preserved
✅ Focus indicators still provide feedback
✅ No motion sickness triggers

Fail Criteria:
❌ Animations continue despite preference
❌ Essential functionality broken
❌ Focus indicators removed
❌ Motion sickness triggers remain

Priority: P1 (High)
Remediation: Fix before release
```

### 2. Vestibular Disorder Considerations

**Test Scenario: Motion Sensitivity Testing**

```
Test ID: MOTION-VEST-001
Objective: Verify site is safe for users with vestibular disorders

Test Criteria:
- No parallax scrolling effects
- No auto-playing videos with motion
- No rapid flashing or strobing
- No unexpected motion triggers
- User control over all animations

Test Steps:
1. Review all animations for vestibular triggers
2. Check for parallax effects
3. Verify auto-play video settings
4. Test animation controls
5. Review motion duration and intensity

Pass Criteria:
✅ No parallax scrolling effects
✅ No auto-playing videos with motion
✅ No flashing faster than 3Hz
✅ All motion user-controlled or essential only
✅ Animation duration <5 seconds
✅ Smooth, predictable motion paths

Fail Criteria:
❌ Parallax effects present
❌ Auto-playing motion videos
❌ Flashing faster than 3Hz
❌ Uncontrolled motion
❌ Animation duration >5 seconds
❌ Erratic or unpredictable motion

Priority: P0 (Critical)
Remediation: Fix immediately
```

## Touch Target Testing

### 1. Mobile Touch Target Verification

**Test Scenario: Touch Target Size Compliance**

```
Test ID: TOUCH-SIZE-001
Objective: Verify all touch targets meet minimum size requirements

Requirements:
- Minimum size: 44px × 44px (iOS/Android guidelines)
- Preferred size: 48px × 48px (Material Design)
- Spacing: 8px minimum between targets
- Exception: Inline text links (but must be easily tappable)

Test Procedure:
1. Use browser developer tools to measure elements
2. Test on actual mobile devices
3. Verify spacing between adjacent targets
4. Test with different finger sizes (accessibility consideration)

Elements to Test:
- Header navigation buttons
- Search button
- Filter chips
- Tile action buttons
- Form controls
- Footer links

Pass Criteria:
✅ All interactive elements ≥44px × 44px
✅ Adequate spacing between targets
✅ Easy to tap without accidental activation
✅ Consistent sizing across similar elements

Fail Criteria:
❌ Interactive elements <44px × 44px
❌ Insufficient spacing causing mis-taps
❌ Difficult to tap accurately
❌ Inconsistent sizing

Priority: P0 (Critical)
Remediation: Fix before release
```

## Automated Testing Integration

### 1. Continuous Accessibility Testing

**Jest + Testing Library Integration:**

```javascript
// __tests__/accessibility.test.js
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import Homepage from '../pages/index';

expect.extend(toHaveNoViolations);

describe('Accessibility Tests', () => {
  test('homepage has no accessibility violations', async () => {
    const { container } = render(<Homepage />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test('keyboard navigation works correctly', async () => {
    render(<Homepage />);
    const user = userEvent.setup();
    
    // Test tab order
    await user.tab();
    expect(screen.getByRole('link', { name: /explore/i })).toHaveFocus();
    
    await user.tab();
    expect(screen.getByRole('button', { name: /user menu/i })).toHaveFocus();
    
    await user.tab();
    expect(screen.getByRole('searchbox')).toHaveFocus();
  });

  test('focus indicators are visible', async () => {
    render(<Homepage />);
    const user = userEvent.setup();
    
    const exploreLink = screen.getByRole('link', { name: /explore/i });
    await user.tab();
    
    expect(exploreLink).toHaveClass('focus:ring-2', 'focus:ring-cool');
  });
});
```

### 2. Visual Regression for Accessibility

**Percy + Accessibility Testing:**

```javascript
// tests/accessibility-visual.test.js
const percySnapshot = require('@percy/puppeteer');
const puppeteer = require('puppeteer');

describe('Accessibility Visual Tests', () => {
  let browser, page;
  
  beforeAll(async () => {
    browser = await puppeteer.launch();
    page = await browser.newPage();
  });
  
  test('focus indicators visible', async () => {
    await page.goto('http://localhost:3000');
    
    // Focus first interactive element
    await page.keyboard.press('Tab');
    
    await percySnapshot(page, 'Focus Indicators - Header', {
      percyCSS: `
        /* Ensure focus rings are captured */
        *:focus {
          outline: 2px solid #0647AE !important;
          outline-offset: 2px !important;
        }
      `
    });
  });
  
  test('high contrast mode compatibility', async () => {
    await page.emulateMediaFeatures([
      { name: 'prefers-contrast', value: 'high' }
    ]);
    
    await page.goto('http://localhost:3000');
    
    await percySnapshot(page, 'High Contrast Mode', {
      widths: [1280],
    });
  });
});
```

## Pass/Fail Criteria & Remediation Priorities

### Priority Levels

**P0 - Critical (Fix Immediately)**
- Blocks release
- Prevents basic functionality
- WCAG 2.1 AA violations
- Legal compliance issues

**P1 - High (Fix Before Release)**
- Significantly impacts user experience
- Accessibility best practices
- Usability concerns

**P2 - Medium (Fix in Next Sprint)**
- Minor usability improvements
- Enhancement opportunities
- Nice-to-have accessibility features

**P3 - Low (Backlog)**
- Future improvements
- Advanced accessibility features
- Optimization opportunities

### Remediation Guidelines

**Immediate Actions (P0):**
1. Stop deployment if automated tests fail
2. Create hotfix branch for critical issues
3. Notify accessibility team and stakeholders
4. Implement fix and re-test immediately
5. Document issue and resolution

**Pre-Release Actions (P1):**
1. Create issue in project management system
2. Assign to appropriate developer
3. Set deadline before release
4. Test fix thoroughly
5. Update documentation

**Sprint Planning (P2/P3):**
1. Add to product backlog
2. Estimate effort required
3. Prioritize in next sprint planning
4. Consider user impact and business value

This comprehensive testing protocol ensures the premium UI redesign meets the highest accessibility and usability standards while providing clear guidance for issue resolution and continuous improvement.