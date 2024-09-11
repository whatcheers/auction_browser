import React, { useEffect, useState } from 'react';
import { Typography, Tooltip, Box } from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';

const DailyAverages = ({ apiUrl }) => {
  const [dailyAverages, setDailyAverages] = useState(null);

  useEffect(() => {
    const fetchDailyAverages = async () => {
      try {
        const response = await fetch(`${apiUrl}/api/daily-averages`);
        const data = await response.json();
        setDailyAverages(data[0]); // Get the most recent day's averages
      } catch (error) {
        console.error('Failed to fetch daily averages:', error);
      }
    };

    fetchDailyAverages();
    const intervalId = setInterval(fetchDailyAverages, 300000); // Refresh every 5 minutes
    return () => clearInterval(intervalId);
  }, [apiUrl]);

  if (!dailyAverages) {
    return null; // Don't render anything while loading
  }

  const tooltipContent = (
    <div>
      <Typography variant="body2">Daily Averages:</Typography>
      <Typography variant="body2">Auctions Scraped: {Math.round(dailyAverages.avg_auctions_scraped)}</Typography>
      <Typography variant="body2">Items Added: {Math.round(dailyAverages.avg_items_added)}</Typography>
      <Typography variant="body2">Items Updated: {Math.round(dailyAverages.avg_items_updated)}</Typography>
      <Typography variant="body2">Items Removed: {Math.round(dailyAverages.avg_items_removed)}</Typography>
      <Typography variant="body2">Errors: {dailyAverages.error_count}</Typography>
      <Typography variant="body2">Last Run: {new Date(dailyAverages.last_run_timestamp).toLocaleString()}</Typography>
    </div>
  );

  const hasErrors = dailyAverages.error_count > 0;

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
      <Typography variant="body2" sx={{ mr: 1 }}>
        Daily Avg: {Math.round(dailyAverages.avg_items_added)} items
      </Typography>
      {hasErrors ? (
        <ErrorIcon color="error" fontSize="small" sx={{ mr: 1 }} />
      ) : (
        <CheckCircleIcon color="success" fontSize="small" sx={{ mr: 1 }} />
      )}
      <Tooltip title={tooltipContent} arrow>
        <InfoIcon fontSize="small" />
      </Tooltip>
    </Box>
  );
};

export default DailyAverages;
