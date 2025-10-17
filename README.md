# 🎨 HealthChat - React TypeScript Frontend

A beautiful, minimal, and human-centered frontend for the Doctor Appointment System.

## Features

- **Clean, Minimal Design** - Beautiful gradient backgrounds and smooth animations
- **Real-time Chat Interface** - Intuitive chat with AI medical assistant
- **Fully Responsive** - Works perfectly on all devices
- **Fast & Optimized** - Built with performance in mind
- **Environment Aware** - Seamless local/production switching
- **♿ Accessible** - Built with accessibility best practices

## Tech Stack

- **React 19** - Latest React with concurrent features
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations
- **Lucide React** - Beautiful icons
- **Axios** - HTTP client for API calls

## Quick Start

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Installation
```bash
# Install dependencies
npm install

# Start development server
npm start

# Open http://localhost:3000
```

### Environment Setup
```bash
# Copy environment template
cp .env.example .env.local

# Edit .env.local with your settings
REACT_APP_API_BASE_URL=http://127.0.0.1:8000
REACT_APP_ENVIRONMENT=development
```

## Usage

### Chat Interface
- Enter your Patient ID (default: 12345678)
- Type messages or use quick actions
- Get instant responses from AI medical assistant

### Quick Actions
- "Book an appointment with Dr. Smith"
- "Check availability for cardiology" 
- "Cancel my appointment"
- "What are the clinic hours?"

## Development

### Available Scripts
```bash
npm start          # Development server
npm run build      # Production build
npm test           # Run tests
npm run type-check # TypeScript checking
npm run lint       # ESLint checking
```

### Project Structure
```
src/
├── components/          # Reusable components
│   ├── ChatInterface.tsx
│   ├── ErrorBoundary.tsx
│   └── StatusIndicator.tsx
├── api/                # API integration
│   ├── agentApi.ts
│   └── chatApi.ts
├── types/              # TypeScript types
└── App.tsx             # Main application
```

## Deployment

### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### Manual Build
```bash
# Build for production
npm run build

# Serve locally
npx serve -s build
```

### Environment Variables (Production)
Set these in your deployment platform:
```
REACT_APP_API_BASE_URL=your backend url (i used render for mine)
REACT_APP_ENVIRONMENT=production
```

## 🎨 Design System

### Colors
- **Primary**: Blue gradient (blue-500 to indigo-600)
- **Success**: Green (green-400, green-600)
- **Error**: Red (red-400, red-600)
- **Background**: Soft gradient (blue-50 to indigo-50)

### Typography
- **Font**: Inter (Google Fonts)
- **Headings**: Semibold to Bold
- **Body**: Regular (400)

### Components
- **Cards**: Rounded corners (rounded-2xl to rounded-3xl)
- **Buttons**: Gradient backgrounds with hover effects
- **Inputs**: Clean borders with focus states
- **Animations**: Smooth Framer Motion transitions

## API Integration

### Backend Connection
- Automatic connection testing
- Real-time status indicators
- Error handling and retry logic
- Environment-aware URL switching

### Supported Endpoints
- `POST /execute` - General queries
- `GET /health` - Health check
- `GET /agents/status` - Agent status
- `POST /api/v1/chat/sessions` - Chat sessions

## Customization

### Styling
Edit `tailwind.config.js` for theme customization:
```javascript
theme: {
  extend: {
    colors: {
      primary: { /* your prefered colors */ },
      // ...
    }
  }
}
```

### API Configuration
Update `src/api/agentApi.ts` for API changes:
```typescript
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000';
```

## Troubleshooting

### Common Issues

**Build Errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**API Connection Issues:**
- Check backend is running
- Verify CORS settings
- Check environment variables

**TypeScript Errors:**
```bash
# Run type checking
npm run type-check
```

## Browser Support

-  Chrome 90+
-  Firefox 88+
-  Safari 14+
-  Edge 90+

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is part of the Doctor Appointment Multi-Agent System.

## 🙏 Acknowledgments

- **Framer Motion** for beautiful animations
- **Tailwind CSS** for utility-first styling
- **Lucide** for clean, consistent icons
- **React Team** for the amazing framework

---

**Built with love for better healthcare experiences**