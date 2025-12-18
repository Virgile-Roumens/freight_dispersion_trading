# Engelhart Freight Analytics - Brand Design System

## Overview
Professional UI/UX redesign for Engelhart Commodities Trading's Capesize freight analytics platform. The design reflects Engelhart's values: **Bold. Collaborative. Proactive. Professional.**

---

## 🎨 Color Palette

### Primary Colors (from Engelhart Logo)

**Navy Blue** - Primary Brand Color
- Hex: `#132c68`
- RGB: `rgb(19, 44, 104)`
- Usage: Headers, primary elements, navigation, charts
- Psychology: Trust, professionalism, depth, stability

**Gold/Yellow** - Accent & Highlight
- Hex: `#f4c430`
- RGB: `rgb(244, 196, 48)`
- Usage: Highlights, calls-to-action, success states, accents
- Psychology: Excellence, value, energy, optimism

**Teal/Light Blue** - Data Visualization
- Hex: `#5eb8e8`
- RGB: `rgb(94, 184, 232)`
- Usage: Charts, data points, secondary information
- Psychology: Innovation, clarity, analytics, flow

**Light Blue** - Supporting Color
- Hex: `#4a90e2`
- RGB: `rgb(74, 144, 226)`
- Usage: Interactive elements, hover states

### Supporting Colors

**Light Gray Background**
- Hex: `#f8f9fa`
- Usage: Page backgrounds, cards

**White**
- Hex: `#ffffff`
- Usage: Content backgrounds, cards

**Success Green**
- Hex: `#28a745`
- Usage: Positive metrics, confirmations

**Warning Amber**
- Hex: `#ffc107`
- Usage: Warnings, cautions (aligned with gold)

**Danger Red**
- Hex: `#dc3545`
- Usage: Negative metrics, errors

---

## 🖼️ Visual Design Elements

### Gradients

**Primary Header Gradient**
```css
background: linear-gradient(135deg, #132c68 0%, #1a3a7f 100%);
```
Usage: Main headers, hero sections, navigation sidebar

**Info Box Gradient**
```css
background: linear-gradient(135deg, #f0f7ff 0%, #e6f2ff 100%);
```
Usage: Information cards, help text

**Card Background**
```css
background: white;
box-shadow: 0 2px 8px rgba(19, 44, 104, 0.1);
border-top: 4px solid #132c68;
```

### Borders & Shadows

**Primary Border**
- Color: `#132c68`
- Width: `2px` (standard), `3-5px` (emphasis)

**Accent Border**
- Color: `#f4c430`
- Width: `2-3px`
- Usage: Active states, highlights

**Card Shadow**
```css
box-shadow: 0 2px 8px rgba(19, 44, 104, 0.1);
```

**Hover Shadow (Enhanced)**
```css
box-shadow: 0 6px 12px rgba(19, 44, 104, 0.2);
```

---

## 📐 Typography

### Headings

**H1 - Main Page Title**
- Size: `2.8rem`
- Weight: `700 (Bold)`
- Color: `#132c68` or `white` (on dark backgrounds)
- Letter-spacing: `-0.5px`

**H2 - Section Headers**
- Size: `2rem`
- Weight: `600 (Semi-bold)`
- Color: `#132c68`
- Border-bottom: `3px solid #f4c430`

**H3 - Subsections**
- Size: `1.5rem`
- Weight: `600 (Semi-bold)`
- Color: `#132c68`

### Body Text

**Primary Text**
- Size: `1rem`
- Color: `#495057` (dark gray)

**Secondary Text**
- Size: `0.9-0.95rem`
- Color: `#6c757d` (medium gray)

**Accent Text**
- Color: `#f4c430` (gold)
- Usage: Highlights, key metrics, labels

---

## 🎯 Component Styles

### Sidebar Navigation

```css
Background: linear-gradient(180deg, #132c68 0%, #1a3a7f 100%)
Text Color: white
Accent Dividers: rgba(244, 196, 48, 0.3)
Section Headers: #f4c430, bold, 1.1rem
```

### Buttons

**Primary Button**
```css
background: linear-gradient(135deg, #132c68 0%, #1a3a7f 100%);
color: white;
border-radius: 6px;
padding: 0.75rem 1.5rem;
font-weight: 600;
box-shadow: 0 4px 6px rgba(19, 44, 104, 0.2);
```

