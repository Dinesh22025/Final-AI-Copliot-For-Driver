import { useEffect, useRef, useState } from 'react'
import api from './api'

export default function DashboardPage() {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)
  const audioContextRef = useRef(null)
  const alertIntervalRef = useRef(null)
  const analysisIntervalRef = useRef(null)
  
  const [analysis, setAnalysis] = useState(null)
  const [alert, setAlert] = useState(null)
  const [isAlertActive, setIsAlertActive] = useState(false)
  const [cameraError, setCameraError] = useState(null)
  const [analysisError, setAnalysisError] = useState(null)
  const [hasSpokenAlert, setHasSpokenAlert] = useState(false)
  const [cameraReady, setCameraReady] = useState(false)

  // Initialize camera ONCE
  useEffect(() => {
    let mounted = true
    
    const startCamera = async () => {
      try {
        console.log('[Camera] Requesting camera access...')
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'user'
          }
        })
        
        if (!mounted) {
          stream.getTracks().forEach(track => track.stop())
          return
        }
        
        streamRef.current = stream
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream
          
          // Wait for video to be ready
          videoRef.current.onloadedmetadata = () => {
            console.log('[Camera] Metadata loaded')
            videoRef.current.play()
              .then(() => {
                console.log('[Camera] Playing successfully')
                setCameraReady(true)
                setCameraError(null)
              })
              .catch(err => {
                console.error('[Camera] Play error:', err)
                setCameraError('Failed to start video playback')
              })
          }
        }
      } catch (err) {
        console.error('[Camera] Access error:', err)
        setCameraError(err.message)
      }
    }
    
    startCamera()
    
    return () => {
      mounted = false
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
        console.log('[Camera] Stopped')
      }
    }
  }, []) // Empty dependency - runs ONCE

  // Voice alert
  const speakAlert = (message) => {
    if ('speechSynthesis' in window && !hasSpokenAlert) {
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(message)
      utterance.rate = 1.0
      utterance.volume = 1.0
      window.speechSynthesis.speak(utterance)
      setHasSpokenAlert(true)
    }
  }

  // Beep sound
  const createBeep = () => {
    try {
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)()
      }
      const ctx = audioContextRef.current
      const oscillator = ctx.createOscillator()
      const gainNode = ctx.createGain()
      oscillator.connect(gainNode)
      gainNode.connect(ctx.destination)
      oscillator.frequency.setValueAtTime(1000, ctx.currentTime)
      gainNode.gain.setValueAtTime(0.7, ctx.currentTime)
      gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.4)
      oscillator.start(ctx.currentTime)
      oscillator.stop(ctx.currentTime + 0.4)
    } catch (err) {
      console.error('[Audio] Error:', err)
    }
  }

  const startAlert = (alertType) => {
    if (alertIntervalRef.current) return
    
    console.log('[Alert] Starting for:', alertType)
    setIsAlertActive(true)
    
    const beepIntervals = {
      sleeping: 300,
      drowsy: 500,
      tired: 800,
      yawning: 600,
      distracted: 600
    }
    
    const messages = {
      sleeping: 'Wake up immediately! You are sleeping!',
      drowsy: 'Wake up! You are getting drowsy!',
      tired: 'You look tired! Take a break soon!',
      yawning: 'You are tired! Take a break!',
      distracted: 'Look at the road! Do not get distracted!'
    }
    
    createBeep()
    speakAlert(messages[alertType] || 'Alert!')
    
    alertIntervalRef.current = setInterval(() => {
      createBeep()
    }, beepIntervals[alertType] || 600)
  }

  const stopAlert = () => {
    if (alertIntervalRef.current) {
      clearInterval(alertIntervalRef.current)
      alertIntervalRef.current = null
      console.log('[Alert] Stopped')
    }
    setIsAlertActive(false)
    setHasSpokenAlert(false)
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
    }
  }

  // Frame analysis loop
  useEffect(() => {
    if (!cameraReady) return
    
    const analyzeFrame = async () => {
      if (!videoRef.current || !canvasRef.current) return
      if (videoRef.current.readyState !== videoRef.current.HAVE_ENOUGH_DATA) return
      
      try {
        const ctx = canvasRef.current.getContext('2d')
        const width = videoRef.current.videoWidth
        const height = videoRef.current.videoHeight
        
        if (width === 0 || height === 0) return
        
        canvasRef.current.width = width
        canvasRef.current.height = height
        ctx.drawImage(videoRef.current, 0, 0, width, height)
        
        const frame = canvasRef.current.toDataURL('image/jpeg', 0.7)
        
        const { data } = await api.post('/api/monitor/analyze', { frame })
        
        console.log('[Analysis]', data.analysis.status, 'Faces:', data.analysis.faces)
        
        setAnalysis(data.analysis)
        setAlert(data.alert)
        setAnalysisError(null)
        
        // Handle alerts
        const alertStates = ['drowsy', 'yawning', 'distracted', 'sleeping', 'tired']
        if (data.alert?.active && alertStates.includes(data.analysis.status)) {
          if (!alertIntervalRef.current) {
            startAlert(data.analysis.status)
          }
        } else if (data.analysis.status === 'focused') {
          stopAlert()
        }
      } catch (err) {
        console.error('[Analysis] Error:', err)
        setAnalysisError(err.response?.data?.detail || err.message || 'Backend error')
      }
    }
    
    console.log('[Analysis] Starting loop')
    analysisIntervalRef.current = setInterval(analyzeFrame, 1000)
    
    return () => {
      if (analysisIntervalRef.current) {
        clearInterval(analysisIntervalRef.current)
        console.log('[Analysis] Stopped')
      }
      stopAlert()
    }
  }, [cameraReady])

  const getStatusColor = (status) => {
    const colors = {
      focused: 'green',
      sleeping: '#8B0000',
      drowsy: 'red',
      tired: '#FF6347',
      yawning: 'orange',
      distracted: 'yellow',
      error: 'gray'
    }
    return colors[status] || 'gray'
  }

  return (
    <div>
      <h2>Live Driver Dashboard</h2>
      <div className="grid">
        <div className="card">
          <video 
            ref={videoRef} 
            autoPlay 
            playsInline 
            muted 
            className="video" 
            style={{ width: '100%', height: 'auto', backgroundColor: '#000' }} 
          />
          <canvas ref={canvasRef} style={{ display: 'none' }} />
        </div>
        
        <div className="card">
          <h3>Real-time Status</h3>
          
          {cameraError && (
            <div style={{padding: '10px', backgroundColor: '#d32f2f', borderRadius: '5px', marginBottom: '10px'}}>
              <p><strong>Camera Error:</strong> {cameraError}</p>
            </div>
          )}
          
          {analysisError && (
            <div style={{padding: '10px', backgroundColor: '#f39c12', borderRadius: '5px', marginBottom: '10px'}}>
              <p><strong>Analysis Error:</strong> {analysisError}</p>
            </div>
          )}
          
          <p>Status: <strong style={{color: getStatusColor(analysis?.status)}}>
            {analysis?.status || 'Initializing...'}
          </strong></p>
          <p>Confidence: <strong>{analysis?.confidence ? (analysis.confidence * 100).toFixed(1) + '%' : '0%'}</strong></p>
          <p>Head Tilt: <strong>{analysis?.head_tilt ?? 0}°</strong></p>
          <p>Gaze Offset: <strong>{analysis?.gaze_offset ?? 0}%</strong></p>
          <p>Faces: <strong>{analysis?.faces ?? 0}</strong></p>
          <p>EAR: <strong>{analysis?.ear ?? 0}</strong></p>
          <p>MAR: <strong>{analysis?.mar ?? 0}</strong></p>
          
          {isAlertActive && (
            <div style={{
              padding: '15px', 
              backgroundColor: '#d32f2f', 
              borderRadius: '5px', 
              marginTop: '10px',
              animation: 'pulse 1s infinite'
            }}>
              <p style={{fontSize: '18px', fontWeight: 'bold'}}>🚨 ALERT ACTIVE 🚨</p>
              <p>{alert?.message || 'Alert in progress'}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
