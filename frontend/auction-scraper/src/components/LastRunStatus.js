import React, { useState, useEffect } from 'react';
import { Box, Typography, CircularProgress } from '@mui/material';

const API_URL = process.env.REACT_APP_API_URL || 'https://hashbrowns:3002';

const LastRunStatus = () => {
  const [status, setStatus] = useState(null);
  const [timestamp, setTimestamp] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();

    const fetchStatus = async () => {
      try {
        const response = await fetch(`${API_URL}/api/last-run-status`, {
          credentials: 'include',
          signal: controller.signal
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (isMounted) {
          setStatus(data.status);
          setTimestamp(data.timestamp);
          setError('');
        }
      } catch (err) {
        if (err.name !== 'AbortError' && isMounted) {
          console.error('Error fetching last run status:', err);
          setError('Failed to fetch status');
          setStatus('Unknown');
          setTimestamp(null);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchStatus();

    return () => {
      isMounted = false;
      controller.abort();
    };
  }, []);

  if (loading) {
    return <CircularProgress size={24} />;
  }

  return (
    <Box>
      <Typography variant="body2" color={error ? 'error' : 'inherit'}>
        {error ? `Error: ${error}` : `Last Run Status: ${status || 'Unknown'}`}
      </Typography>
      <Typography variant="body2">
        {timestamp ? `Timestamp: ${new Date(timestamp).toLocaleString()}` : 'Timestamp: Unknown'}
      </Typography>
    </Box>
  );
};

export default LastRunStatus;