**Hover State**
```css
background: linear-gradient(135deg, #1a3a7f 0%, #132c68 100%);
box-shadow: 0 6px 8px rgba(19, 44, 104, 0.3);
transform: translateY(-2px);
```

### Tabs

**Inactive Tab**
```css
background-color: #f8f9fa;
color: #132c68;
border-radius: 6px;
font-weight: 600;
```

**Active Tab**
```css
background: linear-gradient(135deg, #132c68 0%, #1a3a7f 100%);
color: white;
border: 2px solid #f4c430;
```

### Metrics Cards

```css
background: white;
border-radius: 8px;
padding: 1.5rem;
box-shadow: 0 2px 8px rgba(19, 44, 104, 0.1);
border-top: 4px solid #132c68;
```

**Metric Value**
- Size: `2rem`
- Weight: `700 (Bold)`
- Color: `#132c68`

**Metric Delta**
- Weight: `600 (Semi-bold)`
- Color: Dynamic (green/red/gold)

---

## 📊 Chart Styling

### Color Assignments

**Primary Data (5TC Prices, Portfolio Values)**
- Line: `#132c68` (navy)
- Width: `2.5-3px`
- Fill: `rgba(19, 44, 104, 0.15)`

**Secondary Data (Dispersion, Benchmarks)**
- Line: `#5eb8e8` (teal)
- Width: `2.5px`
- Fill: `rgba(94, 184, 232, 0.15)`

**Highlights & Indicators**
- Line: `#f4c430` (gold)
- Width: `2.5-3px`
- Fill: `rgba(244, 196, 48, 0.2)`

**Reference Lines**
- Dash: `dash` or `dot`
- Color: `#f4c430` (gold) for important references
- Color: `#6c757d` (gray) for neutral references

### Chart Backgrounds

- Background: `white` or `rgba(248, 249, 250, 0.5)`
- Grid: `rgba(19, 44, 104, 0.1)`

---

## 💬 Message Boxes

### Info Box
```css
background: linear-gradient(135deg, #f0f7ff 0%, #e6f2ff 100%);
border-left: 5px solid #132c68;
border-radius: 8px;
padding: 1rem;
box-shadow: 0 2px 4px rgba(19, 44, 104, 0.1);
```

### Success Box
```css
background: linear-gradient(135deg, #f0fff4 0%, #e6f9ea 100%);
border-left: 5px solid #28a745;
border-radius: 8px;
```

### Warning Box
```css
background: linear-gradient(135deg, #fffbf0 0%, #fff8e6 100%);
border-left: 5px solid #f4c430;
border-radius: 8px;
```

### Error Box
```css
background: linear-gradient(135deg, #fff0f0 0%, #ffe6e6 100%);
border-left: 5px solid #dc3545;
border-radius: 8px;
```

---

## 🎪 Branding Elements

### Main Header Banner

```html
<div style='background: linear-gradient(135deg, #132c68 0%, #1a3a7f 100%); 
            padding: 2rem; 
            border-radius: 10px; 
            box-shadow: 0 4px 12px rgba(19, 44, 104, 0.3);'>
    <h1 style='color: white;'>⚓ Capesize Freight Analytics</h1>
    <p style='color: #f4c430;'>ENGELHART COMMODITIES TRADING</p>
    <p style='color: #5eb8e8;'>Where the Future Trades • Be Bold • Be Collaborative • Be Proactive</p>
</div>
```

### Sidebar Branding

```html
<div style='text-align: center; 
            padding: 1rem 0; 
            border-bottom: 2px solid #f4c430;'>
    <h2 style='color: white;'>🚢 FREIGHT ANALYTICS</h2>
    <p style='color: #5eb8e8;'>5TC Price Prediction Engine</p>
</div>
```

### Footer Branding

```html
<div style='text-align: center; 
            padding: 1.5rem; 
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
            border: 2px solid #132c68; 
            border-radius: 8px;'>
    <p style='color: #132c68; font-weight: 700;'>⚓ ENGELHART COMMODITIES TRADING</p>
    <p style='color: #5eb8e8;'>Freight Analytics Platform • Capesize Dispersion Intelligence</p>
    <p style='color: #f4c430;'>Where the Future Trades • Unlocking Opportunities in Global Freight Markets</p>
</div>
```

---

## 📱 Responsive Design

### Breakpoints

- **Desktop**: > 1200px (full width, 3-4 column layouts)
- **Tablet**: 768px - 1200px (2-3 column layouts)
- **Mobile**: < 768px (single column, stacked)

