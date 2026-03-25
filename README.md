# Driver AI Co-Pilot

A full-stack application combining a React frontend with a Flask backend for driver monitoring and AI assistance.

## Project Structure

```
driver-ai-copilot/
├── frontend/          # React/Vite application
│   ├── src/          # React source code
│   ├── public/       # Static assets
│   ├── dist/         # Built frontend (generated)
│   └── package.json
├── backend/          # Flask API server
│   ├── app/          # Flask application
│   ├── run.py        # Server entry point
│   └── requirements.txt
└── package.json      # Root package.json for combined commands
```

## Setup

1. **Install all dependencies:**
   ```bash
   npm run install:all
   ```

2. **Build the frontend:**
   ```bash
   npm run build
   ```

## Running the Application

### Development Mode (Recommended)
Run both frontend and backend simultaneously:
```bash
npm run dev
```

This will:
- Start the Flask backend on `http://localhost:5000`
- Start the Vite dev server on `http://localhost:5173` with API proxying

### Production Mode
1. Build the frontend and start the backend:
   ```bash
   npm run build
   npm start
   ```

The application will be available at `http://localhost:5000`

## API Endpoints

- `GET /` - Serves the React application
- `GET /health` - Health check
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User authentication
- Additional API endpoints for driver monitoring features

## Development

### Frontend Only
```bash
npm run dev:frontend
```

### Backend Only
```bash
npm run dev:backend
```

## Technologies Used

- **Frontend:** React, Vite, Axios
- **Backend:** Flask, SQLAlchemy, TensorFlow
- **Database:** SQLite (development)