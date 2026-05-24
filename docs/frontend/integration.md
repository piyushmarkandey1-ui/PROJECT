# Frontend Integration Guide

## Getting Started

### Installation
```bash
cd frontend
npm install
```

### Development Server
```bash
npm run dev
```
Visit http://localhost:5173

### Production Build
```bash
npm run build
npm run preview
```

## Environment Configuration

Create a `.env` file in the frontend directory:
```env
VITE_API_URL=http://localhost:8000
```

**Production (Vercel):**
Set `VITE_API_URL` in Vercel environment variables to your backend URL.

## Integrating ChatWidget

### Basic Integration
```jsx
import ChatWidget from './components/ChatWidget';

function App() {
  return (
    <div className="app">
      <ChatWidget
        companySlug="your-company-slug"
        companyName="Your Company Name"
      />
    </div>
  );
}
```

### Advanced Integration
```jsx
import ChatWidget from './components/ChatWidget';
import { useState } from 'react';

function App() {
  const [company, setCompany] = useState({
    slug: 'acme-corp',
    name: 'Acme Corporation',
    initialMessage: 'Welcome to Acme Corp! How can we help?'
  });

  return (
    <div className="app">
      <ChatWidget
        companySlug={company.slug}
        companyName={company.name}
        initialMessage={company.initialMessage}
      />
    </div>
  );
}
```

## Customization

### Styling
The project uses Tailwind CSS. Customize in `tailwind.config.js`:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
        secondary: '#64748b',
      },
    },
  },
  plugins: [],
}
```

### Component Customization
Override component styles using Tailwind utility classes or custom CSS in `index.css`.

## Deployment (Vercel)

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Deploy
```bash
cd frontend
vercel
```

### 3. Production Deployment
```bash
vercel --prod
```

### 4. Set Environment Variables
In Vercel dashboard:
- Go to Settings → Environment Variables
- Add `VITE_API_URL` with your backend URL

## Testing

### Unit Tests
```bash
# Add test framework (e.g., Jest, Vitest)
npm install -D vitest @testing-library/react @testing-library/jest-dom
```

### E2E Tests
```bash
# Add Playwright or Cypress
npm install -D @playwright/test
npx playwright install
```

## Performance Optimization

### Code Splitting
Vite automatically code-splits your application.

### Lazy Loading
```jsx
import { lazy, Suspense } from 'react';

const ChatWidget = lazy(() => import('./components/ChatWidget'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ChatWidget />
    </Suspense>
  );
}
```

### Image Optimization
Use Vite's built-in image optimization or a CDN.

## Troubleshooting

### Common Issues

1. **API connection errors**
   - Verify `VITE_API_URL` is correct
   - Check CORS settings on backend
   - Ensure backend is running

2. **Chat not loading**
   - Check browser console for errors
   - Verify company slug is valid
   - Check network tab for failed requests

3. **Styling issues**
   - Clear browser cache
   - Verify Tailwind config
   - Check for conflicting CSS

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Accessibility

- ARIA labels on interactive elements
- Keyboard navigation support
- High contrast mode compatibility
- Screen reader support
