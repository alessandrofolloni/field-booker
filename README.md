# 🏟️ Field Booker

A premium web platform for sports venue discovery and management, featuring **Google ADK-powered AI** and advanced geospatial search.

## 🚀 Key Features

- **🤖 AI Assistant (Google ADK)**: Integrated with the latest **Agent Development Kit** (ADK) by Google. It understands natural language to find fields, suggest sports, and geocode locations (e.g., *"Find a padel court in Milan for tonight"*).
- **🛠️ Field Corrections System**: Community-driven data accuracy. Users can suggest fixes for existing fields (incorrect phone numbers, wrong hours, broken links) which go into a pending queue for admin review.
- **📍 Smart Address Search**: Global search experience with automatic suggestions via Nominatim API, allowing you to center the map anywhere instantly.
- **🗺️ Interactive Map (Glassmorphism)**: A modern, sleek UI featuring a dynamic search radius and custom markers for different sports (Football, Tennis, Basketball, Padel, Volleyball).
- **📱 Mobile-First Design**: Fully responsive SPA optimized for a premium experience on both desktop and mobile devices.
- **🛡️ Admin Dashboard**: Centralized panel for administrators to review and approve New Field Submissions and Corrections.
- **🔐 Secure Google Auth**: Fast and secure login via Google OAuth 2.0 and JWT.

## 🏗️ Microservices Architecture

The application is built as a set of independent, scalable services:

- **AI Assistant Service (Port 8004)**: Reasoning engine using **Google Gemini 1.5 Flash** and **Google ADK**.
- **Fields Service (Port 8002)**: Geospatial core leveraging **PostGIS** for ultra-fast spatial queries.
- **Submissions Service (Port 8003)**: Manages the community workflow for additions and corrections.
- **Auth Service (Port 8001)**: Handles identity, roles (User/Admin), and JWT token lifecycle.
- **Frontend (Port 5173)**: Vue.js 3 SPA with Pinia and a custom Design System.

## 🛠️ Requirements

- **Python 3.10+** (3.12 recommended)
- **Node.js 18+**
- **PostgreSQL** with **PostGIS** extension
- **Google Gemini API Key** (for the AI features)
- **Google OAuth Credentials** (for login)

## 🏁 Getting Started (Local Development)

1. **Configuration**:
   Copy the example environment file and fill in your keys:
   ```bash
   cp .env.example .env
   ```
   *Required variables: `GOOGLE_API_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `ADMIN_EMAILS`.*

2. **Environment Setup**:
   Install all dependencies (Backend & Frontend) and create the virtual environment:
   ```bash
   ./scripts/setup_local.sh
   ```

3. **Running the Platform**:
   Start all 5 microservices and the frontend development server simultaneously:
   ```bash
   ./scripts/run_local.sh
   ```

4. **Syncing with GitHub**:
   Use our custom script to commit and push changes easily:
   ```bash
   ./git_push.sh "Your commit message"
   ```

## 📜 License
MIT License - 2026 Field Booker Team
