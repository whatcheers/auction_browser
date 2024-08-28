import React from 'react';
import { Box, LinearProgress, Typography } from '@mui/material';

const DataLoadingProgress = ({ isLoading, loadedSize, totalSize, status }) => {
  if (!isLoading) return null;

  const progress = totalSize ? (loadedSize / totalSize) * 100 : 100;

  return (
    <Box sx={{ width: '100%', mb: 2 }}>
      <Typography variant="body2" color="text.primary" sx={{ mb: 1 }}>
        {status}
      </Typography>
      <LinearProgress variant="determinate" value={progress} />
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
        {totalSize > 0 && (
          <Typography variant="body2" color="text.secondary">
            {`Loaded: ${(loadedSize / 1024).toFixed(2)} KB of ${(totalSize / 1024).toFixed(2)} KB`}
          </Typography>
        )}
        <Typography variant="body2" color="text.secondary">
          {progress < 100 ? 'Loading...' : 'Completed!'}
        </Typography>
      </Box>
    </Box>
  );
};

export default DataLoadingProgress;
