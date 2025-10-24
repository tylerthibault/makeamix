# MakeAMix Style Guide

## 🎨 Core Principles

### 1. **NO INLINE STYLES - EVER**
- ❌ **NEVER** use `style="..."` attributes
- ✅ **ALWAYS** use CSS classes
- ✅ Create custom CSS classes when needed
- ✅ Use CSS custom properties for dynamic values

### 2. **Use Project CSS Variables**
All styling should leverage our custom CSS variables defined in `main.css`:

#### **Color Variables:**
```css
/* Light Mode */
--bs-primary: #1f4168
--bs-secondary: #2b9c89
--bs-success: #d1fae5
--bs-info: #dbeafe
--bs-warning: #fef3c7
--bs-danger: #fee2e2
--bs-light: #f9fafb
--bs-dark: #111827

/* Background Variables */
--bg-primary: #ffffff
--bg-secondary: #f9fafb
--text-primary: #111827
--text-secondary: #6b7280
--border-color: #e5e7eb
--link-color: #4f46e5

/* Gradients */
--primary-gradient: linear-gradient(135deg, var(--bs-primary) 0%, var(--bs-secondary) 100%)
--secondary-gradient: linear-gradient(135deg, var(--bs-secondary) 0%, var(--bs-primary) 100%)
```

### 3. **Use Bootstrap Addon Classes**
Leverage classes from `bootstrap_addons/colors.css`:

#### **Text Colors:**
```html
<span class="text-primary">Primary text</span>
<span class="text-secondary">Secondary text</span>
<span class="text-success">Success text</span>
```

#### **Background Colors:**
```html
<div class="bg-primary">Primary background</div>
<div class="bg-secondary">Secondary background</div>
<div class="bg-primary-gradient">Gradient background</div>
```

#### **Button Colors:**
```html
<button class="btn btn-primary">Primary button</button>
<button class="btn btn-secondary">Secondary button</button>
```

## 📐 Layout Guidelines

### 1. **Spacing & Sizing**
Use Bootstrap spacing utilities and our custom sizing classes:

```html
<!-- Spacing -->
<div class="p-4 m-3 mb-5">Content</div>

<!-- Custom spacing from sizing.css -->
<div class="p-6 m-8">Extended spacing</div>
```

### 2. **Responsive Design**
Always use Bootstrap responsive classes:

```html
<!-- Responsive columns -->
<div class="col-lg-6 col-md-8 col-sm-12">

<!-- Responsive display -->
<div class="d-none d-md-block">

<!-- Responsive text -->
<h1 class="display-1 display-md-2">
```

### 3. **Flexbox & Grid**
Use Bootstrap flex utilities:

```html
<div class="d-flex justify-content-center align-items-center">
<div class="d-flex flex-column flex-md-row">
```

## 🎭 Component Styling

### 1. **Hero Sections**
Standard hero section structure:

```html
<section class="hero-[style] min-vh-100 d-flex align-items-center position-relative">
    <div class="container position-relative z-3">
        <div class="row align-items-center">
            <!-- Content -->
        </div>
    </div>
</section>
```

### 2. **Animations**
Create CSS classes for animations:

```css
/* ✅ CORRECT - CSS Class */
@keyframes floating {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-20px); }
}

.floating-animation {
    animation: floating 3s ease-in-out infinite;
}
```

```html
<!-- ✅ CORRECT Usage -->
<i class="bi bi-music-note floating-animation"></i>

<!-- ❌ WRONG - Inline style -->
<i class="bi bi-music-note" style="animation: floating 3s ease-in-out infinite;"></i>
```

### 3. **Positioning**
Use Bootstrap position utilities with CSS classes for specific values:

```css
/* ✅ CORRECT - CSS Classes */
.hero-particle-1 {
    top: 10%;
    left: 5%;
    animation-delay: 0s;
}

.hero-particle-2 {
    top: 20%;
    left: 90%;
    animation-delay: 2s;
}
```

```html
<!-- ✅ CORRECT Usage -->
<div class="particle position-absolute hero-particle-1"></div>

<!-- ❌ WRONG - Inline styles -->
<div class="particle position-absolute" style="top: 10%; left: 5%;"></div>
```

## 🎨 Color Usage Standards

