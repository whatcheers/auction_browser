import React, { useState, useEffect, useCallback } from 'react';
import { Box, Typography, CircularProgress, Alert as MuiAlert, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

const apiUrl = process.env.REACT_APP_API_URL || 'https://hashbrowns:3002';

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [debugInfo, setDebugInfo] = useState('');

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const currentDate = new Date();
        const startDate = currentDate.toISOString().split('T')[0];
        const endDate = new Date(currentDate.setDate(currentDate.getDate() + 90)).toISOString().split('T')[0];
        
        const url = `${apiUrl}/api/alerts/?startDate=${startDate}&endDate=${endDate}`;
        setDebugInfo(`Fetching from: ${url}`);
        
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setDebugInfo(prev => `${prev}\nReceived data: ${JSON.stringify(data)}`);
        setAlerts(data);
        setError('');
      } catch (err) {
        console.error('Error fetching alerts:', err);
        setError(`Failed to fetch alerts: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchAlerts();
  }, []);

  const handleDismiss = useCallback(async (alertId) => {
    try {
      const response = await fetch(`${apiUrl}/api/alerts/${alertId}`, {
        method: 'DELETE',
        credentials: 'include',
      });

      if (!response.ok) {
        if (response.status === 404) {
          console.warn(`Alert with ID ${alertId} not found. It may have been already dismissed.`);
          // Remove the alert from the local state even if it's not found on the server
          setAlerts(prevAlerts => prevAlerts.filter(alert => alert.id !== alertId));
        } else {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      } else {
        const result = await response.json();
        if (result.success) {
          setAlerts(prevAlerts => prevAlerts.filter(alert => alert.id !== alertId));
        } else {
          throw new Error(result.error || 'Failed to dismiss alert');
        }
      }
    } catch (error) {
      console.error('Error dismissing alert:', error);
      setError(`Failed to dismiss alert: ${error.message}`);
    }
  }, [apiUrl]);

  if (loading) {
    return <CircularProgress size={24} />;
  }

  return (
    <Box>
      <Typography variant="h6">Alerts</Typography>
      {error && <MuiAlert severity="error">{error}</MuiAlert>}
      {debugInfo && <MuiAlert severity="info">{debugInfo}</MuiAlert>}
      {alerts.length === 0 && !loading && !error && (
        <MuiAlert severity="info">No new alerts found.</MuiAlert>
      )}
      {alerts.map((alert, index) => (
        <MuiAlert
          key={index}
          severity="info"
          action={
            <IconButton
              aria-label="close"
              color="inherit"
              size="small"
              onClick={() => handleDismiss(alert.id)}
            >
              <CloseIcon fontSize="inherit" />
            </IconButton>
          }
        >
          New item matching "{alert.keyword}" found: {alert.item_name}
        </MuiAlert>
      ))}
    </Box>
  );
};

export default Alerts;
