# Shopping Assistant Chatbot Service

An AI-powered shopping assistant built with Strands Agents SDK and AWS Bedrock Nova Pro. This service provides intelligent shopping guidance, product recommendations, and cart management through a conversational interface.

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- AWS credentials with Bedrock access
- Access to the e-commerce backend API (optional for basic functionality)

### 1. Environment Setup

```bash
# Clone and navigate to the chatbot service
cd chatbot_service

# Copy environment configuration
cp .env.example .env

# Edit .env with your AWS credentials
nano .env
```

### 2. AWS Configuration

Choose one of these authentication methods:

**Option 1: Bedrock API Key (Recommended for Development)**
```bash
export AWS_BEARER_TOKEN_BEDROCK=your_bedrock_api_key
export AWS_REGION=us-west-2
```

**Option 2: AWS Credentials**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-west-2
```

### 3. Start the Service

```bash
# Using the start script (recommended)
./scripts/start.sh

# Or manually
python run.py
```

The service will start on port 8000 by default.

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_BEARER_TOKEN_BEDROCK` | Bedrock API key | None |
| `AWS_ACCESS_KEY_ID` | AWS access key | None |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | None |
| `AWS_SESSION_TOKEN` | AWS session token (optional) | None |
| `AWS_REGION` | AWS region | us-west-2 |
| `BACKEND_API_URL` | E-commerce backend URL | http://localhost:5000 |
| `CHATBOT_PORT` | Service port | 8000 |
| `LOG_LEVEL` | Logging level | INFO |
| `BEDROCK_MODEL_ID` | Bedrock model ID | us.amazon.nova-pro-v1:0 |

### Model Configuration

The service uses AWS Bedrock Nova Pro by default. You can configure different models by setting the `BEDROCK_MODEL_ID` environment variable:

- `us.amazon.nova-pro-v1:0` (default)
- `us.amazon.nova-premier-v1:0`
- `anthropic.claude-sonnet-4-20250514-v1:0`

## 📡 API Endpoints

### Chat Endpoint
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Show me electronics products",
  "session_id": "optional-session-id"
}
```

### Health Check
```http
GET /api/health
```

### Session Management
```http
GET /api/sessions/{session_id}
DELETE /api/sessions/{session_id}
POST /api/sessions/cleanup
```

### Service Status
```http
GET /api/status
```

## 🤖 Chatbot Capabilities

The shopping assistant can help with:

- **Product Search**: Find products by name, category, or description
- **Product Details**: Get detailed information including reviews and ratings
- **Product Comparison**: Compare multiple products side-by-side
- **Cart Management**: Add, remove, and update items in the shopping cart
- **Cart Summary**: View cart contents and calculate totals
- **Shopping Guidance**: Provide personalized recommendations

### Example Interactions

```
User: "Show me smartphones under $700"
Assistant: Found 2 products matching your criteria...

User: "Add the iPhone to my cart"
Assistant: ✅ Added 1x iPhone to your cart! Total: $699.99

User: "What's in my cart?"
Assistant: 🛒 Your Shopping Cart (1 item)...
```

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Start with Docker Compose
cd docker
docker-compose up -d

# View logs
docker-compose logs -f chatbot

# Stop
docker-compose down
```

### Manual Docker Build

```bash
# Build image
docker build -f docker/Dockerfile -t shopping-chatbot .

# Run container
docker run -d \
  --name shopping-chatbot \
  -p 8000:8000 \
  -e AWS_BEARER_TOKEN_BEDROCK=your_key \
  -e AWS_REGION=us-west-2 \
  shopping-chatbot
```

## 🔍 Monitoring and Health Checks

### Health Check Endpoint

The service provides a comprehensive health check at `/api/health`:

```json
{
  "status": "healthy",
  "service": "shopping-assistant-chatbot",
  "timestamp": "2024-01-01T00:00:00",
  "details": {
    "initialized": true,
    "bedrock_authenticated": true,
    "backend_api_healthy": true,
    "active_sessions": 5,
    "total_sessions": 23
  }
}
```

### Logging

The service provides structured logging with different levels:

- `DEBUG`: Detailed debugging information
- `INFO`: General operational messages
- `WARNING`: Warning messages for non-critical issues
- `ERROR`: Error messages for failures

## 🛠️ Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run specific test file
pytest test_agent.py -v

# Run with coverage
pytest --cov=chatbot_service
```

### Project Structure

```
chatbot_service/
├── __init__.py              # Package initialization
├── app.py                   # FastAPI application
├── agent.py                 # Main shopping assistant agent
├── bedrock_client.py        # AWS Bedrock integration
├── backend_client.py        # E-commerce backend client
├── config.py                # Configuration management
├── error_handler.py         # Error handling utilities
├── logger.py                # Logging configuration
├── models.py                # Pydantic data models
├── session_manager.py       # Session management
├── run.py                   # Standalone runner
├── tools/                   # Custom agent tools
│   ├── product_search.py    # Product search tools
│   ├── product_details.py   # Product detail tools
│   ├── cart_management.py   # Cart management tools
│   └── cart_summary.py      # Cart summary tools
├── scripts/                 # Utility scripts
│   ├── start.sh            # Start script
│   └── stop.sh             # Stop script
├── docker/                  # Docker configuration
│   ├── Dockerfile          # Docker image definition
│   └── docker-compose.yml  # Docker Compose configuration
└── test_*.py               # Test files
```

## 🔒 Security Considerations

- **Credentials**: Never commit AWS credentials to version control
- **Environment Variables**: Use `.env` files for local development
- **Network**: The service runs on all interfaces (0.0.0.0) by default
- **CORS**: Configured for localhost origins, update for production
- **Logging**: Sensitive information is not logged

## 🚨 Troubleshooting

### Common Issues

**Authentication Errors**
```
ERROR: No AWS credentials configured
```
- Ensure AWS credentials are properly set in environment variables
- Check that Bedrock model access is enabled in AWS console

**Backend Connection Issues**
```
ERROR: Cannot connect to backend API
```
- Verify the backend service is running
- Check the `BACKEND_API_URL` configuration
- Ensure network connectivity between services

**Model Access Denied**
```
ERROR: Access denied to model
```
- Enable model access in AWS Bedrock console
- Verify IAM permissions for Bedrock service
- Check the model ID is correct for your region

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
export LOG_LEVEL=DEBUG
python run.py
```

## 📝 License

This project is part of the e-commerce application suite. See the main project for license information.

## 🤝 Contributing

1. Follow the existing code style and patterns
2. Add tests for new functionality
3. Update documentation for API changes
4. Ensure all tests pass before submitting changes

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs for error details
3. Ensure all prerequisites are met
4. Verify AWS credentials and permissions