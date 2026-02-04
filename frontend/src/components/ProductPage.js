import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

const ProductPage = () => {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [addingToCart, setAddingToCart] = useState(false);

  useEffect(() => {
    fetchProduct();
    fetchReviews();
  }, [id]);

  const fetchProduct = async () => {
    try {
      const response = await axios.get(`/api/products/${id}`);
      setProduct(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching product:', error);
      setLoading(false);
    }
  };

  const fetchReviews = async () => {
    try {
      const response = await axios.get(`/api/products/${id}/reviews`);
      setReviews(response.data);
    } catch (error) {
      console.error('Error fetching reviews:', error);
    }
  };

  const addToCart = async () => {
    setAddingToCart(true);
    try {
      await axios.post('/api/cart', {
        product_id: product.id,
        quantity: quantity
      });
      alert('Product added to cart successfully!');
    } catch (error) {
      console.error('Error adding to cart:', error);
      alert('Error adding product to cart');
    }
    setAddingToCart(false);
  };

  const renderStars = (rating) => {
    return '⭐'.repeat(rating) + '☆'.repeat(5 - rating);
  };

  if (loading) {
    return <div className="container"><div className="loading">Loading product...</div></div>;
  }

  if (!product) {
    return (
      <div className="container">
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <h2>Product not found</h2>
          <Link to="/" className="btn">Back to Home</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <Link to="/" style={{ color: '#3498db', textDecoration: 'none', marginBottom: '1rem', display: 'inline-block' }}>
        ← Back to Products
      </Link>
      
      <div className="product-detail">
        <div className="product-detail-header">
          <div className="product-detail-emoji">{product.emoji}</div>
          <div className="product-detail-info">
            <h1>{product.name}</h1>
            <div className="product-detail-price">${product.price}</div>
            <div className="product-category" style={{ marginBottom: '1rem' }}>{product.category}</div>
            <div className="product-detail-description">{product.description}</div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
              <label htmlFor="quantity">Quantity:</label>
              <select 
                id="quantity"
                value={quantity} 
                onChange={(e) => setQuantity(parseInt(e.target.value))}
                style={{ padding: '0.5rem', borderRadius: '4px', border: '1px solid #ddd' }}
              >
                {[...Array(10)].map((_, i) => (
                  <option key={i + 1} value={i + 1}>{i + 1}</option>
                ))}
              </select>
            </div>
            
            <button 
              className="btn btn-success" 
              onClick={addToCart}
              disabled={addingToCart}
              style={{ fontSize: '1.1rem', padding: '1rem 2rem' }}
            >
              {addingToCart ? 'Adding...' : 'Add to Cart'}
            </button>
          </div>
        </div>
      </div>

      <div className="reviews-section">
        <h3>Customer Reviews</h3>
        {reviews.length === 0 ? (
          <p style={{ color: '#7f8c8d' }}>No reviews yet.</p>
        ) : (
          reviews.map(review => (
            <div key={review.id} className="review">
              <div className="review-header">
                <span className="review-author">{review.user_name}</span>
                <span className="review-rating">{renderStars(review.rating)}</span>
              </div>
              <div className="review-comment">{review.comment}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ProductPage;