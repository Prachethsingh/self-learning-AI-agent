import { useState, useEffect, useCallback } from 'react';

const useWebSocket = (url) => {
  const [data, setData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    ws.onmessage = (event) => {
      try {
        const parsedData = JSON.parse(event.data);
        setData(parsedData);
      } catch (e) {
        console.error('Error parsing WebSocket message:', e);
        setData(event.data); // Fallback to raw data
      }
    };

    ws.onerror = (event) => {
      setError(event);
      console.error('WebSocket error:', event);
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    // Cleanup on unmount
    return () => {
      ws.close();
    };
  }, [url]);

  const sendMessage = useCallback((message) => {
    // Implementation would depend on your WebSocket library
    // This is a placeholder for sending messages back to server
  }, []);

  return { data, isConnected, error, sendMessage };
};

export default useWebSocket;