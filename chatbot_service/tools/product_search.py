"""Product search tool for the shopping assistant."""

from typing import List, Dict, Any
from strands import tool

from ..backend_client import BackendClient
from ..logger import logger


@tool
async def search_products(query: str, category: str = None) -> str:
    """
    Search for products by name, description, or category.
    
    Args:
        query (str): Search term to find products (e.g., "smartphone", "laptop", "coffee")
        category (str, optional): Specific category to filter by (e.g., "Electronics", "Home", "Clothing")
    
    Returns:
        str: Formatted list of matching products with details
    """
    try:
        async with BackendClient() as client:
            products = await client.search_products(query, category)
            
            if not products:
                if category:
                    return f"No products found matching '{query}' in category '{category}'. Try a different search term or browse other categories."
                else:
                    return f"No products found matching '{query}'. Try a different search term or check the spelling."
            
            # Format products for display
            result = f"Found {len(products)} product(s) matching '{query}':\n\n"
            
            for product in products[:10]:  # Limit to top 10 results
                result += f"{product['emoji']} **{product['name']}** - ${product['price']:.2f}\n"
                result += f"   Category: {product['category']}\n"
                result += f"   Description: {product['description']}\n"
                result += f"   Product ID: {product['id']}\n\n"
            
            if len(products) > 10:
                result += f"... and {len(products) - 10} more products. Try a more specific search to narrow results.\n"
            
            return result
            
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        return f"Sorry, I encountered an error while searching for products. Please try again later."


@tool
async def get_all_products() -> str:
    """
    Get all available products in the store.
    
    Returns:
        str: Formatted list of all products organized by category
    """
    try:
        async with BackendClient() as client:
            products = await client.get_all_products()
            
            if not products:
                return "No products are currently available in the store."
            
            # Organize products by category
            categories = {}
            for product in products:
                category = product.get('category', 'Other')
                if category not in categories:
                    categories[category] = []
                categories[category].append(product)
            
            # Format by category
            result = f"Here are all {len(products)} products in our store:\n\n"
            
            for category, category_products in categories.items():
                result += f"**{category}** ({len(category_products)} items):\n"
                for product in category_products:
                    result += f"  {product['emoji']} {product['name']} - ${product['price']:.2f}\n"
                result += "\n"
            
            result += "Use the product search tool or ask for specific product details to learn more!"
            return result
            
    except Exception as e:
        logger.error(f"Error getting all products: {e}")
        return "Sorry, I encountered an error while retrieving products. Please try again later."


@tool
async def get_products_by_category(category: str) -> str:
    """
    Get all products in a specific category.
    
    Args:
        category (str): Category name (e.g., "Electronics", "Clothing", "Home", "Books")
    
    Returns:
        str: Formatted list of products in the specified category
    """
    try:
        async with BackendClient() as client:
            all_products = await client.get_all_products()
            
            if not all_products:
                return "No products are currently available in the store."
            
            # Filter by category (case-insensitive)
            category_products = [
                p for p in all_products 
                if p.get('category', '').lower() == category.lower()
            ]
            
            if not category_products:
                available_categories = list(set(p.get('category', 'Other') for p in all_products))
                return f"No products found in category '{category}'. Available categories: {', '.join(available_categories)}"
            
            result = f"Products in **{category}** category ({len(category_products)} items):\n\n"
            
            for product in category_products:
                result += f"{product['emoji']} **{product['name']}** - ${product['price']:.2f}\n"
                result += f"   {product['description']}\n"
                result += f"   Product ID: {product['id']}\n\n"
            
            return result
            
    except Exception as e:
        logger.error(f"Error getting products by category: {e}")
        return f"Sorry, I encountered an error while retrieving {category} products. Please try again later."