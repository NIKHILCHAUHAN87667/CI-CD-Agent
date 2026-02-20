# AI DevOps Agent - Frontend

Modern React frontend for the AI DevOps Agent with TailwindCSS and GitHub OAuth integration.

## 🚀 Features

- **GitHub OAuth Authentication**: Secure login with GitHub
- **Real-time Dashboard**: Monitor agent runs and statistics
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern UI**: Built with TailwindCSS and custom components
- **State Management**: Zustand for efficient state handling
- **API Integration**: Seamless connection to backend API

## 📦 Tech Stack

- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Zustand**: Lightweight state management
- **Axios**: HTTP client for API calls
- **Lucide React**: Beautiful icon library
- **React Hot Toast**: Toast notifications

## 🛠️ Development

### Prerequisites
- Node.js 18+ and npm
- Backend API running on http://localhost:8000

### Install Dependencies
```bash
npm install
```

### Configure Environment
Create `.env` file:
```env
VITE_API_URL=http://localhost:8000
VITE_GITHUB_CLIENT_ID=your_github_client_id
VITE_GITHUB_REDIRECT_URI=http://localhost:3000/auth/callback
```

### Run Development Server
```bash
npm run dev
```

App will be available at http://localhost:3000

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## 📁 Project Structure

```
src/
├── components/       # Reusable UI components
│   ├── ui/          # Base UI components (Button, Card, etc.)
│   ├── Header.jsx   # Navigation header
│   ├── Layout.jsx   # Page layout wrapper
│   └── ProtectedRoute.jsx  # Auth guard
├── pages/           # Page components
│   ├── HomePage.jsx
│   ├── LoginPage.jsx
│   ├── DashboardPage.jsx
│   ├── RunAgentPage.jsx
│   ├── ResultsPage.jsx
│   └── HistoryPage.jsx
├── services/        # API services
│   └── api.js       # API client and endpoints
├── store/           # State management
│   └── index.js     # Zustand stores
├── lib/             # Utilities
│   └── utils.js     # Helper functions
├── App.jsx          # Main app component
├── main.jsx         # Entry point
└── index.css        # Global styles
```

## 🎨 UI Components

### Base Components
- `Button`: Versatile button with variants
- `Card`: Content container with header/footer
- `Input/Label`: Form inputs
- `Spinner`: Loading indicator

### Layout Components
- `Header`: Navigation bar with auth status
- `Layout`: Page wrapper with header and footer
- `ProtectedRoute`: Auth guard for private routes

## 🔐 Authentication Flow

1. User clicks "Login with GitHub"
2. Redirects to GitHub OAuth page
3. User authorizes the application
4. GitHub redirects back to `/auth/callback`
5. Frontend exchanges code for JWT token
6. User is logged in and redirected to dashboard

## 📱 Pages

### HomePage (`/`)
- Landing page with features
- Call-to-action for login
- How it works section

### LoginPage (`/login`)
- GitHub OAuth login button  
- Feature highlights
- Auto-redirects if already logged in

### DashboardPage (`/dashboard`)
- Statistics overview
- Recent runs list
- Quick access to run agent

### RunAgentPage (`/run`)
- Configure and run agent
- Form inputs for repo details
- Real-time execution
- Branch name preview

### ResultsPage (`/results/:id`)
- Detailed run results
- Fixes breakdown
- Error statistics
- Run metadata

### HistoryPage (`/history`)
- All past runs
- Search and filter
- Status indicators

## 🎯 API Integration

All API calls are handled through `src/services/api.js`:

```javascript
import { agentAPI } from '@/services/api';

// Run agent
const result = await agentAPI.runAgent(data);

// Get all runs
const runs = await agentAPI.getRuns();

// Get specific run
const run = await agentAPI.getRun(id);
```

## 🌐 Deployment

### Vercel (Recommended)
1. Push code to GitHub
2. Import project on Vercel
3. Set root directory to `frontend`
4. Add environment variables
5. Deploy!

### Netlify
1. Push code to GitHub
2. Connect repository
3. Build command: `npm run build`
4. Publish directory: `dist`
5. Add environment variables

### Docker
```bash
docker build -t ai-devops-frontend .
docker run -p 3000:80 ai-devops-frontend
```

## 🔧 Configuration

### Environment Variables
- `VITE_API_URL`: Backend API URL
- `VITE_GITHUB_CLIENT_ID`: GitHub OAuth Client ID
- `VITE_GITHUB_REDIRECT_URI`: OAuth callback URL

### Path Aliases
Configured in `vite.config.js` and `jsconfig.json`:
```javascript
import { Component } from '@/components/Component';
```

## 📊 State Management

Using Zustand for state:

### Auth Store
- `user`: Current user object
- `token`: JWT token
- `isAuthenticated`: Boolean
- `login()`: Login action
- `logout()`: Logout action

### Agent Store
- `runs`: Array of agent runs
- `currentRun`: Active run details
- `isRunning`: Boolean
- Actions for managing runs

## 🎨 Theming

TailwindCSS with custom theme in `tailwind.config.js`:
- Primary color: Blue
- Support for dark mode
- Custom spacing and borders
- Responsive breakpoints

## 🐛 Troubleshooting

**Port already in use**:
```bash
# Kill process on port 3000
npx kill-port 3000
```

**Build errors**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**API not connecting**:
- Check `VITE_API_URL` in `.env`
- Ensure backend is running
- Check CORS settings

## 📝 License

Part of the AI DevOps Agent project - RIFT PUNE HACK 122

---

