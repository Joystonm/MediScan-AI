# MediScan-AI Design System

## Overview

The MediScan-AI design system is a comprehensive, modern healthcare-focused UI framework built with accessibility, trust, and professionalism in mind. It provides a consistent visual language across all medical AI applications.

## 🎨 Design Principles

### 1. **Trust & Professionalism**
- Clean, medical-grade aesthetics
- Consistent visual hierarchy
- Professional color palette
- Clear, readable typography

### 2. **Accessibility First**
- WCAG 2.1 AA compliant
- High contrast ratios
- Keyboard navigation support
- Screen reader friendly
- Reduced motion support

### 3. **Healthcare Context**
- Medical terminology consideration
- Status indicators for urgency levels
- Visual overlays for medical imaging
- Confidence scoring visualization

### 4. **Modern & Futuristic**
- Subtle gradients and shadows
- Smooth animations and transitions
- Card-based layouts
- Contemporary iconography

## 🎯 Color System

### Primary Palette (Medical Blue)
```css
--primary-50: #f0f9ff   /* Lightest blue backgrounds */
--primary-100: #e0f2fe  /* Light blue accents */
--primary-200: #bae6fd  /* Subtle blue elements */
--primary-300: #7dd3fc  /* Disabled states */
--primary-400: #38bdf8  /* Hover states */
--primary-500: #0ea5e9  /* Primary brand color */
--primary-600: #0284c7  /* Primary buttons */
--primary-700: #0369a1  /* Primary text */
--primary-800: #075985  /* Dark primary */
--primary-900: #0c4a6e  /* Darkest primary */
```

### Secondary Palette (Medical Green)
```css
--secondary-50: #f0fdf4   /* Success backgrounds */
--secondary-100: #dcfce7  /* Success accents */
--secondary-200: #bbf7d0  /* Light success */
--secondary-300: #86efac  /* Success hover */
--secondary-400: #4ade80  /* Success active */
--secondary-500: #22c55e  /* Success primary */
--secondary-600: #16a34a  /* Success buttons */
--secondary-700: #15803d  /* Success text */
--secondary-800: #166534  /* Dark success */
--secondary-900: #14532d  /* Darkest success */
```

### Neutral Palette
```css
--neutral-0: #ffffff     /* Pure white */
--neutral-50: #f8fafc    /* Background */
--neutral-100: #f1f5f9   /* Light backgrounds */
--neutral-200: #e2e8f0   /* Borders */
--neutral-300: #cbd5e1   /* Disabled elements */
--neutral-400: #94a3b8   /* Placeholder text */
--neutral-500: #64748b   /* Secondary text */
--neutral-600: #475569   /* Primary text */
--neutral-700: #334155   /* Headings */
--neutral-800: #1e293b   /* Dark text */
--neutral-900: #0f172a   /* Darkest text */
```

### Status Colors
- **Success**: `#22c55e` - Positive results, completed actions
- **Warning**: `#f59e0b` - Caution, medium priority
- **Error**: `#ef4444` - Critical issues, high priority
- **Info**: `#3b82f6` - Informational content

## 📝 Typography

### Font Family
- **Primary**: Inter (Google Fonts)
- **Monospace**: JetBrains Mono, Fira Code

### Type Scale
```css
--text-xs: 0.75rem     /* 12px - Labels, captions */
--text-sm: 0.875rem    /* 14px - Small text, metadata */
--text-base: 1rem      /* 16px - Body text */
--text-lg: 1.125rem    /* 18px - Large body text */
--text-xl: 1.25rem     /* 20px - Small headings */
--text-2xl: 1.5rem     /* 24px - Section headings */
--text-3xl: 1.875rem   /* 30px - Page headings */
--text-4xl: 2.25rem    /* 36px - Large headings */
--text-5xl: 3rem       /* 48px - Hero headings */
--text-6xl: 3.75rem    /* 60px - Display headings */
```

