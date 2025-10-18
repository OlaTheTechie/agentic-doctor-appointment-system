# healthchat - react typescript frontend

A beautiful, minimal, and human-centered frontend for the Doctor Appointment System.

## features

- **Clean, Minimal Design** - Beautiful gradient backgrounds and smooth animations
- **Real-time Chat Interface** - Intuitive chat with AI medical assistant
- **Fully Responsive** - Works perfectly on all devices
- **Fast & Optimized** - Built with performance in mind
- **Environment Aware** - Seamless local/production switching
- **Accessible** - Built with accessibility best practices

## tech stack

- **React 19** - Latest React with concurrent features
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations
- **Lucide React** - Beautiful icons
- **Axios** - HTTP client for API calls

## quick start

### prerequisites
- Node.js 16+ 
- npm or yarn

### installation
```bash
# install dependencies
npm install

# start development server
npm start

# open http://localhost:3000
```

### environment setup
```bash
# copy environment template
cp .env.example .env.local

# edit .env.local with your settings
REACT_APP_API_BASE_URL=http://127.0.0.1:8000
REACT_APP_ENVIRONMENT=development
```

## usage

### chat interface
- Enter your Patient ID (default: 12345678)
- Type messages or use quick actions
- Get instant responses from AI medical assistant

### quick actions
- "Book an appointment with Dr. Smith"
- "Check availability for cardiology" 
- "Cancel my appointment"
- "What are the clinic hours?"

## development

### available scripts
```bash
npm start          # Development server
npm run build      # Production build
npm test           # Run tests
npm run type-check # TypeScript checking
npm run lint       # ESLint checking
```

### project structure
```
src/
├── components/          # reusable components
│   ├── ChatInterface.tsx
│   ├── ErrorBoundary.tsx
│   └── StatusIndicator.tsx
├── api/                # api integration
│   ├── agentApi.ts
│   └── chatApi.ts
├── types/              # typescript types
└── App.tsx             # Main application
```

## deployment

### vercel (recommended)
```bash
# install vercel cli
npm i -g vercel

# deploy
vercel --prod
```

### manual build
```bash
# build for production
npm run build

# serve locally
npx serve -s build
```

### environment variables (production)
Set these in your deployment platform:
```
REACT_APP_API_BASE_URL=your backend url (i used render for mine)
REACT_APP_ENVIRONMENT=production
```

## 🎨 design system

### colors
- **Primary**: Blue gradient (blue-500 to indigo-600)
- **Success**: Green (green-400, green-600)
- **Error**: Red (red-400, red-600)
- **Background**: Soft gradient (blue-50 to indigo-50)

### typography
- **Font**: Inter (Google Fonts)
- **Headings**: Semibold to Bold
- **Body**: Regular (400)

### components
- **Cards**: Rounded corners (rounded-2xl to rounded-3xl)
- **Buttons**: Gradient backgrounds with hover effects
- **Inputs**: Clean borders with focus states
- **Animations**: Smooth Framer Motion transitions

## api integration

### backend connection
- Automatic connection testing
- Real-time status indicators
- Error handling and retry logic
- Environment-aware URL switching

### supported endpoints
- `POST /execute` - General queries
- `GET /health` - Health check
- `GET /agents/status` - Agent status
- `POST /api/v1/chat/sessions` - Chat sessions

## customization

### styling
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

### api configuration
Update `src/api/agentApi.ts` for API changes:
```typescript
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000';
```

## troubleshooting

### common issues

**Build Errors:**
```bash
# clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**API Connection Issues:**
- Check backend is running
- Verify CORS settings
- Check environment variables

**TypeScript Errors:**
```bash
# run type checking
npm run type-check
```

## browser support

-  Chrome 90+
-  Firefox 88+
-  Safari 14+
-  Edge 90+

## contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## license

This project is part of the Doctor Appointment Multi-Agent System.

## 🙏 Acknowledgments

- **Framer Motion** for beautiful animations
- **Tailwind CSS** for utility-first styling
- **Lucide** for clean, consistent icons
- **React Team** for the amazing framework

---

**Built with love for better healthcare experiences**