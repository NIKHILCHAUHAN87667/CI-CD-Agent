import { useEffect, useRef, useState } from 'react';

export const useAgentProgress = (runId) => {
  const [progress, setProgress] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [currentStatus, setCurrentStatus] = useState('');
  const wsRef = useRef(null);

  useEffect(() => {
    if (!runId) return;

    // Connect to WebSocket
    const apiBase = import.meta.env.VITE_API_URL || 'https://cicdagentapi.onrender.com';
    const wsBase = apiBase.replace(/^http/, 'ws');
    const wsUrl = `${wsBase}/ws/runs/${runId}`;
    
    console.log(`🔌 Connecting to WebSocket: ${wsUrl}`);
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('✅ WebSocket connected');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('📨 Received progress:', data);
        
        // Update current status
        setCurrentStatus(data.status);
        
        // Add to progress log (prevent duplicates)
        setProgress(prev => {
          const isDuplicate = prev.some(
            item => item.message === data.message && item.timestamp === data.timestamp
          );
          if (isDuplicate) return prev;
          return [...prev, data];
        });
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('🔌 WebSocket disconnected');
      setIsConnected(false);
    };

    // Cleanup on unmount
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [runId]);

  const clearProgress = () => {
    setProgress([]);
    setCurrentStatus('');
  };

  return {
    progress,
    currentStatus,
    isConnected,
    clearProgress
  };
};
