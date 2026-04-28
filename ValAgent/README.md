# ValAgent: AI-Powered Course Enrollment Orchestrator

## Overview

ValAgent is a sophisticated AI-driven orchestrator designed for an educational course enrollment platform. It leverages natural language processing, large language models, and microservices architecture to provide a seamless, conversational experience for users managing course registrations, payments, and enrollments.

The system consists of multiple specialized microservices coordinated by a central orchestrator that understands user intent and executes complex workflows through tool calling.

## Architecture

ValAgent follows a microservices architecture with the following components:

### Core Services

1. **Orchestrator** (`/orchestrator`)
   - Main AI agent that processes user queries
   - Uses intent classification and LLM planning for multi-step workflows
   - Coordinates tool execution across all services

2. **Authentication** (`/authentication`)
   - User registration and login
   - JWT token management and validation

3. **Courses** (`/courses`)
   - Course catalog management
   - Search and filtering capabilities

4. **Discounts** (`/discounts`)
   - Discount code management
   - Application logic for pricing

5. **Payments** (`/payments`)
   - Payment intent creation
   - Integration with payment providers

6. **Enrollments** (`/enrollments`)
   - Course enrollment management
   - User enrollment tracking

7. **RAG (Retrieval-Augmented Generation)** (`/RAG`)
   - AI-powered search and Q&A for course information
   - Vector-based knowledge retrieval

8. **Intent Classification** (`/intent`)
   - Natural language intent detection
   - Tool recommendation based on user queries

### Supporting Components

- **ChatBot**: Conversational interface
- **MCP (Model Context Protocol)**: Standardized tool calling interface
- **Database**: MySQL with SQLAlchemy ORM
- **Vector Store**: ChromaDB for embeddings
- **LLM**: Groq API for planning and generation

## Key Features

### AI-Powered Orchestration
- **Intent Classification**: Automatically understands user requests from natural language
- **Multi-Step Planning**: Uses LLM to plan complex sequences of actions
- **Context Management**: Maintains conversation context across interactions
- **Tool Calling**: Executes operations across microservices via MCP

### User Management
- **Secure Authentication**: JWT-based auth with password hashing
- **User Profiles**: Registration with email validation
- **Session Management**: Bearer token validation for protected operations

### Course Management
- **Rich Course Catalog**: Detailed course information with pricing
- **Search & Filtering**: Full-text search across course titles and descriptions
- **Active/Inactive Status**: Course availability management

### Enrollment Workflow
- **Discount Application**: Coupon code support with validation
- **Payment Processing**: Secure payment intent creation
- **Enrollment Tracking**: Complete enrollment lifecycle management

### AI-Enhanced Features
- **RAG Search**: Semantic search through course content
- **Conversational Q&A**: AI-powered answers to course-related questions
- **Intelligent Planning**: Automated workflow orchestration

## Technology Stack

- **Backend**: FastAPI (Python async web framework)
- **Database**: MySQL with SQLAlchemy ORM
- **AI/ML**: 
  - Groq API (LLM for planning)
  - Sentence Transformers (embeddings)
  - ChromaDB (vector storage)
  - Hugging Face Transformers
- **Authentication**: Python-JOSE, PassLib, Cryptography
- **Communication**: MCP (Model Context Protocol)
- **Email**: FastAPI-Mail for notifications
- **Deployment**: Uvicorn ASGI server

## API Endpoints

### Orchestrator
- `POST /orchestrate` - Main orchestration endpoint
- `GET /health` - Health check

### Authentication
- `POST /signup` - User registration
- `POST /login` - User login
- `GET /auth/me` - Current user session

### Courses
- `GET /courses` - List courses with search/filtering
- `GET /courses/{id}` - Get specific course details
- `POST /courses/seed` - Bulk course creation

### Discounts
- `GET /discount` - List available discounts

### Payments
- `POST /payments/payments/intent` - Create payment intent

### Enrollments
- `POST /discount/enrollments` - Create enrollment
- `GET /discount/enrollments/{user_id}` - List user enrollments

### RAG
- `GET /health` - Health check
- `GET /search` - Semantic search
- `POST /rag/ask` - Q&A with context

## Business Flow

1. **User Registration**: New users sign up with email/password
2. **Authentication**: Users login to obtain JWT tokens
3. **Course Discovery**: Browse available courses with search
4. **Discount Application**: Apply valid discount codes
5. **Payment**: Create payment intents for course fees
6. **Enrollment**: Complete course enrollment after payment
7. **AI Assistance**: Use RAG for course information queries

## Installation & Setup

1. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables (see `.env` files in each service)

4. Start services in order (database, then individual services, finally orchestrator)

## Development