### Layout Principles

1. **White Space**: Generous padding and margins for breathing room
2. **Hierarchy**: Clear visual hierarchy with size, weight, color
3. **Consistency**: Repeated patterns for familiarity
4. **Accessibility**: High contrast ratios (WCAG AA compliant)

---

## 🎭 Brand Voice & Messaging

### Tone of Voice

- **Professional** but not stuffy
- **Confident** without arrogance  
- **Innovative** but grounded in data
- **Collaborative** - "we" not "I"
- **Action-oriented** - verbs over adjectives

### Key Phrases

- "Where the Future Trades"
- "Be Bold. Be Collaborative. Be Proactive."
- "Unlocking Opportunities in Global Freight Markets"
- "Advanced Analytics for Informed Trading Decisions"
- "Institutional-Grade Quantitative Intelligence"
- "Navigating Complex Markets with Agility"
- "Generating Value Through Data-Driven Insights"

### Section Labeling

Instead of generic terms, use professional trading desk language:

- ❌ "Settings" → ✅ "Configuration"
- ❌ "Results" → ✅ "Performance Analytics"
- ❌ "Data" → ✅ "Market Intelligence"
- ❌ "Help" → ✅ "Analytical Framework"
- ❌ "Export" → ✅ "Strategic Reporting"

---

## 🔧 Implementation Guidelines

### CSS Organization

1. Define color variables at top
2. Apply to base elements (body, headers)
3. Component-specific styles
4. State variations (hover, active)
5. Responsive adjustments

### Performance Considerations

- Use CSS gradients over images
- Optimize shadow effects
- Minimize animation complexity
- Cache static styles

### Accessibility

- Maintain 4.5:1 contrast ratio for text
- Use semantic HTML
- Provide alt text for all visuals
- Keyboard navigation support

---

## 🎨 Design Philosophy

### Engelhart Values Translation to Design

**"Be Bold"**
- Strong color choices (navy, gold)
- Confident typography (large, bold headers)
- Clear calls-to-action

**"Be Collaborative"**
- Transparent data presentation
- Shared context (info boxes, explanations)
- Inviting visual hierarchy

**"Be Proactive"**
- Actionable insights upfront
- Clear next steps
- Immediate visual feedback

**"Where the Future Trades"**
- Modern, forward-looking design
- Data-driven aesthetics
- Professional trading desk feel

---

## 📋 Checklist for Brand Compliance

- [ ] Primary color (#132c68) used for main elements
- [ ] Gold (#f4c430) used for accents and highlights
- [ ] Teal (#5eb8e8) used in data visualization
- [ ] Gradients applied to headers and key sections
- [ ] Professional typography (bold headers, clear hierarchy)
- [ ] Engelhart branding visible (header, footer, sidebar)
- [ ] Charts use brand color palette
- [ ] Message boxes styled with brand colors
- [ ] Buttons have gradient and hover effects
- [ ] White space and padding consistent
- [ ] Mobile-responsive layout
- [ ] Accessibility standards met

---

## 🚀 Future Enhancements

### Potential Additions

1. **Animated logo** - Subtle mosaic effect
2. **Loading animations** - Branded spinner/progress bar
3. **Dark mode** - Alternative navy/gold theme
4. **Custom icons** - Engelhart-specific freight icons
5. **Interactive tooltips** - Branded hover states
6. **Micro-interactions** - Smooth transitions
7. **Report templates** - Branded PDF exports

---

## 📞 Brand Contact

**Engelhart Commodities Trading**
- Website: [Engelhart values and mission]
- Values: Bold • Collaborative • Proactive • Professional
- Industry: Energy, Freight, Agriculture Commodities
- Focus: Global market opportunities, value generation, certainty in uncertain markets

---

## 📚 Resources

### Color Tools
- [Coolors.co](https://coolors.co/) - Color palette generator
- [Contrast Checker](https://webaim.org/resources/contrastchecker/) - Accessibility testing

### Design Inspiration
- Bloomberg Terminal - Professional data aesthetic
- Reuters Eikon - Financial markets UI
- Refinitiv Workspace - Trading desk design

---

**Last Updated:** December 18, 2025  
**Design System Version:** 1.0  
**Platform:** Streamlit-based Web Application  
**Target Audience:** Professional freight traders, commodities analysts, risk managers
