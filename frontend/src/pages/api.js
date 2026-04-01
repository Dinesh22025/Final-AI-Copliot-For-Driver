import axios from 'axios'

// Better API config for local + deployment
const api = axios.create({
  baseURL: import.meta.env.DEV 
    ? 'http://localhost:8000'  // Local: backend routes include /api/*
    : import.meta.env.VITE_API_URL || 'https://your-backend.onrender.com',  // Prod: set VITE_API_URL in .env or hosting
});

export const setToken = (token) => {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`
    localStorage.setItem('token', token)
  } else {
    delete api.defaults.headers.common.Authorization
    localStorage.removeItem('token')
  }
}

const storedToken = localStorage.getItem('token')
if (storedToken) {
  setToken(storedToken)
}

export default api
