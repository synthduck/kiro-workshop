"""Tests for backend API integration client."""

import pytest
import httpx
from unittest.mock import AsyncMock, patch
from chatbot_service.backend_client import BackendClient, BackendAPIError


class TestBackendClient:
    """Test cases for backend API integration."""
    
    @pytest.fixture
    def client(self):
        """Create a backend client for testing."""
        return BackendClient(base_url="http://test-backend:5000")
    
    @pytest.mark.asyncio
    async def test_get_all_products_success(self, client):
        """Test successful product retrieval."""
        mock_products = [
            {"id": 1, "name": "Test Product", "price": 10.99, "category": "Test"},
            {"id": 2, "name": "Another Product", "price": 20.99, "category": "Test"}
        ]
        
        with patch.object(client, '_make_request', return_value=mock_products):
            products = await client.get_all_products()
            
            assert len(products) == 2
            assert products[0]["name"] == "Test Product"
            assert products[1]["price"] == 20.99
    
    @pytest.mark.asyncio
    async def test_get_all_products_failure(self, client):
        """Test product retrieval failure handling."""
        with patch.object(client, '_make_request', side_effect=BackendAPIError("API Error")):
            products = await client.get_all_products()
            
            assert products == []
    
    @pytest.mark.asyncio
    async def test_get_product_by_id_success(self, client):
        """Test successful single product retrieval."""
        mock_product = {"id": 1, "name": "Test Product", "price": 10.99}
        
        with patch.object(client, '_make_request', return_value=mock_product):
            product = await client.get_product_by_id(1)
            
            assert product is not None
            assert product["id"] == 1
            assert product["name"] == "Test Product"
    
    @pytest.mark.asyncio
    async def test_get_product_by_id_not_found(self, client):
        """Test product not found scenario."""
        with patch.object(client, '_make_request', side_effect=BackendAPIError("Not found")):
            product = await client.get_product_by_id(999)
            
            assert product is None
    
    @pytest.mark.asyncio
    async def test_search_products_by_name(self, client):
        """Test product search by name."""
        mock_products = [
            {"id": 1, "name": "Smartphone", "description": "Latest phone", "category": "Electronics"},
            {"id": 2, "name": "Laptop", "description": "Gaming laptop", "category": "Electronics"},
            {"id": 3, "name": "Coffee Mug", "description": "Ceramic mug", "category": "Home"}
        ]
        
        with patch.object(client, 'get_all_products', return_value=mock_products):
            results = await client.search_products("phone")
            
            assert len(results) == 1
            assert results[0]["name"] == "Smartphone"
    
    @pytest.mark.asyncio
    async def test_search_products_by_category(self, client):
        """Test product search by category."""
        mock_products = [
            {"id": 1, "name": "Smartphone", "description": "Latest phone", "category": "Electronics"},
            {"id": 2, "name": "Laptop", "description": "Gaming laptop", "category": "Electronics"},
            {"id": 3, "name": "Coffee Mug", "description": "Ceramic mug", "category": "Home"}
        ]
        
        with patch.object(client, 'get_all_products', return_value=mock_products):
            results = await client.search_products("electronics", category="Electronics")
            
            assert len(results) == 2
            assert all(item["category"] == "Electronics" for item in results)
    
    @pytest.mark.asyncio
    async def test_get_cart_items_success(self, client):
        """Test successful cart retrieval."""
        mock_cart = [
            {"id": 1, "product_id": 1, "quantity": 2, "name": "Test Product", "price": 10.99},
            {"id": 2, "product_id": 2, "quantity": 1, "name": "Another Product", "price": 20.99}
        ]
        
        with patch.object(client, '_make_request', return_value=mock_cart):
            cart_items = await client.get_cart_items()
            
            assert len(cart_items) == 2
            assert cart_items[0]["quantity"] == 2
    
    @pytest.mark.asyncio
    async def test_add_to_cart_success(self, client):
        """Test successful item addition to cart."""
        with patch.object(client, '_make_request', return_value={"message": "Success"}):
            result = await client.add_to_cart(1, 2)
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_add_to_cart_failure(self, client):
        """Test cart addition failure handling."""
        with patch.object(client, '_make_request', side_effect=BackendAPIError("API Error")):
            result = await client.add_to_cart(1, 2)
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_update_cart_item_success(self, client):
        """Test successful cart item update."""
        with patch.object(client, '_make_request', return_value={"message": "Updated"}):
            result = await client.update_cart_item(1, 3)
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_remove_from_cart_success(self, client):
        """Test successful cart item removal."""
        with patch.object(client, '_make_request', return_value={"message": "Removed"}):
            result = await client.remove_from_cart(1)
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_get_cart_summary_with_items(self, client):
        """Test cart summary calculation with items."""
        mock_cart = [
            {"id": 1, "product_id": 1, "quantity": 2, "name": "Test Product", "price": 10.99},
            {"id": 2, "product_id": 2, "quantity": 1, "name": "Another Product", "price": 20.99}
        ]
        
        with patch.object(client, 'get_cart_items', return_value=mock_cart):
            summary = await client.get_cart_summary()
            
            assert summary["total_items"] == 3  # 2 + 1
            assert summary["total_cost"] == 42.97  # (10.99 * 2) + (20.99 * 1)
            assert summary["empty"] is False
            assert len(summary["items"]) == 2
    
    @pytest.mark.asyncio
    async def test_get_cart_summary_empty(self, client):
        """Test cart summary for empty cart."""
        with patch.object(client, 'get_cart_items', return_value=[]):
            summary = await client.get_cart_summary()
            
            assert summary["total_items"] == 0
            assert summary["total_cost"] == 0.0
            assert summary["empty"] is True
            assert summary["items"] == []
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, client):
        """Test successful health check."""
        with patch.object(client, '_make_request', return_value=[]):
            result = await client.health_check()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, client):
        """Test health check failure."""
        with patch.object(client, '_make_request', side_effect=BackendAPIError("Connection failed")):
            result = await client.health_check()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_make_request_timeout_error(self, client):
        """Test timeout error handling."""
        with patch.object(client.client, 'request', side_effect=httpx.TimeoutException("Timeout")):
            with pytest.raises(BackendAPIError, match="Timeout while calling backend API"):
                await client._make_request("GET", "/test")
    
    @pytest.mark.asyncio
    async def test_make_request_connection_error(self, client):
        """Test connection error handling."""
        with patch.object(client.client, 'request', side_effect=httpx.ConnectError("Connection failed")):
            with pytest.raises(BackendAPIError, match="Cannot connect to backend API"):
                await client._make_request("GET", "/test")
    
    @pytest.mark.asyncio
    async def test_make_request_404_error(self, client):
        """Test 404 error handling."""
        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        
        with patch.object(client.client, 'request', return_value=mock_response):
            with pytest.raises(BackendAPIError, match="Resource not found"):
                await client._make_request("GET", "/test")
    
    @pytest.mark.asyncio
    async def test_make_request_server_error(self, client):
        """Test server error handling."""
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        with patch.object(client.client, 'request', return_value=mock_response):
            with pytest.raises(BackendAPIError, match="Backend API error: 500"):
                await client._make_request("GET", "/test")


if __name__ == "__main__":
    # Simple integration test with the actual backend
    import asyncio
    
    async def test_integration():
        """Test integration with actual backend if available."""
        async with BackendClient() as client:
            try:
                # Test health check
                healthy = await client.health_check()
                print(f"Backend health check: {'✓' if healthy else '✗'}")
                
                if healthy:
                    # Test getting products
                    products = await client.get_all_products()
                    print(f"Retrieved {len(products)} products")
                    
                    # Test cart operations
                    cart_summary = await client.get_cart_summary()
                    print(f"Cart summary: {cart_summary['total_items']} items, ${cart_summary['total_cost']}")
                    
            except Exception as e:
                print(f"Integration test failed: {e}")
    
    asyncio.run(test_integration())