Built with ❤️ using React and TailwindCSS

# AI DevOps Agent - Frontend

Modern React frontend for the AI DevOps Agent with TailwindCSS and GitHub OAuth integration.

## 🚀 Features

- **GitHub OAuth Authentication**: Secure login with GitHub
- **Real-time Dashboard**: Monitor agent runs and statistics
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern UI**: Built with TailwindCSS and custom components
- **State Management**: Zustand for efficient state handling
- **API Integration**: Seamless connection to backend API

## 📦 Tech Stack

- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Zustand**: Lightweight state management
- **Axios**: HTTP client for API calls
- **Lucide React**: Beautiful icon library
- **React Hot Toast**: Toast notifications

## 🛠️ Development

### Prerequisites
- Node.js 18+ and npm
- Backend API running on https://cicdagentapi.onrender.com

### Install Dependencies
```bash
npm install
```

### Configure Environment
Create `.env` file:
```env
VITE_API_URL=https://cicdagentapi.onrender.com
VITE_GITHUB_CLIENT_ID=your_github_client_id
VITE_GITHUB_REDIRECT_URI=http://localhost:3000/auth/callback
```

### Run Development Server
```bash
npm run dev
```

App will be available at http://localhost:3000

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## 📁 Project Structure

```
src/
├── components/       # Reusable UI components
│   ├── ui/          # Base UI components (Button, Card, etc.)
│   ├── Header.jsx   # Navigation header
│   ├── Layout.jsx   # Page layout wrapper
│   └── ProtectedRoute.jsx  # Auth guard
├── pages/           # Page components
│   ├── HomePage.jsx
│   ├── LoginPage.jsx
│   ├── DashboardPage.jsx
│   ├── RunAgentPage.jsx
│   ├── ResultsPage.jsx
│   └── HistoryPage.jsx
├── services/        # API services
│   └── api.js       # API client and endpoints
├── store/           # State management
│   └── index.js     # Zustand stores
├── lib/             # Utilities
│   └── utils.js     # Helper functions
├── App.jsx          # Main app component
├── main.jsx         # Entry point
└── index.css        # Global styles
```

## 🎨 UI Components

### Base Components
- `Button`: Versatile button with variants
- `Card`: Content container with header/footer
- `Input/Label`: Form inputs
- `Spinner`: Loading indicator

### Layout Components
- `Header`: Navigation bar with auth status
- `Layout`: Page wrapper with header and footer
- `ProtectedRoute`: Auth guard for private routes

## 🔐 Authentication Flow

1. User clicks "Login with GitHub"
2. Redirects to GitHub OAuth page
3. User authorizes the application
4. GitHub redirects back to `/auth/callback`
5. Frontend exchanges code for JWT token
6. User is logged in and redirected to dashboard

## 📱 Pages

### HomePage (`/`)
- Landing page with features
- Call-to-action for login
- How it works section

### LoginPage (`/login`)
- GitHub OAuth login button  
- Feature highlights
- Auto-redirects if already logged in

### DashboardPage (`/dashboard`)
- Statistics overview
- Recent runs list
- Quick access to run agent

### RunAgentPage (`/run`)
- Configure and run agent
- Form inputs for repo details
- Real-time execution
- Branch name preview

### ResultsPage (`/results/:id`)
- Detailed run results
- Fixes breakdown
- Error statistics
- Run metadata

### HistoryPage (`/history`)
- All past runs
- Search and filter
- Status indicators

## 🎯 API Integration

All API calls are handled through `src/services/api.js`:

```javascript
import { agentAPI } from '@/services/api';

// Run agent
const result = await agentAPI.runAgent(data);

// Get all runs
const runs = await agentAPI.getRuns();

// Get specific run
const run = await agentAPI.getRun(id);
```

## 🌐 Deployment

### Vercel (Recommended)
1. Push code to GitHub
2. Import project on Vercel
3. Set root directory to `frontend`
4. Add environment variables
5. Deploy!

### Netlify
1. Push code to GitHub
2. Connect repository
3. Build command: `npm run build`
4. Publish directory: `dist`
5. Add environment variables

### Docker
```bash
docker build -t ai-devops-frontend .
docker run -p 3000:80 ai-devops-frontend
```

## 🔧 Configuration

### Environment Variables
- `VITE_API_URL`: Backend API URL
- `VITE_GITHUB_CLIENT_ID`: GitHub OAuth Client ID
- `VITE_GITHUB_REDIRECT_URI`: OAuth callback URL

### Path Aliases
Configured in `vite.config.js` and `jsconfig.json`:
```javascript
import { Component } from '@/components/Component';
```

## 📊 State Management

Using Zustand for state:

### Auth Store
- `user`: Current user object
- `token`: JWT token
- `isAuthenticated`: Boolean
- `login()`: Login action
- `logout()`: Logout action

### Agent Store
- `runs`: Array of agent runs
- `currentRun`: Active run details
- `isRunning`: Boolean
- Actions for managing runs

## 🎨 Theming

TailwindCSS with custom theme in `tailwind.config.js`:
- Primary color: Blue
- Support for dark mode
- Custom spacing and borders
- Responsive breakpoints

## 🐛 Troubleshooting

**Port already in use**:
```bash
# Kill process on port 3000
npx kill-port 3000
```

**Build errors**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**API not connecting**:
- Check `VITE_API_URL` in `.env`
- Ensure backend is running
- Check CORS settings

## 📝 License

Part of the AI DevOps Agent project - RIFT PUNE HACK 122

---

Built with ❤️ using React and TailwindCSS
