# Technology Stack

## Architecture
- **3-tier architecture**: Frontend (React) → Backend (Node.js/Express) → Database (SQLite)
- **RESTful API**: Clean separation between frontend and backend
- **Single Page Application (SPA)**: React with client-side routing

## Frontend Stack
- **React 18.2.0**: Component-based UI framework
- **React Router DOM 6.3.0**: Client-side routing
- **Axios 1.4.0**: HTTP client for API calls
- **CSS3**: Custom styling with responsive design
- **Create React App**: Build tooling and development server

## Backend Stack
- **Node.js**: JavaScript runtime
- **Express.js 4.18.2**: Web application framework
- **SQLite3 5.1.6**: Embedded database
- **CORS 2.8.5**: Cross-origin resource sharing
- **Body-parser 1.20.2**: Request body parsing middleware

## Development Tools
- **Nodemon 2.0.22**: Backend auto-restart during development
- **Concurrently 7.6.0**: Run multiple npm scripts simultaneously
- **React Scripts 5.0.1**: Create React App build tools

## Common Commands

### Initial Setup
```bash
npm run install-all    # Install all dependencies (root, backend, frontend)
```

### Development
```bash
npm run dev            # Start both backend and frontend servers
npm run server         # Start backend only (port 5000)
npm run client         # Start frontend only (port 3000)
```

### Backend Development
```bash
cd backend
npm run dev            # Start with nodemon (auto-restart)
npm start              # Start production server
```

### Frontend Development
```bash
cd frontend
npm start              # Start development server
npm run build          # Build for production
npm test               # Run tests
```

## API Conventions
- Base URL: `http://localhost:5000/api`
- RESTful endpoints with standard HTTP methods (GET, POST, PUT, DELETE)
- JSON request/response format
- Error responses include `{ error: "message" }` format