# Cinematic Background Image System - Art Direction Brief

## Overview

This document provides comprehensive art direction for TripChoice's premium cinematic hero background system. The goal is to create a cohesive library of high-impact travel imagery that supports the brand's sophisticated positioning while ensuring optimal text contrast and visual storytelling.

## Visual Identity & Mood

**Brand Positioning:** Premium, sophisticated travel experiences that inspire wanderlust
**Visual Mood:** Cinematic, aspirational, warm, inviting, editorial-quality
**Emotional Tone:** Wonder, serenity, adventure, luxury, authenticity

## Technical Specifications

### Image Requirements
- **Resolution:** Minimum 1920px wide (2560px preferred for high-DPI displays)
- **Aspect Ratio:** 16:9 (1920×1080, 2560×1440)
- **Format:** WebP primary, JPEG fallback
- **Quality:** 85% compression for optimal balance
- **File Size:** Target <500KB per image after optimization

### Processing Pipeline
1. **Color Grading:** HDR look with enhanced dynamic range
2. **Tone Mapping:** Warm golden highlights, rich shadows
3. **Grain Addition:** Subtle film grain at 2.5% opacity
4. **Optimization:** WebP conversion with progressive loading
5. **Responsive Variants:** Generate 1920px, 1440px, 1024px, 768px versions

## Composition Guidelines

### Rule of Thirds
- **Horizon Placement:** Lower third (ground-heavy) or upper third (sky-heavy)
- **Subject Placement:** Key elements at intersection points
- **Negative Space:** Reserve upper-left and center areas for text overlay

### Leading Lines
- **Natural Lines:** Rivers, shorelines, mountain ridges, pathways
- **Direction:** Guide eye toward horizon or key focal points
- **Depth:** Create layers (foreground, midground, background)

### Human Elements
- **Silhouettes Only:** Traveler figures gazing outward, never at camera
- **Scale:** Small figures to emphasize landscape grandeur
- **Positioning:** Lower third or edge placement
- **Emotion:** Contemplative, aspirational poses

## Image Theme Library

### 1. Mountain Lakes (Golden Hour)
**Mood:** Serene, majestic, contemplative
**Composition:**
- Crystal-clear alpine lake in foreground
- Dramatic mountain peaks in background
- Traveler silhouette on shoreline or dock
- Soft reflections doubling the visual impact
- Golden hour lighting (30 minutes before sunset)

**Color Palette:**
- Warm golds and oranges in sky
- Deep blues and teals in water
- Rich purples and magentas in mountains
- Subtle pink highlights on snow caps

**Example Prompt:**
"Cinematic wide shot of pristine alpine lake at golden hour, dramatic mountain peaks reflected in still water, lone traveler silhouette standing on wooden dock gazing toward horizon, warm golden light, HDR processing, film grain texture, 16:9 aspect ratio"

### 2. Tropical Beaches (Sunset)
**Mood:** Romantic, peaceful, luxurious
**Composition:**
- Pristine beach with gentle waves
- Palm trees or tropical vegetation framing
- Couple or individual silhouette walking shoreline
- Dramatic sunset sky with cloud formations
- Soft foam patterns in foreground

**Color Palette:**
- Vibrant oranges and reds in sky
- Warm yellows and golds on water
- Deep blues in ocean depths
- Soft whites in foam and sand

**Example Prompt:**
"Cinematic beach sunset with couple silhouettes walking along pristine shoreline, dramatic orange and pink sky, gentle waves with soft foam, palm trees framing composition, warm golden light reflecting on wet sand, HDR look, subtle film grain, 16:9"

### 3. Misty Valleys (Dawn)
**Mood:** Mysterious, ethereal, adventurous
**Composition:**
- Rolling hills or valleys with morning mist
- Layered mountain ridges creating depth
- Traveler on elevated viewpoint
- Soft, diffused lighting through fog
- Winding paths or rivers below

**Color Palette:**
- Soft blues and purples in mist
- Warm golds breaking through fog
- Rich greens in vegetation
- Cool grays in distant mountains

**Example Prompt:**
"Cinematic dawn landscape of misty valley with layered mountain ridges, lone hiker silhouette on cliff edge overlooking fog-filled valley, soft golden light breaking through mist, atmospheric depth, HDR processing, film grain, 16:9"

### 4. City Skylines (Dusk)
**Mood:** Sophisticated, urban, dynamic
**Composition:**
- Modern city skyline during blue hour
- Warm lights beginning to illuminate buildings
- Traveler on rooftop or elevated position
- River or water feature reflecting lights
- Balance of natural and artificial lighting

**Color Palette:**
- Deep blues in twilight sky
- Warm yellows and oranges in windows
- Cool blues in glass buildings
- Golden reflections on water

**Example Prompt:**
"Cinematic city skyline at dusk, modern skyscrapers with warm window lights, traveler silhouette on rooftop terrace overlooking urban landscape, blue hour lighting, river reflections, HDR processing, film grain texture, 16:9"

