import React, { useState, useEffect } from 'react';
import { Box, Typography, CircularProgress } from '@mui/material';

const LastRunStatus = ({ apiUrl }) => {
  const [status, setStatus] = useState(null);
  const [timestamp, setTimestamp] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch(`${apiUrl}/bin/last-run-status`, {
          credentials: 'include'
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setStatus(data.status);
        setTimestamp(data.timestamp);
      } catch (err) {
        console.error('Error fetching last run status:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
  }, [apiUrl]);

  if (loading) {
    return <CircularProgress size={24} />;
  }

  if (error) {
    return <Typography variant="body2" color="error">{`Error: ${error}`}</Typography>;
  }

  return (
    <Box>
      <Typography variant="body2">{`Last Run Status: ${status}`}</Typography>
      <Typography variant="body2">{`Timestamp: ${new Date(timestamp).toLocaleString()}`}</Typography>
    </Box>
  );
};

export default LastRunStatus;