### Font Weights
- **Light (300)**: Subtle text, large displays
- **Normal (400)**: Body text, paragraphs
- **Medium (500)**: Emphasis, labels
- **Semibold (600)**: Headings, important text
- **Bold (700)**: Strong emphasis
- **Extrabold (800)**: Hero text, branding

## 🧩 Components

### Buttons

#### Primary Button
```jsx
<button className="btn btn-primary">
  Primary Action
</button>
```

#### Secondary Button
```jsx
<button className="btn btn-secondary">
  Secondary Action
</button>
```

#### Outline Button
```jsx
<button className="btn btn-outline">
  Outline Action
</button>
```

#### Ghost Button
```jsx
<button className="btn btn-ghost">
  Ghost Action
</button>
```

#### Button Sizes
- `btn-sm`: Small buttons (forms, inline actions)
- Default: Standard buttons
- `btn-lg`: Large buttons (CTAs, primary actions)

### Cards

#### Basic Card
```jsx
<div className="card">
  <div className="card-header">
    <h3 className="card-title">Card Title</h3>
    <p className="card-subtitle">Card subtitle</p>
  </div>
  <p>Card content goes here...</p>
</div>
```

#### Feature Card
```jsx
<div className="feature-card">
  <div className="feature-icon bg-primary-100 text-primary-600">
    <Icon />
  </div>
  <h3 className="feature-title">Feature Title</h3>
  <p className="feature-description">Feature description...</p>
  <button className="btn btn-primary w-full">Action</button>
</div>
```

#### Stats Card
```jsx
<div className="stats-card">
  <div className="stats-number text-primary-600">95%</div>
  <div className="stats-label">Accuracy Rate</div>
</div>
```

### Forms

#### Input Field
```jsx
<input 
  type="text" 
  className="input" 
  placeholder="Enter text..."
/>
```

#### Upload Area
```jsx
<div className="upload-area">
  <div className="upload-icon">
    <UploadIcon />
  </div>
  <h3>Drop files here</h3>
  <p>or click to browse</p>
</div>
```

### Badges

#### Status Badges
```jsx
<span className="badge badge-success">Success</span>
<span className="badge badge-warning">Warning</span>
<span className="badge badge-error">Error</span>
<span className="badge badge-info">Info</span>
```

### Progress Indicators

#### Confidence Bar
```jsx
<div className="confidence-bar">
  <div className="confidence-fill confidence-high" style={{ width: '87%' }} />
</div>
```

#### Loading Spinner
```jsx
<div className="loading-spinner" />
```

#### Skeleton Loader
```jsx
<div className="skeleton h-4 w-32" />
```

## 🎭 Icons

### Medical Icons
- `HeartIcon` - Cardiovascular, favorites
- `StethoscopeIcon` - Medical examination
- `XRayIcon` - Radiology, imaging
- `ChatIcon` - Triage, communication

### Action Icons
- `UploadIcon` - File upload
- `DownloadIcon` - File download
- `SendIcon` - Submit, send
- `SearchIcon` - Search functionality

### Status Icons
- `CheckIcon` - Success, completion
- `CheckCircleIcon` - Verified, approved
- `XIcon` - Close, cancel
- `ExclamationIcon` - Warning, attention
- `AlertIcon` - Information, notice

### Usage
```jsx
import { HeartIcon } from './components/common/Icons';

<HeartIcon className="w-6 h-6 text-primary-600" />
```

## 📐 Layout System

### Container
```jsx
<div className="container mx-auto px-4">
  Content goes here...
</div>
```

### Grid System
```jsx
<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
  <div>Column 1</div>
  <div>Column 2</div>
  <div>Column 3</div>
</div>
```

