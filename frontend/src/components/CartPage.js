import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const CartPage = () => {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCartItems();
  }, []);

  const fetchCartItems = async () => {
    try {
      const response = await axios.get('/api/cart');
      setCartItems(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching cart items:', error);
      setLoading(false);
    }
  };

  const updateQuantity = async (itemId, newQuantity) => {
    if (newQuantity < 1) return;
    
    try {
      await axios.put(`/api/cart/${itemId}`, { quantity: newQuantity });
      setCartItems(cartItems.map(item => 
        item.id === itemId ? { ...item, quantity: newQuantity } : item
      ));
    } catch (error) {
      console.error('Error updating quantity:', error);
      alert('Error updating quantity');
    }
  };

  const removeItem = async (itemId) => {
    try {
      await axios.delete(`/api/cart/${itemId}`);
      setCartItems(cartItems.filter(item => item.id !== itemId));
    } catch (error) {
      console.error('Error removing item:', error);
      alert('Error removing item');
    }
  };

  const calculateTotal = () => {
    return cartItems.reduce((total, item) => total + (item.price * item.quantity), 0).toFixed(2);
  };

  if (loading) {
    return <div className="container"><div className="loading">Loading cart...</div></div>;
  }

  if (cartItems.length === 0) {
    return (
      <div className="container">
        <div className="empty-cart">
          <h2>Your cart is empty</h2>
          <p>Add some products to get started!</p>
          <Link to="/" className="btn">Continue Shopping</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <h2 style={{ marginBottom: '2rem', color: '#2c3e50' }}>Shopping Cart</h2>
      
      {cartItems.map(item => (
        <div key={item.id} className="cart-item">
          <div className="cart-item-emoji">{item.emoji}</div>
          <div className="cart-item-details">
            <div className="cart-item-name">{item.name}</div>
            <div className="cart-item-price">${item.price}</div>
            <div className="quantity-controls">
              <button 
                className="quantity-btn"
                onClick={() => updateQuantity(item.id, item.quantity - 1)}
              >
                -
              </button>
              <span className="quantity-display">{item.quantity}</span>
              <button 
                className="quantity-btn"
                onClick={() => updateQuantity(item.id, item.quantity + 1)}
              >
                +
              </button>
            </div>
            <div style={{ color: '#2c3e50', fontWeight: 'bold' }}>
              Subtotal: ${(item.price * item.quantity).toFixed(2)}
            </div>
          </div>
          <button 
            className="btn btn-danger"
            onClick={() => removeItem(item.id)}
          >
            Remove
          </button>
        </div>
      ))}

      <div className="cart-total">
        <div className="total-amount">
          Total: ${calculateTotal()}
        </div>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
          <Link to="/" className="btn">Continue Shopping</Link>
          <button className="btn btn-success">Proceed to Checkout</button>
        </div>
      </div>
    </div>
  );
};

export default CartPage;