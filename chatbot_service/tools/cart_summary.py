"""Cart summary tool for the shopping assistant."""

from strands import tool

from ..backend_client import BackendClient
from ..logger import logger


@tool
async def get_cart_summary() -> str:
    """
    Get a summary of the current shopping cart including all items and total cost.
    
    Returns:
        str: Detailed cart summary with items, quantities, and total cost
    """
    try:
        async with BackendClient() as client:
            cart_summary = await client.get_cart_summary()
            
            if cart_summary.get('empty', True):
                return "🛒 **Your cart is empty!**\n\nReady to start shopping? I can help you find products or browse categories. What are you looking for today?"
            
            items = cart_summary['items']
            total_items = cart_summary['total_items']
            total_cost = cart_summary['total_cost']
            
            result = f"🛒 **Your Shopping Cart** ({total_items} items)\n\n"
            
            # List all items
            for item in items:
                item_total = item['price'] * item['quantity']
                result += f"{item['emoji']} **{item['name']}**\n"
                result += f"   💰 ${item['price']:.2f} each × {item['quantity']} = ${item_total:.2f}\n"
                result += f"   🆔 Cart Item ID: {item['id']}\n\n"
            
            # Add totals
            result += "─" * 40 + "\n"
            result += f"📦 **Total Items:** {total_items}\n"
            result += f"💵 **Total Cost:** ${total_cost:.2f}\n\n"
            
            # Add helpful actions
            result += "**What would you like to do?**\n"
            result += "• Continue shopping for more items\n"
            result += "• Update quantities (just tell me the cart item ID and new quantity)\n"
            result += "• Remove items (just tell me the cart item ID to remove)\n"
            result += "• Proceed to checkout\n"
            result += "• Clear the entire cart\n\n"
            
            result += "Just let me know how I can help with your cart!"
            
            return result
            
    except Exception as e:
        logger.error(f"Error getting cart summary: {e}")
        return "Sorry, I encountered an error while retrieving your cart. Please try again later."


@tool
async def get_cart_total() -> str:
    """
    Get just the total cost of items in the cart.
    
    Returns:
        str: Simple message with the cart total
    """
    try:
        async with BackendClient() as client:
            cart_summary = await client.get_cart_summary()
            
            if cart_summary.get('empty', True):
                return "Your cart is empty, so the total is $0.00."
            
            total_items = cart_summary['total_items']
            total_cost = cart_summary['total_cost']
            
            return f"💵 Your cart total is **${total_cost:.2f}** for {total_items} items."
            
    except Exception as e:
        logger.error(f"Error getting cart total: {e}")
        return "Sorry, I encountered an error while calculating your cart total. Please try again later."


@tool
async def count_cart_items() -> str:
    """
    Get the number of items currently in the cart.
    
    Returns:
        str: Message with the count of items in cart
    """
    try:
        async with BackendClient() as client:
            cart_summary = await client.get_cart_summary()
            
            if cart_summary.get('empty', True):
                return "Your cart is currently empty (0 items)."
            
            total_items = cart_summary['total_items']
            unique_products = len(cart_summary['items'])
            
            if unique_products == 1:
                return f"📦 You have {total_items} items of 1 product in your cart."
            else:
                return f"📦 You have {total_items} items across {unique_products} different products in your cart."
            
    except Exception as e:
        logger.error(f"Error counting cart items: {e}")
        return "Sorry, I encountered an error while counting your cart items. Please try again later."