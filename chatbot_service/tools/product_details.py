"""Product details tool for the shopping assistant."""

from typing import Dict, Any
from strands import tool

from ..backend_client import BackendClient
from ..logger import logger


@tool
async def get_product_details(product_id: int) -> str:
    """
    Get detailed information about a specific product including reviews.
    
    Args:
        product_id (int): The unique ID of the product to get details for
    
    Returns:
        str: Detailed product information including reviews and ratings
    """
    try:
        async with BackendClient() as client:
            # Get product details
            product = await client.get_product_by_id(product_id)
            
            if not product:
                return f"Product with ID {product_id} not found. Please check the product ID and try again."
            
            # Get product reviews
            reviews = await client.get_product_reviews(product_id)
            
            # Format product details
            result = f"{product['emoji']} **{product['name']}**\n\n"
            result += f"💰 **Price:** ${product['price']:.2f}\n"
            result += f"📂 **Category:** {product['category']}\n"
            result += f"📝 **Description:** {product['description']}\n"
            result += f"🆔 **Product ID:** {product['id']}\n\n"
            
            # Add reviews section
            if reviews:
                # Calculate average rating
                total_rating = sum(review['rating'] for review in reviews)
                avg_rating = total_rating / len(reviews)
                
                result += f"⭐ **Customer Reviews** (Average: {avg_rating:.1f}/5 stars, {len(reviews)} reviews):\n\n"
                
                for review in reviews:
                    stars = "⭐" * review['rating'] + "☆" * (5 - review['rating'])
                    result += f"**{review['user_name']}** {stars}\n"
                    result += f"   \"{review['comment']}\"\n\n"
            else:
                result += "📝 **Customer Reviews:** No reviews yet. Be the first to review this product!\n\n"
            
            result += f"To add this item to your cart, just ask me to add product {product_id} to your cart!"
            
            return result
            
    except Exception as e:
        logger.error(f"Error getting product details for ID {product_id}: {e}")
        return f"Sorry, I encountered an error while retrieving details for product {product_id}. Please try again later."


@tool
async def compare_products(product_id1: int, product_id2: int) -> str:
    """
    Compare two products side by side.
    
    Args:
        product_id1 (int): ID of the first product to compare
        product_id2 (int): ID of the second product to compare
    
    Returns:
        str: Side-by-side comparison of the two products
    """
    try:
        async with BackendClient() as client:
            # Get both products
            product1 = await client.get_product_by_id(product_id1)
            product2 = await client.get_product_by_id(product_id2)
            
            if not product1:
                return f"Product with ID {product_id1} not found."
            if not product2:
                return f"Product with ID {product_id2} not found."
            
            # Get reviews for both products
            reviews1 = await client.get_product_reviews(product_id1)
            reviews2 = await client.get_product_reviews(product_id2)
            
            # Calculate average ratings
            avg_rating1 = sum(r['rating'] for r in reviews1) / len(reviews1) if reviews1 else 0
            avg_rating2 = sum(r['rating'] for r in reviews2) / len(reviews2) if reviews2 else 0
            
            # Format comparison
            result = "🔍 **Product Comparison**\n\n"
            
            result += f"**{product1['emoji']} {product1['name']}** vs **{product2['emoji']} {product2['name']}**\n\n"
            
            result += "| Feature | Product 1 | Product 2 |\n"
            result += "|---------|-----------|----------|\n"
            result += f"| **Price** | ${product1['price']:.2f} | ${product2['price']:.2f} |\n"
            result += f"| **Category** | {product1['category']} | {product2['category']} |\n"
            result += f"| **Rating** | {avg_rating1:.1f}/5 ({len(reviews1)} reviews) | {avg_rating2:.1f}/5 ({len(reviews2)} reviews) |\n\n"
            
            result += f"**{product1['name']} Description:**\n{product1['description']}\n\n"
            result += f"**{product2['name']} Description:**\n{product2['description']}\n\n"
            
            # Price comparison
            if product1['price'] < product2['price']:
                savings = product2['price'] - product1['price']
                result += f"💰 **Price Advantage:** {product1['name']} is ${savings:.2f} cheaper!\n\n"
            elif product2['price'] < product1['price']:
                savings = product1['price'] - product2['price']
                result += f"💰 **Price Advantage:** {product2['name']} is ${savings:.2f} cheaper!\n\n"
            else:
                result += f"💰 **Price:** Both products have the same price.\n\n"
            
            # Rating comparison
            if avg_rating1 > avg_rating2 and reviews1:
                result += f"⭐ **Rating Advantage:** {product1['name']} has a higher customer rating!\n\n"
            elif avg_rating2 > avg_rating1 and reviews2:
                result += f"⭐ **Rating Advantage:** {product2['name']} has a higher customer rating!\n\n"
            
            result += "Would you like to add either of these products to your cart?"
            
            return result
            
    except Exception as e:
        logger.error(f"Error comparing products {product_id1} and {product_id2}: {e}")
        return f"Sorry, I encountered an error while comparing the products. Please try again later."