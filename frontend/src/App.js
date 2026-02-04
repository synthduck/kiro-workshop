import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import HomePage from './components/HomePage';
import ProductPage from './components/ProductPage';
import CartPage from './components/CartPage';
import ChatBot from './components/ChatBot';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="header">
          <nav className="nav">
            <h1>🛒 E-Commerce Store</h1>
            <ul className="nav-links">
              <li><Link to="/">Home</Link></li>
              <li><Link to="/cart">Cart</Link></li>
            </ul>
          </nav>
        </header>

        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/product/:id" element={<ProductPage />} />
          <Route path="/cart" element={<CartPage />} />
        </Routes>

        {/* Chatbot Component */}
        <ChatBot />
      </div>
    </Router>
  );
}

export default App;