### Spacing Scale
```css
--space-1: 0.25rem    /* 4px */
--space-2: 0.5rem     /* 8px */
--space-3: 0.75rem    /* 12px */
--space-4: 1rem       /* 16px */
--space-5: 1.25rem    /* 20px */
--space-6: 1.5rem     /* 24px */
--space-8: 2rem       /* 32px */
--space-10: 2.5rem    /* 40px */
--space-12: 3rem      /* 48px */
--space-16: 4rem      /* 64px */
--space-20: 5rem      /* 80px */
--space-24: 6rem      /* 96px */
```

## 🎨 Visual Effects

### Shadows
```css
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05)
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)
--shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25)
```

### Border Radius
```css
--radius-sm: 0.375rem   /* 6px */
--radius-md: 0.5rem     /* 8px */
--radius-lg: 0.75rem    /* 12px */
--radius-xl: 1rem       /* 16px */
--radius-2xl: 1.5rem    /* 24px */
--radius-full: 9999px   /* Fully rounded */
```

### Transitions
```css
--transition-fast: 150ms ease-in-out
--transition-normal: 250ms ease-in-out
--transition-slow: 350ms ease-in-out
```

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

### Responsive Classes
```jsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  Responsive grid
</div>
```

## ♿ Accessibility Features

### Focus Management
- Visible focus rings on all interactive elements
- Logical tab order
- Skip links for navigation

### Color Contrast
- Minimum 4.5:1 contrast ratio for normal text
- Minimum 3:1 contrast ratio for large text
- High contrast mode support

### Screen Reader Support
- Semantic HTML structure
- ARIA labels and descriptions
- Alternative text for images

### Keyboard Navigation
- All interactive elements keyboard accessible
- Escape key closes modals/dropdowns
- Arrow keys for navigation where appropriate

## 🌙 Dark Mode Support

The design system includes automatic dark mode support based on user preferences:

```css
@media (prefers-color-scheme: dark) {
  :root {
    --neutral-0: #1e293b;
    --neutral-50: #0f172a;
    /* ... other dark mode colors */
  }
}
```

## 🎯 Medical-Specific Components

### Confidence Visualization
```jsx
<div className="confidence-bar">
  <div className="confidence-fill confidence-high" style={{ width: '87%' }} />
</div>
```

### Result Cards
```jsx
<div className="result-card">
  <div className="result-header">
    <h3>Analysis Result</h3>
    <span className="badge badge-success">High Confidence</span>
  </div>
  <div className="result-content">
    Analysis details...
  </div>
</div>
```

### Upload Areas
```jsx
<div className="upload-area">
  <div className="upload-icon">
    <UploadIcon />
  </div>
  <h3>Upload Medical Image</h3>
  <p>Drag and drop or click to browse</p>
  <div className="text-sm text-neutral-400">
    Supported: JPG, PNG, DICOM
  </div>
</div>
```

## 🚀 Implementation

### Installation
1. Import the design system CSS:
```jsx
import './styles/design-system.css';
```

2. Use components with appropriate classes:
```jsx
<button className="btn btn-primary">
  Get Started
</button>
```

3. Import icons as needed:
```jsx
import { HeartIcon } from './components/common/Icons';
```

### Best Practices

1. **Consistency**: Always use design system classes
2. **Accessibility**: Include proper ARIA labels
3. **Performance**: Use CSS custom properties for theming
4. **Maintainability**: Follow component patterns
5. **Testing**: Test with keyboard navigation and screen readers

## 📚 Resources

- **Figma Design File**: [Link to design file]
- **Component Storybook**: [Link to storybook]
- **Accessibility Guidelines**: WCAG 2.1 AA
- **Color Palette Tool**: [Link to color tool]
- **Icon Library**: Heroicons-based custom set

## 🔄 Updates & Versioning

The design system follows semantic versioning:
- **Major**: Breaking changes to component APIs
- **Minor**: New components or non-breaking enhancements
- **Patch**: Bug fixes and minor improvements

Current Version: **2.0.0**

---

**Built with ❤️ for better healthcare accessibility**
