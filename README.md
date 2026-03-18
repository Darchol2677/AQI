# AQI Detector Web Application

A complete Air Quality Index (AQI) web application built with Flask (Python) and Vanilla HTML/CSS/JS.

## Features
- Real-time AQI search for global cities.
- Auto-detect user location to fetch local AQI.
- Display detailed pollutants (PM2.5, PM10, CO, NO2, SO2, O3).
- Display a 24-hour interactive AQI forecast graph using Chart.js.
- Clean and responsive UI interface.
- Local Storage based Recent searches caching.

## How to Run Locally

1. Ensure Python 3.8+ is installed on your machine.
2. Clone the repository or open the project folder.
3. Keep the terminal at the project root folder.
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the Flask application:
   ```bash
   python app.py
   ```
6. Open your browser and go to: `http://127.0.0.1:5000`

## Deployment

This app uses the Free Tier Open-Meteo Air Quality & Geocoding API which does not require API keys, making deployment a breeze!

### 1. Deploying on Vercel
Vercel is great for Serverless Flask applications.

**Steps:**
1. A `vercel.json` file is already included in this repository.
2. Push your project code to a GitHub repository.
3. Go to [Vercel](https://vercel.com/), login, and click **"Add New Project"**.
4. Import your newly created GitHub repository.
5. Vercel will auto-detect the configuration. Click **Deploy**.

### 2. Deploying on Render

Render provides a managed "Web Service" deployment for Flask apps.

**Steps:**
1. Push your project to a GitHub repository.
2. Go to [Render](https://render.com/), login, and click **"New +" -> "Web Service"**.
3. Connect your GitHub repository.
4. In the configuration settings:
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Select the "Free" tier and click **Create Web Service**.
6. Deployment might take a few minutes before going live.
