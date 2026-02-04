"""Cart management tools for the shopping assistant."""

from strands import tool

from ..backend_client import BackendClient
from ..logger import logger


@tool
async def add_to_cart(product_id: int, quantity: int = 1) -> str:
    """
    Add a product to the shopping cart.
    
    Args:
        product_id (int): The ID of the product to add to cart
        quantity (int): Number of items to add (default: 1)
    
    Returns:
        str: Confirmation message about the cart addition
    """
    try:
        if quantity <= 0:
            return "Quantity must be a positive number. Please specify how many items you'd like to add."
        
        async with BackendClient() as client:
            # First, verify the product exists
            product = await client.get_product_by_id(product_id)
            if not product:
                return f"Product with ID {product_id} not found. Please check the product ID and try again."
            
            # Add to cart
            success = await client.add_to_cart(product_id, quantity)
            
            if success:
                total_cost = product['price'] * quantity
                result = f"✅ Added {quantity}x **{product['name']}** to your cart!\n\n"
                result += f"{product['emoji']} {product['name']}\n"
                result += f"💰 ${product['price']:.2f} each\n"
                result += f"📦 Quantity: {quantity}\n"
                result += f"💵 Total: ${total_cost:.2f}\n\n"
                result += "Would you like to continue shopping or view your cart?"
                return result
            else:
                return f"Sorry, I couldn't add {product['name']} to your cart. Please try again later."
                
    except Exception as e:
        logger.error(f"Error adding product {product_id} to cart: {e}")
        return "Sorry, I encountered an error while adding the item to your cart. Please try again later."


@tool
async def remove_from_cart(cart_item_id: int) -> str:
    """
    Remove an item from the shopping cart.
    
    Args:
        cart_item_id (int): The ID of the cart item to remove
    
    Returns:
        str: Confirmation message about the cart removal
    """
    try:
        async with BackendClient() as client:
            # Get current cart to find the item
            cart_items = await client.get_cart_items()
            
            # Find the item to remove
            item_to_remove = None
            for item in cart_items:
                if item['id'] == cart_item_id:
                    item_to_remove = item
                    break
            
            if not item_to_remove:
                return f"Cart item with ID {cart_item_id} not found. Please check your cart and try again."
            
            # Remove from cart
            success = await client.remove_from_cart(cart_item_id)
            
            if success:
                result = f"🗑️ Removed **{item_to_remove['name']}** from your cart.\n\n"
                result += f"Removed: {item_to_remove['quantity']}x {item_to_remove['name']}\n"
                result += f"Saved: ${item_to_remove['price'] * item_to_remove['quantity']:.2f}\n\n"
                result += "Would you like to continue shopping or view your updated cart?"
                return result
            else:
                return f"Sorry, I couldn't remove {item_to_remove['name']} from your cart. Please try again later."
                
    except Exception as e:
        logger.error(f"Error removing cart item {cart_item_id}: {e}")
        return "Sorry, I encountered an error while removing the item from your cart. Please try again later."


@tool
async def update_cart_quantity(cart_item_id: int, new_quantity: int) -> str:
    """
    Update the quantity of an item in the shopping cart.
    
    Args:
        cart_item_id (int): The ID of the cart item to update
        new_quantity (int): The new quantity for the item
    
    Returns:
        str: Confirmation message about the quantity update
    """
    try:
        if new_quantity <= 0:
            return "Quantity must be a positive number. To remove an item completely, use the remove_from_cart tool."
        
        async with BackendClient() as client:
            # Get current cart to find the item
            cart_items = await client.get_cart_items()
            
            # Find the item to update
            item_to_update = None
            for item in cart_items:
                if item['id'] == cart_item_id:
                    item_to_update = item
                    break
            
            if not item_to_update:
                return f"Cart item with ID {cart_item_id} not found. Please check your cart and try again."
            
            old_quantity = item_to_update['quantity']
            
            # Update quantity
            success = await client.update_cart_item(cart_item_id, new_quantity)
            
            if success:
                old_total = item_to_update['price'] * old_quantity
                new_total = item_to_update['price'] * new_quantity
                difference = new_total - old_total
                
                result = f"📦 Updated **{item_to_update['name']}** quantity in your cart.\n\n"
                result += f"{item_to_update['emoji']} {item_to_update['name']}\n"
                result += f"Old quantity: {old_quantity} → New quantity: {new_quantity}\n"
                result += f"Price change: ${difference:+.2f}\n"
                result += f"New item total: ${new_total:.2f}\n\n"
                
                if new_quantity > old_quantity:
                    result += "Great choice! Added more items to your cart."
                else:
                    result += "Updated! Reduced the quantity in your cart."
                
                return result
            else:
                return f"Sorry, I couldn't update the quantity for {item_to_update['name']}. Please try again later."
                
    except Exception as e:
        logger.error(f"Error updating cart item {cart_item_id} quantity: {e}")
        return "Sorry, I encountered an error while updating the item quantity. Please try again later."


@tool
async def clear_cart() -> str:
    """
    Remove all items from the shopping cart.
    
    Returns:
        str: Confirmation message about clearing the cart
    """
    try:
        async with BackendClient() as client:
            # Get current cart items
            cart_items = await client.get_cart_items()
            
            if not cart_items:
                return "Your cart is already empty! Ready to start shopping?"
            
            # Remove all items
            removed_count = 0
            total_saved = 0.0
            
            for item in cart_items:
                success = await client.remove_from_cart(item['id'])
                if success:
                    removed_count += 1
                    total_saved += item['price'] * item['quantity']
            
            if removed_count == len(cart_items):
                result = f"🗑️ **Cart cleared!** Removed all {removed_count} items.\n\n"
                result += f"Items removed: {removed_count}\n"
                result += f"Total value cleared: ${total_saved:.2f}\n\n"
                result += "Your cart is now empty and ready for new items. What would you like to shop for?"
                return result
            elif removed_count > 0:
                result = f"⚠️ **Partially cleared:** Removed {removed_count} out of {len(cart_items)} items.\n\n"
                result += f"Some items couldn't be removed. Please try again or contact support."
                return result
            else:
                return "Sorry, I couldn't clear your cart. Please try again later."
                
    except Exception as e:
        logger.error(f"Error clearing cart: {e}")
        return "Sorry, I encountered an error while clearing your cart. Please try again later."