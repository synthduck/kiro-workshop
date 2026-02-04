# Project Structure

## Root Level
```
ecommerce-app/
├── package.json          # Root package with dev scripts
├── README.md             # Project documentation
├── backend/              # Node.js/Express API server
├── frontend/             # React application
└── .kiro/               # Kiro IDE configuration
```

## Backend Structure (`/backend`)
```
backend/
├── package.json          # Backend dependencies
├── server.js            # Main Express server file
├── ecommerce.db         # SQLite database (auto-generated)
└── node_modules/        # Backend dependencies
```

### Backend Patterns
- **Single file architecture**: All routes and database logic in `server.js`
- **Database initialization**: Tables created on startup with sample data
- **RESTful routes**: Organized by resource (`/api/products`, `/api/cart`)
- **Error handling**: Consistent JSON error responses

## Frontend Structure (`/frontend`)
```
frontend/
├── package.json          # Frontend dependencies
├── public/
│   └── index.html       # HTML template
├── src/
│   ├── index.js         # React app entry point
│   ├── index.css        # Global styles
│   ├── App.js           # Main app component with routing
│   └── components/      # React components
│       ├── HomePage.js      # Product listing page
│       ├── ProductPage.js   # Product detail page
│       └── CartPage.js      # Shopping cart page
└── node_modules/        # Frontend dependencies
```

### Frontend Patterns
- **Component-based architecture**: Each page is a separate component
- **Functional components**: Using React hooks (useState, useEffect)
- **Client-side routing**: React Router for navigation
- **API integration**: Axios for HTTP requests to backend
- **Responsive design**: CSS Grid and Flexbox with mobile breakpoints

## File Naming Conventions
- **Components**: PascalCase (e.g., `HomePage.js`, `ProductPage.js`)
- **Files**: camelCase for JavaScript, kebab-case for config files
- **Database**: snake_case for table and column names

## Code Organization
- **Backend**: All logic in single `server.js` file for simplicity
- **Frontend**: One component per file, shared styles in `index.css`
- **Database**: SQLite with in-memory initialization and sample data seeding
- **Configuration**: Package.json scripts for development workflow

## Development Workflow
- **Concurrent development**: Both servers run simultaneously via `npm run dev`
- **Proxy setup**: Frontend proxies API calls to backend (port 3000 → 5000)
- **Auto-reload**: Nodemon for backend, React dev server for frontend