# Mansio Backend  

## Overview  

This is a backend system built using **FastAPI, RabbitMQ, PostgreSQL, and Stripe**, with AI-powered property enhancements using **Cohere**. The system handles property management, AI-enhanced descriptions, payment processing, and integrates with **RabbitMQ** for task queueing.  

## Architecture  

The project follows a **microservice-inspired architecture** with background workers:  

- **FastAPI Backend**: Handles API requests, database operations, and task publishing.  
- **RabbitMQ Message Queue**: Queues tasks for AI processing and Stripe payment handling.  
- **AI Worker** (`ai_worker.py`): Enhances property descriptions and generates AI keywords.  
- **Stripe Worker** (`stripe_worker.py`): Manages Stripe product creation and updates.  
- **PostgreSQL Database**: Stores property data, including AI-enhanced descriptions and Stripe product IDs.  

## Features  

✅ **Property Management** (CRUD operations)  
✅ **AI-enhanced Property Descriptions** (Cohere API)  
✅ **Stripe Integration** (Product creation & payments)  
✅ **Stripe Webhook Integration** (Updates after payment completion)  
✅ **Asynchronous Task Processing** (RabbitMQ workers)  
✅ **PostgreSQL Storage**  

## Setup Instructions  

### 1️⃣ Clone the Repository  
```sh
git clone https://github.com/Himdyuti1/mansio_assignment.git
cd mansio_assignment
```

### 2️⃣ Set Up Virtual Environment
```sh
python3 -m venv env
source env/bin/activate
```

### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 4️⃣ Set Up Environment Variables
Create a .env file in the project root and configure:
```text
DATABASE_URL=postgresql+asyncpg://username:password@server-url/database_name
COHERE_API_KEY=your-cohere-api-key
STRIPE_SECRET_KEY=your-stripe-secret-key
WEBHOOK_SECRET_KEY=your-webhook-secret-key
RABBITMQ_HOST=rabbitmq-server-url
```

### 5️⃣ Create the database
Create a postgresql database with a suitable name on a local or deployed postgresql server

### 6️⃣ Initialize the relation in the database
```sh
python3 db_init.py
```

### 7️⃣ Start RabbitMQ
Ensure RabbitMQ is installed and running:

### 8️⃣ Run the FastAPI Backend
```sh
uvicorn main:app --reload
```

### 9️⃣ Start the Workers

**AI  Worker** (Handles AI-based property enhancements)
```sh
python3 ai_worker.py
```

**Stripe Worker** (Handles Stripe product creation)
```sh
python3 stripe_worker.py
```

## API Testing
All the APIs can be tested on http://localhost:8000/docs when the FastAPI server is running.
