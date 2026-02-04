import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const HomePage = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await axios.get('/api/products');
      setProducts(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching products:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="container"><div className="loading">Loading products...</div></div>;
  }

  return (
    <div className="container">
      <h2 style={{ marginBottom: '2rem', color: '#2c3e50' }}>Featured Products</h2>
      <div className="product-grid">
        {products.map(product => (
          <Link key={product.id} to={`/product/${product.id}`} style={{ textDecoration: 'none' }}>
            <div className="product-card">
              <div className="product-emoji">{product.emoji}</div>
              <div className="product-name">{product.name}</div>
              <div className="product-price">${product.price}</div>
              <div className="product-category">{product.category}</div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default HomePage;