### 1. **Primary Palette**
- **Primary (`--bs-primary`)**: Main brand color, buttons, links
- **Secondary (`--bs-secondary`)**: Accent color, secondary buttons
- **Success**: Positive actions, checkmarks, success states
- **Warning**: Attention, highlights, call-to-action
- **Danger**: Errors, warnings, delete actions

### 2. **Background Hierarchy**
- **`--bg-primary`**: Main page background
- **`--bg-secondary`**: Card backgrounds, sections
- **Gradients**: Hero sections, special elements

### 3. **Text Hierarchy**
- **`--text-primary`**: Main content text
- **`--text-secondary`**: Subdued text, captions

## 🔧 CSS Organization

### 1. **File Structure**
```
css/
├── main.css (imports & variables)
├── bootstrap_addons/
│   ├── colors.css (color utilities)
│   ├── sizing.css (spacing utilities)
│   ├── buttons.css (button styles)
│   └── basic.css (basic utilities)
└── components/
    ├── hero.css (hero-specific styles)
    └── [component].css
```

### 2. **Component-Specific CSS**
Create dedicated CSS files for complex components:

```css
/* components/hero.css */
.hero-gradient {
    background: var(--primary-gradient);
}

.hero-particle {
    width: 8px;
    height: 8px;
    background: var(--bs-primary);
    border-radius: 50%;
    opacity: 0.7;
}

.hero-particle-1 { top: 10%; left: 5%; animation-delay: 0s; }
.hero-particle-2 { top: 20%; left: 90%; animation-delay: 2s; }
/* etc... */
```

## 📱 Responsive Design Standards

### 1. **Breakpoint Usage**
```html
<!-- Mobile-first approach -->
<div class="col-12 col-md-6 col-lg-4">
<h1 class="fs-4 fs-md-3 fs-lg-1">
<div class="p-3 p-md-4 p-lg-5">
```

### 2. **Display Classes**
```html
<div class="d-none d-md-block">Desktop only</div>
<div class="d-block d-md-none">Mobile only</div>
```

## ✅ Examples

### **CORRECT Implementation:**

```html
<!-- HTML -->
<section class="hero-example min-vh-100 bg-primary-gradient">
    <div class="container">
        <h1 class="text-white display-1 fw-bold">Title</h1>
        <div class="hero-particles">
            <div class="hero-particle hero-particle-1"></div>
            <div class="hero-particle hero-particle-2"></div>
        </div>
    </div>
</section>
```

```css
/* CSS */
.hero-example {
    position: relative;
    overflow: hidden;
}

.hero-particle {
    position: absolute;
    width: 8px;
    height: 8px;
    background: var(--bs-secondary);
    border-radius: 50%;
    animation: particleFloat 6s ease-in-out infinite;
}

.hero-particle-1 {
    top: 10%;
    left: 5%;
    animation-delay: 0s;
}
```

### **WRONG Implementation:**

```html
<!-- ❌ NEVER DO THIS -->
<section style="min-height: 100vh; background: linear-gradient(135deg, #1f4168 0%, #2b9c89 100%);">
    <div style="position: relative;">
        <h1 style="color: white; font-size: 4rem;">Title</h1>
        <div style="position: absolute; top: 10%; left: 5%; width: 8px; height: 8px; background: #2b9c89;"></div>
    </div>
</section>
```

## 🎯 Key Reminders

1. **NEVER use inline styles** (`style="..."`)
2. **ALWAYS use our CSS variables** for colors and spacing
3. **ALWAYS use Bootstrap classes** when available
4. **CREATE CSS classes** for custom styling
5. **ORGANIZE CSS** in appropriate files
6. **FOLLOW responsive** design patterns
7. **USE semantic** HTML structure

## 🔄 Theme Support

All styles must support both light and dark themes through CSS variables. Never hardcode colors - always use our variable system.

```css
/* ✅ CORRECT - Uses variables */
.custom-element {
    background-color: var(--bg-primary);
    color: var(--text-primary);
    border-color: var(--border-color);
}

/* ❌ WRONG - Hardcoded colors */
.custom-element {
    background-color: #ffffff;
    color: #111827;
    border-color: #e5e7eb;
}
```

---

**Remember: Consistency is key. Follow these guidelines to ensure maintainable, scalable, and theme-compatible code.**