"""Shopping assistant agent using Strands SDK and Bedrock Nova Pro."""

from typing import Dict, Any, Optional, List
from strands import Agent

from .bedrock_client import BedrockClient
from .session_manager import SessionManager
from .logger import logger

# Import all custom tools
from .tools.product_search import search_products, get_all_products, get_products_by_category
from .tools.product_details import get_product_details, compare_products
from .tools.cart_management import add_to_cart, remove_from_cart, update_cart_quantity, clear_cart
from .tools.cart_summary import get_cart_summary, get_cart_total, count_cart_items


class ShoppingAssistant:
    """Main shopping assistant agent class."""
    
    def __init__(self):
        self.bedrock_client = BedrockClient()
        self.session_manager = SessionManager()
        self.agent = None
        self._initialized = False
        
        # Define the system prompt for the shopping assistant
        self.system_prompt = """You are a friendly and helpful shopping assistant for an e-commerce website. Your role is to help customers find products, manage their shopping cart, and provide excellent customer service.

**Your capabilities:**
- Search for products by name, category, or description
- Provide detailed product information including reviews and ratings
- Help customers add, remove, or update items in their shopping cart
- Compare products to help customers make informed decisions
- Provide shopping recommendations based on customer needs
- Assist with cart management and checkout guidance

**Guidelines:**
- Always be friendly, helpful, and enthusiastic about helping customers
- Use the available tools to provide accurate, up-to-date information
- When customers ask about products, use the search tools to find relevant items
- For cart operations, always confirm actions and provide clear feedback
- If you encounter errors, apologize and suggest alternatives
- Encourage customers to explore products and make purchases
- Use emojis and formatting to make responses engaging and easy to read
- Always provide specific product IDs when mentioning products so customers can easily reference them

**Available tools:**
- Product search and browsing tools
- Product detail and comparison tools  
- Cart management tools (add, remove, update quantities)
- Cart summary and total calculation tools

Remember: You're here to make shopping easy and enjoyable for customers!"""
    
    async def initialize(self) -> bool:
        """Initialize the shopping assistant agent."""
        try:
            logger.info("Initializing shopping assistant agent...")
            
            # Authenticate with Bedrock
            if not self.bedrock_client.authenticate():
                logger.error("Failed to authenticate with Bedrock")
                return False
            
            # Collect all tools
            tools = [
                # Product search tools
                search_products,
                get_all_products,
                get_products_by_category,
                
                # Product details tools
                get_product_details,
                compare_products,
                
                # Cart management tools
                add_to_cart,
                remove_from_cart,
                update_cart_quantity,
                clear_cart,
                
                # Cart summary tools
                get_cart_summary,
                get_cart_total,
                count_cart_items,
            ]
            
            # Create the agent with tools and system prompt
            self.agent = self.bedrock_client.create_agent(
                tools=tools,
                system_prompt=self.system_prompt
            )
            
            self._initialized = True
            logger.info("Shopping assistant agent initialized successfully")
            
            # Log available tools
            tool_names = [tool.__name__ for tool in tools]
            logger.info(f"Agent initialized with {len(tools)} tools: {', '.join(tool_names)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize shopping assistant agent: {e}")
            return False
    
    async def process_message(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a customer message and return a response."""
        if not self._initialized:
            return {
                "response": "Sorry, the shopping assistant is not available right now. Please try again later.",
                "session_id": session_id,
                "error": "Agent not initialized"
            }
        
        try:
            # Get or create session
            if not session_id:
                session_id = self.session_manager.create_session()
            
            session = self.session_manager.get_session(session_id)
            if not session:
                session_id = self.session_manager.create_session()
                session = self.session_manager.get_session(session_id)
            
            logger.info(f"Processing message for session {session_id}: {message[:100]}...")
            
            # Add user message to conversation history
            self.session_manager.add_message(session_id, "user", message)
            
            # Process with the agent
            response = self.agent(message)
            
            # Extract the response text
            response_text = ""
            
            # Handle different response formats from Strands
            if hasattr(response, 'message'):
                message_content = response.message
                if isinstance(message_content, dict) and 'content' in message_content:
                    content = message_content['content']
                    if isinstance(content, list) and len(content) > 0:
                        first_item = content[0]
                        if isinstance(first_item, dict) and 'text' in first_item:
                            response_text = first_item['text']
                        else:
                            response_text = str(first_item)
                    else:
                        response_text = str(content)
                else:
                    response_text = str(message_content)
            elif isinstance(response, dict):
                if 'content' in response:
                    content = response['content']
                    if isinstance(content, list) and len(content) > 0:
                        # Extract text from the first content item
                        first_item = content[0]
                        if isinstance(first_item, dict) and 'text' in first_item:
                            response_text = first_item['text']
                        else:
                            response_text = str(first_item)
                    else:
                        response_text = str(content)
                elif 'message' in response:
                    response_text = str(response['message'])
                else:
                    response_text = str(response)
            elif hasattr(response, 'content'):
                response_text = str(response.content)
            else:
                response_text = str(response)
            
            # Ensure response_text is a clean string
            if not isinstance(response_text, str):
                response_text = str(response_text)
            
            # Add assistant response to conversation history
            self.session_manager.add_message(session_id, "assistant", response_text)
            
            logger.info(f"Generated response for session {session_id}: {str(response_text)[:100]}...")
            
            return {
                "response": response_text,
                "session_id": session_id,
                "suggestions": self._generate_suggestions(message, response_text)
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "I apologize, but I encountered an error while processing your request. Please try again or rephrase your question.",
                "session_id": session_id,
                "error": str(e)
            }
    
    def _generate_suggestions(self, user_message: str, response: str) -> List[str]:
        """Generate helpful suggestions based on the conversation."""
        suggestions = []
        
        user_lower = user_message.lower()
        response_lower = str(response).lower()
        
        # Product search suggestions
        if "search" in user_lower or "find" in user_lower:
            suggestions.extend([
                "Show me all products",
                "What's in the Electronics category?",
                "Compare two products"
            ])
        
        # Cart-related suggestions
        if "cart" in user_lower or "add" in user_lower:
            suggestions.extend([
                "Show my cart summary",
                "What's my cart total?",
                "Continue shopping"
            ])
        
        # Product detail suggestions
        if "product" in response_lower and "id" in response_lower:
            suggestions.extend([
                "Add this to my cart",
                "Tell me more about this product",
                "Show me similar products"
            ])
        
        # General shopping suggestions
        if not suggestions:
            suggestions = [
                "Search for products",
                "Browse categories",
                "Check my cart",
                "Get shopping recommendations"
            ]
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a session."""
        session = self.session_manager.get_session(session_id)
        if not session:
            return None
        
        return {
            "session_id": session_id,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "message_count": len(session.conversation_history),
            "user_preferences": session.user_preferences
        }
    
    def is_initialized(self) -> bool:
        """Check if the agent is properly initialized."""
        return self._initialized
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the shopping assistant."""
        return {
            "initialized": self._initialized,
            "bedrock_authenticated": self.bedrock_client.is_authenticated(),
            "model_info": self.bedrock_client.get_model_info(),
            "active_sessions": self.session_manager.get_active_session_count(),
            "total_sessions": self.session_manager.get_total_session_count()
        }