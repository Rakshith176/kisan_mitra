# 🌾 Agricultural AI Platform - Setup Guide

This guide will help you set up and run the Agricultural AI Platform on your local machine. The platform consists of a FastAPI backend and a Flutter frontend.

## 📋 Prerequisites

### System Requirements
- **Operating System**: macOS, Windows, or Linux
- **Python**: 3.11 or higher
- **Flutter**: 3.16 or higher
- **Git**: Latest version
- **Memory**: At least 4GB RAM (8GB recommended)
- **Storage**: At least 2GB free space

### Required API Keys
Before starting, you'll need to obtain the following API keys:

1. **Google AI API Key** (Required)
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Create a new API key
   - This is used for Gemini AI integration

2. **Tavily API Key** (Required)
   - Visit [Tavily](https://tavily.com/)
   - Sign up for a free account
   - Get your API key
   - This is used for web search capabilities

3. **Optional API Keys**
   - **Weather API**: Open-Meteo (free, no key required)
   - **Market Data**: Data.gov.in (free, no key required)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd capital_one
```

### 2. Set Up Environment Variables
```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file with your API keys
nano .env  # or use your preferred editor
```

Update the `.env` file with your actual API keys:
```env
# Required API Keys
GOOGLE_API_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# App Configuration
APP_ENV=development
LOG_LEVEL=INFO
```

## 🔧 Backend Setup

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### 4. Start the Backend Server
```bash
# From the backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

The backend will be available at:
- **API Documentation**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health
- **WebSocket**: ws://localhost:8080/ws

### 6. Verify Backend Setup
Visit http://localhost:8080/health in your browser. You should see:
```json
{
  "status": "ok",
  "env": "development"
}
```

## 📱 Frontend Setup

### 1. Navigate to Frontend Directory
```bash
cd ../frontend
```

### 2. Check Flutter Installation
```bash
flutter doctor
```

If Flutter is not installed, follow the [official Flutter installation guide](https://flutter.dev/docs/get-started/install).

### 3. Get Dependencies
```bash
flutter pub get
```

### 4. Run the App

#### For Development
```bash
# Start the app in debug mode
flutter run

# Or specify a device
flutter run -d chrome  # For web
flutter run -d <device-id>  # For mobile
```

### 5. Verify Frontend Setup
- The app should launch and connect to the backend
- You should see the main interface with navigation options
- Test the chat functionality to ensure WebSocket connection works

## 🔗 Connecting Frontend to Backend

### Configuration
The frontend is configured to connect to the backend at `http://localhost:8080`. If you need to change this:

1. **For Development**: Update the API base URL in your Flutter app

### 3. Tests
1. Start the backend server
2. Start the frontend app
3. Test the following features:
   - User registration/login
   - Chat functionality
   - Market price queries
   - Weather information
   - Crop recommendations


#### Frontend Issues - Common Solutions

**Flutter Dependencies**
```bash
# Clean and get dependencies
flutter clean
flutter pub get
```

**Build Issues**
```bash
# Clean build cache
flutter clean
flutter pub get
flutter run
```

**Device Connection**
```bash
# List available devices
flutter devices
# Run on specific device
flutter run -d <device-id>
```


## 🔄 Development Workflow

### 1. Start Development Environment
```bash
# Terminal 1: Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Terminal 2: Start frontend
cd frontend
flutter run
```


This setup guide should get you up and running with the Agricultural AI Platform. The platform combines cutting-edge AI technology with practical agricultural knowledge to help farmers make better decisions.