### 5. Desert Landscapes (Magic Hour)
**Mood:** Dramatic, vast, transformative
**Composition:**
- Expansive desert with dramatic rock formations
- Sand dunes with wind-carved patterns
- Traveler figure for scale emphasis
- Dramatic sky with interesting cloud formations
- Strong directional lighting creating shadows

**Color Palette:**
- Warm oranges and reds in rock
- Golden yellows in sand
- Deep purples and magentas in shadows
- Brilliant blues in clear sky

**Example Prompt:**
"Cinematic desert landscape at magic hour, dramatic red rock formations and sand dunes, lone traveler silhouette against vast landscape, warm golden light creating long shadows, clear blue sky with wispy clouds, HDR look, film grain, 16:9"

### 6. Forest Paths (Filtered Light)
**Mood:** Peaceful, natural, grounding
**Composition:**
- Winding forest path with dappled sunlight
- Tall trees creating natural cathedral
- Traveler walking deeper into forest
- Rays of light filtering through canopy
- Rich textures in bark and foliage

**Color Palette:**
- Rich greens in foliage
- Warm golds in sunbeams
- Deep browns in tree trunks
- Soft yellows in filtered light

## Overlay System

### Gradient Application
**Primary Overlay:** `linear-gradient(to bottom, rgba(6,71,174,0.15), rgba(7,28,60,0.3) 50%, rgba(7,28,60,0.75))`
- Cool blue at top (15% opacity)
- Ink blue in middle (30% opacity)  
- Deep ink at bottom (75% opacity)

**Secondary Overlay:** `linear-gradient(to top, rgba(7,28,60,0.4), transparent 40%)`
- Additional bottom gradient for text contrast
- Ensures readability of lower text elements

### Grain Texture
- **File:** `/grain.svg` or `/grain.png`
- **Opacity:** 2.5%
- **Blend Mode:** `mix-blend-mode: overlay`
- **Purpose:** Adds premium film-like quality

### Text Contrast Assurance
- **Minimum Ratio:** 4.5:1 for all text elements
- **Testing Areas:** Upper-left (greeting), center (H1), lower-center (subtitle)
- **Fallback:** Increase overlay opacity if contrast insufficient
- **Dynamic Adjustment:** Consider image brightness analysis for auto-adjustment

## Content Guidelines

### Prohibited Elements
- ❌ Text or logos within images
- ❌ Busy backgrounds in text overlay areas
- ❌ People facing camera or posing
- ❌ Branded clothing or equipment
- ❌ Modern vehicles or technology
- ❌ Cluttered compositions

### Required Elements
- ✅ Clear negative space for text overlay
- ✅ Natural leading lines
- ✅ Consistent lighting quality
- ✅ Traveler silhouettes (when included)
- ✅ Authentic, unposed moments
- ✅ High dynamic range suitable for HDR processing

## Quality Control Checklist

### Pre-Processing
- [ ] Image resolution ≥1920px wide
- [ ] 16:9 aspect ratio confirmed
- [ ] No text or logos present
- [ ] Sufficient negative space for overlay text
- [ ] Authentic travel context

### Post-Processing
- [ ] HDR look applied consistently
- [ ] Warm golden tones enhanced
- [ ] Film grain added at 2.5% opacity
- [ ] WebP format with JPEG fallback
- [ ] File size optimized <500KB
- [ ] Responsive variants generated

### Contrast Testing
- [ ] Text contrast ≥4.5:1 with overlay applied
- [ ] Greeting text readable (upper-left)
- [ ] H1 text readable (center)
- [ ] Subtitle text readable (lower-center)
- [ ] Fallback overlay tested if needed

## Implementation Notes

### CSS Integration
```css
.cinematic-hero {
  background-image: 
    linear-gradient(to bottom, rgba(6,71,174,0.15), rgba(7,28,60,0.3) 50%, rgba(7,28,60,0.75)),
    linear-gradient(to top, rgba(7,28,60,0.4), transparent 40%),
    url('/grain.svg'),
    url('[hero-image.webp]');
  background-blend-mode: normal, normal, overlay, normal;
  background-size: cover, cover, 100px 100px, cover;
  background-position: center, center, 0 0, center;
}
```

### Animation Integration
```css
@keyframes kenBurns {
  0% { transform: scale(1.00); }
  100% { transform: scale(1.03); }
}

.hero-image {
  animation: kenBurns 7s ease-out infinite alternate;
}
```

### Responsive Considerations
- Use `srcset` for different viewport sizes
- Prioritize mobile-optimized versions <300KB
- Consider art direction changes for mobile (closer crops)
- Test overlay effectiveness across all breakpoints

## Brand Consistency

### Style Continuity
- Maintain consistent color grading across all images
- Ensure similar contrast and saturation levels
- Apply uniform grain texture and HDR processing
- Keep lighting quality and mood consistent

### Seasonal Considerations
- Rotate images based on travel seasons
- Consider regional relevance for target markets
- Update library quarterly with fresh content
- A/B test image performance and engagement

This art direction brief ensures TripChoice's hero imagery maintains premium quality while supporting optimal user experience and brand positioning.