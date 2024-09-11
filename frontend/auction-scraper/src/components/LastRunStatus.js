import React, { useState, useEffect } from 'react';
import { Box, Typography, CircularProgress } from '@mui/material';

const API_URL = process.env.REACT_APP_API_URL || 'https://hashbrowns:3002';

const LastRunStatus = () => {
  const [averages, setAverages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();

    const fetchAverages = async () => {
      try {
        const response = await fetch(`${API_URL}/api/daily-averages`, {
          credentials: 'include',
          signal: controller.signal
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (isMounted) {
          setAverages(data);
          setError('');
        }
      } catch (err) {
        if (err.name !== 'AbortError' && isMounted) {
          console.error('Error fetching daily averages:', err);
          setError('Failed to fetch daily averages');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchAverages();

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
        {error ? `Error: ${error}` : 'Daily Averages:'}
      </Typography>
      {averages.map((avg, index) => (
        <Box key={index}>
          <Typography variant="body2">Date: {avg.date}</Typography>
          <Typography variant="body2">Total Sales: {avg.total_sales}</Typography>
          <Typography variant="body2">Addresses Skipped: {avg.avg_addresses_skipped}</Typography>
          {/* Add more fields as needed */}
        </Box>
      ))}
    </Box>
  );
};

export default LastRunStatus;