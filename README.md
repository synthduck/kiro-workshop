# E-Commerce Website

A simple e-commerce website built with React frontend, Node.js backend, and SQLite database following 3-tier architecture.

## Features

### Frontend (React)
- **Home Page**: Product listing with 20 sample products using emojis as product images
- **Product Page**: Detailed product view with description, price, quantity selector, add-to-cart functionality, and customer reviews
- **Shopping Cart Page**: Cart management with quantity updates, item removal, and total cost calculation

### Backend (Node.js + Express)
- RESTful API endpoints for products and cart management
- SQLite database for data persistence
- CORS enabled for frontend-backend communication

### Database (SQLite)
- Products table with sample data
- Cart items table for shopping cart functionality
- Reviews table for customer feedback

## Project Structure

```
ecommerce-app/
├── backend/
│   ├── package.json
│   ├── server.js
│   └── ecommerce.db (created automatically)
├── frontend/
│   ├── package.json
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── index.js
│       ├── index.css
│       ├── App.js
│       └── components/
│           ├── HomePage.js
│           ├── ProductPage.js
│           └── CartPage.js
├── package.json
└── README.md
```

## Installation & Setup

1. **Install root dependencies:**
   ```bash
   npm run install-all
   ```

2. **Start the development servers:**
   ```bash
   npm run dev
   ```

   This will start:
   - Backend server on http://localhost:5000
   - Frontend development server on http://localhost:3000

## API Endpoints

- `GET /api/products` - Get all products
- `GET /api/products/:id` - Get single product
- `GET /api/products/:id/reviews` - Get product reviews
- `GET /api/cart` - Get cart items
- `POST /api/cart` - Add item to cart
- `PUT /api/cart/:id` - Update cart item quantity
- `DELETE /api/cart/:id` - Remove item from cart

## Sample Products

The application includes 20 sample products across different categories:
- Electronics (smartphones, laptops, headphones, etc.)
- Clothing (t-shirts, sneakers)
- Home & Garden (coffee mugs, plants)
- Books & Music
- Sports & Accessories

Each product includes an emoji as a visual representation, making the interface fun and engaging.

## Technologies Used

- **Frontend**: React, React Router, Axios, CSS3
- **Backend**: Node.js, Express.js, SQLite3, CORS
- **Database**: SQLite
- **Development**: Concurrently for running both servers

## Usage

1. Browse products on the home page
2. Click on any product to view details
3. Add products to cart with desired quantity
4. Manage cart items (update quantities, remove items)
5. View total cost and proceed to checkout

The application demonstrates a complete e-commerce flow with a clean, responsive design and full CRUD operations for cart management.