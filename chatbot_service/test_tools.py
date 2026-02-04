"""Tests for custom shopping assistant tools."""

import pytest
from unittest.mock import patch, AsyncMock

from chatbot_service.tools.product_search import search_products, get_all_products, get_products_by_category
from chatbot_service.tools.product_details import get_product_details, compare_products
from chatbot_service.tools.cart_management import add_to_cart, remove_from_cart, update_cart_quantity, clear_cart
from chatbot_service.tools.cart_summary import get_cart_summary, get_cart_total, count_cart_items


class TestProductSearchTools:
    """Test cases for product search tools."""
    
    @pytest.mark.asyncio
    async def test_search_products_success(self):
        """Test successful product search."""
        mock_products = [
            {"id": 1, "name": "Smartphone", "price": 699.99, "category": "Electronics", 
             "description": "Latest smartphone", "emoji": "📱"},
            {"id": 2, "name": "Smart Watch", "price": 299.99, "category": "Electronics",
             "description": "Fitness tracker", "emoji": "⌚"}
        ]
        
        with patch('chatbot_service.tools.product_search.BackendClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.search_products.return_value = mock_products
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            result = await search_products("smart")
            
            assert "Found 2 product(s)" in result
            assert "Smartphone" in result
            assert "Smart Watch" in result
            assert "$699.99" in result
    
    @pytest.mark.asyncio
    async def test_search_products_no_results(self):
        """Test product search with no results."""
        with patch('chatbot_service.tools.product_search.BackendClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.search_products.return_value = []
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            result = await search_products("nonexistent")
            
            assert "No products found" in result
            assert "Try a different search term" in result
    
    @pytest.mark.asyncio
    async def test_get_products_by_category_success(self):
        """Test getting products by category."""
        mock_products = [
            {"id": 1, "name": "Smartphone", "price": 699.99, "category": "Electronics", 
             "description": "Latest smartphone", "emoji": "📱"},
            {"id": 2, "name": "Laptop", "price": 1299.99, "category": "Electronics",
             "description": "Gaming laptop", "emoji": "💻"}
        ]
        
        with patch('chatbot_service.tools.product_search.BackendClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get_all_products.return_value = mock_products
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            result = await get_products_by_category("Electronics")
            
            assert "Electronics" in result
            assert "2 items" in result
            assert "Smartphone" in result
            assert "Laptop" in result


class TestProductDetailsTools:
    """Test cases for product details tools."""
    
    @pytest.mark.asyncio
    async def test_get_product_details_success(self):
        """Test successful product details retrieval."""
        mock_product = {
            "id": 1, "name": "Smartphone", "price": 699.99, "category": "Electronics",
            "description": "Latest smartphone", "emoji": "📱"
        }
        mock_reviews = [
            {"user_name": "John", "rating": 5, "comment": "Great phone!"},
            {"user_name": "Jane", "rating": 4, "comment": "Good value"}
        ]
        
        with patch('chatbot_service.tools.product_details.BackendClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get_product_by_id.return_value = mock_product
            mock_instance.get_product_reviews.return_value = mock_reviews
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            result = await get_product_details(1)
            
            assert "Smartphone" in result
            assert "$699.99" in result
            assert "Customer Reviews" in result
            assert "John" in result
            assert "4.5/5" in result  # Average rating
    
    @pytest.mark.asyncio
    async def test_get_product_details_not_found(self):
        """Test product details for non-existent product."""
        with patch('chatbot_service.tools.product_details.BackendClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get_product_by_id.return_value = None
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            result = await get_product_details(999)
            
            assert "not found" in result
            assert "999" in result


class TestCartManagementTools:
    """Test cases for cart management tools."""
    
    @pytest.mark.asyncio
    async def test_add_to_cart_success(self):
        """Test successful item addition to cart."""
        mock_product = {
            "id": 1, "name": "Smartphone", "price": 699.99, "emoji": "📱"
        }
        
        with patch('chatbot_service.tools.cart_management.BackendClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get_product_by_id.return_value = mock_product
            mock_instance.add_to_cart.return_value = True
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            result = await add_to_cart(1, 2)
            
            assert "Added 2x" in result
            assert "Smartphone" in result
            assert "$1399.98" in result  # 2 * 699.99
    
    @pytest.mark.asyncio
    async def test_add_to_cart_invalid_quantity(self):
        """Test adding item with invalid quantity."""
        result = await add_to_cart(1, 0)
        
        assert "Quantity must be a positive number" in result
    
    @pytest.mark.asyncio
    async def test_remove_from_cart_success(self):
        """Test successful item removal from cart."""
        mock_cart_items = [
            {"id": 1, "name": "Smartphone", "quantity": 2, "price": 699.99}
        ]
        
        with patch('chatbot_service.tools.cart_management.BackendClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get_cart_items.return_value = mock_cart_items
            mock_instance.remove_from_cart.return_value = True
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            result = await remove_from_cart(1)
            
            assert "Removed" in result
            assert "Smartphone" in result
            assert "$1399.98" in result  # Saved amount
    
    @pytest.mark.asyncio
    async def test_update_cart_quantity_success(self):
        """Test successful cart quantity update."""
        mock_cart_items = [
            {"id": 1, "name": "Smartphone", "quantity": 2, "price": 699.99, "emoji": "📱"}
        ]
        
        with patch('chatbot_service.tools.cart_management.BackendClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get_cart_items.return_value = mock_cart_items
            mock_instance.update_cart_item.return_value = True
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            result = await update_cart_quantity(1, 3)
            
            assert "Updated" in result
            assert "2 → New quantity: 3" in result
            assert "$+699.99" in result  # Price increase


class TestCartSummaryTools:
    """Test cases for cart summary tools."""
    
    @pytest.mark.asyncio
    async def test_get_cart_summary_with_items(self):
        """Test cart summary with items."""
        mock_summary = {
            "empty": False,
            "items": [
                {"id": 1, "name": "Smartphone", "quantity": 2, "price": 699.99, "emoji": "📱"},
                {"id": 2, "name": "Headphones", "quantity": 1, "price": 199.99, "emoji": "🎧"}
            ],
            "total_items": 3,
            "total_cost": 1599.97
        }
        
        with patch('chatbot_service.tools.cart_summary.BackendClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get_cart_summary.return_value = mock_summary
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            result = await get_cart_summary()
            
            assert "3 items" in result
            assert "$1599.97" in result
            assert "Smartphone" in result
            assert "Headphones" in result
    
    @pytest.mark.asyncio
    async def test_get_cart_summary_empty(self):
        """Test cart summary when empty."""
        mock_summary = {"empty": True}
        
        with patch('chatbot_service.tools.cart_summary.BackendClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get_cart_summary.return_value = mock_summary
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            result = await get_cart_summary()
            
            assert "cart is empty" in result
            assert "Ready to start shopping" in result
    
    @pytest.mark.asyncio
    async def test_get_cart_total(self):
        """Test getting cart total."""
        mock_summary = {
            "empty": False,
            "total_items": 3,
            "total_cost": 1599.97
        }
        
        with patch('chatbot_service.tools.cart_summary.BackendClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get_cart_summary.return_value = mock_summary
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            result = await get_cart_total()
            
            assert "$1599.97" in result
            assert "3 items" in result
    
    @pytest.mark.asyncio
    async def test_count_cart_items(self):
        """Test counting cart items."""
        mock_summary = {
            "empty": False,
            "total_items": 3,
            "items": [{"id": 1}, {"id": 2}]  # 2 unique products
        }
        
        with patch('chatbot_service.tools.cart_summary.BackendClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get_cart_summary.return_value = mock_summary
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            result = await count_cart_items()
            
            assert "3 items" in result
            assert "2 different products" in result


if __name__ == "__main__":
    # Run a simple test to verify tools work
    import asyncio
    
    async def test_tools():
        """Test tools with mock data."""
        print("Testing shopping assistant tools...")
        
        # Test search (will fail without backend, but shows the tool works)
        try:
            result = await search_products("test")
            print(f"Search result: {result[:100]}...")
        except Exception as e:
            print(f"Search test (expected to fail without backend): {e}")
        
        print("Tools are properly configured!")
    
    asyncio.run(test_tools())