Each service runs independently on different ports:
- Orchestrator: 9000
- Authentication: 8080
- Courses: 8081
- Discounts: 8082
- Enrollments: 8083
- Payments: 8084
- RAG: 8085
- Intent: 8087
- MCP: 8000

## Security

- JWT token-based authentication
- Password hashing with bcrypt
- Input validation and sanitization
- Protected endpoints for sensitive operations
- Token validation for payment/enrollment operations

## Future Enhancements

- Multi-tenant support
- Advanced analytics and reporting
- Integration with learning management systems
- Mobile app support
- Advanced AI features (recommendations, personalized learning paths)

# Create virtual environment
1. python3 -m venv venv
2. source venv/bin/activate
# Install requirements
1. python3 -m pip install -r requirements.txt

REST API

REGISTRATION Tool:

Health Endpoint:
curl --location 'http://localhost:8080/health' \
--header 'accept: application/json'

SignUp:
curl --location 'http://localhost:8080/signup' \
--header 'accept: application/json' \
--header 'Content-Type: application/json' \
--data-raw '{
  "email": "abc@ab.com",
  "password": "123456",
  "name": "Raj"
}'

SignIn:
curl --location 'http://localhost:8080/login' \
--header 'accept: application/json' \
--header 'Content-Type: application/json' \
--data-raw '{
  "email": "abc@ab.com",
  "password": "123456"
}'

Current Session:
curl --location 'http://localhost:8080/auth/me' \
--header 'Authorization: Bearer '

RAG Tool:

health:
curl --location 'http://localhost:8085/health' \
--header 'accept: application/json'

search: 
curl --location 'http://localhost:8085/search?q=aiml&top_k=8' \
--header 'accept: application/json' \
--data ''

ask:
curl --location 'http://localhost:8085/rag/ask' \
--header 'accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
  "query": "aiml",
  "top_k": 6
}'

PAYMENT Tool:

health:
curl --location 'http://localhost:8084/health' \
--header 'accept: application/json'

payment:
curl --location 'http://localhost:8084/payments/payments/intent' \
--header 'accept: application/json' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer ' \
--data '{
  "enrollment_id": 1
}'

ENROLLMENT Tool:
health:
curl --location 'http://localhost:8083/health' \
--header 'accept: application/json'

enrollment: 
curl --location 'http://localhost:8083/discount/enrollments' \
--header 'accept: application/json' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiaWF0IjoxNzYyMjU1ODgxLCJleHAiOjE3NjIyNTk0ODF9.lR_D4L58MvWP0ehEcjNOxCJbsb9wccNIVXlr4UXRsGM' \
--data '{
  "course_id": 1,
  "discount_id": 1
}'

list the enrollments:
curl --location 'http://localhost:8083/discount/enrollments/2' \
--header 'accept: application/json' \
--header 'Authorization: Bearer '

DISCOUNTS Tool:
Health:
curl --location 'http://localhost:8082/health' \
--header 'accept: application/json'

discounts list:
curl --location 'http://localhost:8082/discount' \
--header 'accept: application/json'

COURSES Tool:
health:
curl --location 'http://localhost:8081/health' \
--header 'accept: application/json'

list courses:
curl --location 'http://localhost:8081/courses?limit=20&offset=0&include_inactive=false' \
--header 'accept: application/json'

List courses by Id:
curl --location 'http://localhost:8081/courses/1' \
--header 'accept: application/json'

Business Flow:
Signup

If the user does not have an account, call the signup tool with name, email, password.

Save returned user_id and/or email in context.

Signin

Call the signin tool with email, password.

Save the returned user_id and JWT/access token in context.

Authenticate (orchestrator level)

Validate the token once centrally (auth service or internal check).

Extract and store user_id for later tools.

Downstream microservices usually receive user_id directly (no need to validate again).

List available courses

Call list_courses to show the user which courses exist.

If the user already specified a course (e.g. “AIML course”), choose the best matching course from list_courses.

Get discounts (if relevant)

Call list_discounts to get available coupon codes.

Optionally filter only ACTIVE discounts.

If the user mentions a specific coupon, select that code.

Apply discount (optional)

If the user wants a discount, call apply_discount with course_id and selected code.

Use final_price_cents from the response to determine the amount to charge.

If no discount is used, use course.price_cents.

Create payment (payment first)

Call create_payment_intent with:

user_id

course_id

amount_cents (either discounted or full price)

Read payment_id and status from the response.

Only continue if status == "PAID" (for MOCK provider).

Create enrollment

Call enroll_course with:

user_id

course_id

payment_id

Save the returned enrollment_id and status.

List enrolled courses

Call something like list_enrollments (or repeatedly get_enrollment_by_id) to show all user’s enrollments.

Optionally join with list_courses to show course titles and details.