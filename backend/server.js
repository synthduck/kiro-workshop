const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Database setup
const db = new sqlite3.Database('./ecommerce.db');

// Initialize database tables
db.serialize(() => {
  // Products table
  db.run(`CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT,
    emoji TEXT,
    category TEXT
  )`);

  // Cart items table
  db.run(`CREATE TABLE IF NOT EXISTS cart_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    quantity INTEGER DEFAULT 1,
    FOREIGN KEY (product_id) REFERENCES products (id)
  )`);

  // Reviews table
  db.run(`CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    user_name TEXT,
    rating INTEGER,
    comment TEXT,
    FOREIGN KEY (product_id) REFERENCES products (id)
  )`);

  // Insert sample products
  const sampleProducts = [
    { name: 'Smartphone', price: 699.99, description: 'Latest smartphone with advanced features', emoji: '📱', category: 'Electronics' },
    { name: 'Laptop', price: 1299.99, description: 'High-performance laptop for work and gaming', emoji: '💻', category: 'Electronics' },
    { name: 'Headphones', price: 199.99, description: 'Wireless noise-canceling headphones', emoji: '🎧', category: 'Electronics' },
    { name: 'Coffee Mug', price: 15.99, description: 'Ceramic coffee mug with beautiful design', emoji: '☕', category: 'Home' },
    { name: 'T-Shirt', price: 29.99, description: 'Comfortable cotton t-shirt', emoji: '👕', category: 'Clothing' },
    { name: 'Sneakers', price: 89.99, description: 'Comfortable running sneakers', emoji: '👟', category: 'Clothing' },
    { name: 'Book', price: 19.99, description: 'Bestselling fiction novel', emoji: '📚', category: 'Books' },
    { name: 'Watch', price: 249.99, description: 'Elegant wristwatch with leather strap', emoji: '⌚', category: 'Accessories' },
    { name: 'Sunglasses', price: 79.99, description: 'UV protection sunglasses', emoji: '🕶️', category: 'Accessories' },
    { name: 'Backpack', price: 59.99, description: 'Durable travel backpack', emoji: '🎒', category: 'Accessories' },
    { name: 'Camera', price: 899.99, description: 'Digital camera with 4K video', emoji: '📷', category: 'Electronics' },
    { name: 'Gaming Console', price: 499.99, description: 'Next-gen gaming console', emoji: '🎮', category: 'Electronics' },
    { name: 'Bicycle', price: 399.99, description: 'Mountain bike for outdoor adventures', emoji: '🚲', category: 'Sports' },
    { name: 'Guitar', price: 299.99, description: 'Acoustic guitar for music lovers', emoji: '🎸', category: 'Music' },
    { name: 'Plant', price: 24.99, description: 'Beautiful indoor plant', emoji: '🪴', category: 'Home' },
    { name: 'Perfume', price: 89.99, description: 'Luxury fragrance', emoji: '🧴', category: 'Beauty' },
    { name: 'Wallet', price: 49.99, description: 'Leather wallet with multiple compartments', emoji: '👛', category: 'Accessories' },
    { name: 'Keyboard', price: 129.99, description: 'Mechanical gaming keyboard', emoji: '⌨️', category: 'Electronics' },
    { name: 'Mouse', price: 69.99, description: 'Wireless gaming mouse', emoji: '🖱️', category: 'Electronics' },
    { name: 'Tablet', price: 449.99, description: 'Portable tablet for work and entertainment', emoji: '📱', category: 'Electronics' }
  ];

  const stmt = db.prepare('INSERT OR IGNORE INTO products (name, price, description, emoji, category) VALUES (?, ?, ?, ?, ?)');
  sampleProducts.forEach(product => {
    stmt.run(product.name, product.price, product.description, product.emoji, product.category);
  });
  stmt.finalize();

  // Insert sample reviews
  const sampleReviews = [
    { product_id: 1, user_name: 'John Doe', rating: 5, comment: 'Amazing phone! Great camera quality.' },
    { product_id: 1, user_name: 'Jane Smith', rating: 4, comment: 'Good performance, battery could be better.' },
    { product_id: 2, user_name: 'Mike Johnson', rating: 5, comment: 'Perfect for work and gaming!' },
    { product_id: 3, user_name: 'Sarah Wilson', rating: 4, comment: 'Great sound quality and comfort.' }
  ];

  const reviewStmt = db.prepare('INSERT OR IGNORE INTO reviews (product_id, user_name, rating, comment) VALUES (?, ?, ?, ?)');
  sampleReviews.forEach(review => {
    reviewStmt.run(review.product_id, review.user_name, review.rating, review.comment);
  });
  reviewStmt.finalize();
});

// API Routes

// Get all products
app.get('/api/products', (req, res) => {
  db.all('SELECT * FROM products', (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

// Get single product
app.get('/api/products/:id', (req, res) => {
  const { id } = req.params;
  db.get('SELECT * FROM products WHERE id = ?', [id], (err, row) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    if (!row) {
      res.status(404).json({ error: 'Product not found' });
      return;
    }
    res.json(row);
  });
});

// Get product reviews
app.get('/api/products/:id/reviews', (req, res) => {
  const { id } = req.params;
  db.all('SELECT * FROM reviews WHERE product_id = ?', [id], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

// Get cart items
app.get('/api/cart', (req, res) => {
  db.all(`
    SELECT ci.id, ci.quantity, p.name, p.price, p.emoji, p.id as product_id
    FROM cart_items ci
    JOIN products p ON ci.product_id = p.id
  `, (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

// Add item to cart
app.post('/api/cart', (req, res) => {
  const { product_id, quantity = 1 } = req.body;
  
  // Check if item already exists in cart
  db.get('SELECT * FROM cart_items WHERE product_id = ?', [product_id], (err, row) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    
    if (row) {
      // Update quantity if item exists
      db.run('UPDATE cart_items SET quantity = quantity + ? WHERE product_id = ?', 
        [quantity, product_id], function(err) {
        if (err) {
          res.status(500).json({ error: err.message });
          return;
        }
        res.json({ message: 'Cart updated successfully' });
      });
    } else {
      // Insert new item
      db.run('INSERT INTO cart_items (product_id, quantity) VALUES (?, ?)', 
        [product_id, quantity], function(err) {
        if (err) {
          res.status(500).json({ error: err.message });
          return;
        }
        res.json({ message: 'Item added to cart successfully' });
      });
    }
  });
});

// Update cart item quantity
app.put('/api/cart/:id', (req, res) => {
  const { id } = req.params;
  const { quantity } = req.body;
  
  db.run('UPDATE cart_items SET quantity = ? WHERE id = ?', [quantity, id], function(err) {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json({ message: 'Cart item updated successfully' });
  });
});

// Remove item from cart
app.delete('/api/cart/:id', (req, res) => {
  const { id } = req.params;
  
  db.run('DELETE FROM cart_items WHERE id = ?', [id], function(err) {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json({ message: 'Item removed from cart successfully' });
  });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});