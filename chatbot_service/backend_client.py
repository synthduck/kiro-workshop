"""HTTP client for integrating with the existing backend API."""

import asyncio
from typing import List, Dict, Any, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import Config
from .logger import logger


class BackendAPIError(Exception):
    """Custom exception for backend API errors."""
    pass


class BackendClient:
    """HTTP client for the existing e-commerce backend API."""
    
    def __init__(self, base_url: str = None, timeout: float = 30.0):
        self.base_url = base_url or Config.BACKEND_API_URL
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"Content-Type": "application/json"}
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with retry logic and error handling."""
        try:
            logger.debug(f"Making {method} request to {endpoint}")
            response = await self.client.request(method, endpoint, **kwargs)
            
            if response.status_code == 404:
                logger.warning(f"Resource not found: {endpoint}")
                raise BackendAPIError(f"Resource not found: {endpoint}")
            
            if response.status_code >= 400:
                logger.error(f"Backend API error {response.status_code}: {response.text}")
                raise BackendAPIError(f"Backend API error: {response.status_code}")
            
            return response.json()
            
        except httpx.TimeoutException:
            logger.error(f"Timeout while calling {endpoint}")
            raise BackendAPIError(f"Timeout while calling backend API: {endpoint}")
        except httpx.ConnectError:
            logger.error(f"Connection error while calling {endpoint}")
            raise BackendAPIError(f"Cannot connect to backend API: {endpoint}")
        except Exception as e:
            logger.error(f"Unexpected error calling {endpoint}: {e}")
            raise BackendAPIError(f"Unexpected error: {e}")
    
    async def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products from the backend API."""
        try:
            products = await self._make_request("GET", "/api/products")
            logger.info(f"Retrieved {len(products)} products")
            return products
        except BackendAPIError:
            logger.error("Failed to retrieve products")
            return []
    
    async def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific product by ID."""
        try:
            product = await self._make_request("GET", f"/api/products/{product_id}")
            logger.info(f"Retrieved product {product_id}: {product.get('name', 'Unknown')}")
            return product
        except BackendAPIError:
            logger.warning(f"Product {product_id} not found")
            return None
    
    async def get_product_reviews(self, product_id: int) -> List[Dict[str, Any]]:
        """Get reviews for a specific product."""
        try:
            reviews = await self._make_request("GET", f"/api/products/{product_id}/reviews")
            logger.info(f"Retrieved {len(reviews)} reviews for product {product_id}")
            return reviews
        except BackendAPIError:
            logger.warning(f"Failed to get reviews for product {product_id}")
            return []
    
    async def search_products(self, query: str, category: str = None) -> List[Dict[str, Any]]:
        """Search products by name, description, or category."""
        try:
            all_products = await self.get_all_products()
            
            if not all_products:
                return []
            
            query_lower = query.lower()
            filtered_products = []
            
            for product in all_products:
                # Check if query matches name, description, or category
                name_match = query_lower in product.get('name', '').lower()
                desc_match = query_lower in product.get('description', '').lower()
                category_match = query_lower in product.get('category', '').lower()
                
                # If specific category is requested, filter by it
                if category:
                    category_filter = category.lower() == product.get('category', '').lower()
                    if not category_filter:
                        continue
                
                if name_match or desc_match or category_match:
                    filtered_products.append(product)
            
            logger.info(f"Found {len(filtered_products)} products matching '{query}'")
            return filtered_products
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    async def get_cart_items(self) -> List[Dict[str, Any]]:
        """Get all items in the shopping cart."""
        try:
            cart_items = await self._make_request("GET", "/api/cart")
            logger.info(f"Retrieved {len(cart_items)} cart items")
            return cart_items
        except BackendAPIError:
            logger.error("Failed to retrieve cart items")
            return []
    
    async def add_to_cart(self, product_id: int, quantity: int = 1) -> bool:
        """Add an item to the shopping cart."""
        try:
            data = {"product_id": product_id, "quantity": quantity}
            result = await self._make_request("POST", "/api/cart", json=data)
            logger.info(f"Added product {product_id} (qty: {quantity}) to cart")
            return True
        except BackendAPIError:
            logger.error(f"Failed to add product {product_id} to cart")
            return False
    
    async def update_cart_item(self, cart_item_id: int, quantity: int) -> bool:
        """Update the quantity of a cart item."""
        try:
            data = {"quantity": quantity}
            result = await self._make_request("PUT", f"/api/cart/{cart_item_id}", json=data)
            logger.info(f"Updated cart item {cart_item_id} to quantity {quantity}")
            return True
        except BackendAPIError:
            logger.error(f"Failed to update cart item {cart_item_id}")
            return False
    
    async def remove_from_cart(self, cart_item_id: int) -> bool:
        """Remove an item from the shopping cart."""
        try:
            result = await self._make_request("DELETE", f"/api/cart/{cart_item_id}")
            logger.info(f"Removed cart item {cart_item_id}")
            return True
        except BackendAPIError:
            logger.error(f"Failed to remove cart item {cart_item_id}")
            return False
    
    async def get_cart_summary(self) -> Dict[str, Any]:
        """Get a summary of the shopping cart including total cost."""
        try:
            cart_items = await self.get_cart_items()
            
            if not cart_items:
                return {
                    "items": [],
                    "total_items": 0,
                    "total_cost": 0.0,
                    "empty": True
                }
            
            total_cost = sum(item['price'] * item['quantity'] for item in cart_items)
            total_items = sum(item['quantity'] for item in cart_items)
            
            summary = {
                "items": cart_items,
                "total_items": total_items,
                "total_cost": round(total_cost, 2),
                "empty": False
            }
            
            logger.info(f"Cart summary: {total_items} items, ${total_cost:.2f}")
            return summary
            
        except Exception as e:
            logger.error(f"Error getting cart summary: {e}")
            return {
                "items": [],
                "total_items": 0,
                "total_cost": 0.0,
                "empty": True,
                "error": str(e)
            }
    
    async def health_check(self) -> bool:
        """Check if the backend API is healthy and accessible."""
        try:
            # Try to get products as a health check
            await self._make_request("GET", "/api/products")
            logger.info("Backend API health check passed")
            return True
        except Exception as e:
            logger.error(f"Backend API health check failed: {e}")
            return False