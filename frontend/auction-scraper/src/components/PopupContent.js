import React, { memo, useRef, useCallback } from 'react';
import { Paper, Typography, IconButton, Tooltip } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import InfoIcon from '@mui/icons-material/Info';
import FavoriteIcon from '@mui/icons-material/Favorite';
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder';
import { ThemeProvider, createTheme } from '@mui/material/styles';

const PopupItem = memo(({ item, isSelected, onFavorite, onRowClick }) => {
  console.log('Rendering PopupItem:', item.id || item.url);

  return (
    <div
      style={{ 
        marginBottom: '10px', 
        backgroundColor: isSelected ? '#e0e0e0' : 'transparent',
        padding: '8px',
        borderRadius: '4px'
      }}
      onClick={() => onRowClick(item)}
    >
      <Typography variant="body1">
        <a href={item.url} target="_blank" rel="noopener noreferrer">
          {item.item_name || 'Unnamed Item'}
        </a>
      </Typography>
      <Typography variant="body2" color="textSecondary">
        Location: {item.location || 'Unknown'}
      </Typography>
      <Typography variant="body2" color="textSecondary">
        Time Left: {item.time_left || 'N/A'}
      </Typography>
      <Typography variant="body2" color="textSecondary">
        Current Bid: {item.current_bid || 'N/A'}
      </Typography>
      <IconButton 
        onClick={(e) => {
          e.stopPropagation();
          onFavorite(item);
        }}
        size="small"
      >
        {item.favorite === 'Y' ? <FavoriteIcon color="error" /> : <FavoriteBorderIcon />}
      </IconButton>
    </div>
  );
});

const PopupContent = memo(({ features, onClose, onFavorite, onRowClick, selectedRows = [], popupState = {}, onPopupChange, darkMode }) => {
  const { position = { x: 0, y: 0 }, size = { width: 300, height: 400 } } = popupState;
  const isDragging = useRef(false);
  const isResizing = useRef(false);
  const dragStart = useRef({ x: 0, y: 0 });

  const handleMouseDown = useCallback((e) => {
    if (e.target.classList.contains('resize-handle')) {
      isResizing.current = true;
    } else {
      isDragging.current = true;
    }
    dragStart.current = { x: e.clientX, y: e.clientY };
  }, []);

  const handleMouseMove = useCallback((e) => {
    if (isDragging.current || isResizing.current) {
      const dx = e.clientX - dragStart.current.x;
      const dy = e.clientY - dragStart.current.y;
      const newState = isDragging.current
        ? { position: { x: position.x + dx, y: position.y + dy }, size }
        : { position, size: { width: Math.max(200, size.width + dx), height: Math.max(200, size.height + dy) } };
      
      if (typeof onPopupChange === 'function') {
        onPopupChange(newState);
      }
    }
    dragStart.current = { x: e.clientX, y: e.clientY };
  }, [position, size, onPopupChange]);

  const handleMouseUp = useCallback(() => {
    isDragging.current = false;
    isResizing.current = false;
  }, []);

  console.log('PopupContent: Received new props', { 
    featuresCount: features.length, 
    selectedRowsCount: selectedRows.length 
  });

  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
    },
  });

  return (
    <ThemeProvider theme={theme}>
      <Paper
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        sx={{
          p: 2,
          backgroundColor: darkMode ? '#333' : '#f5f5f5',  // Adjust background color based on dark mode
          borderRadius: '8px',
          boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
          position: 'absolute',
          left: position.x,
          top: position.y,
          width: size.width,
          height: size.height,
          overflow: 'hidden',
          cursor: 'move',
        }}
      >
        <div style={{ height: '100%', overflowY: 'auto' }}>
          <Typography variant="h6" gutterBottom>
            Details
          </Typography>
          {features.map((f) => {
            const item = f.get ? f.get('itemData') : f.itemData || f;
            const isSelected = selectedRows.includes(item.url);
            return (
              <PopupItem
                key={item.id || item.url}
                item={item}
                isSelected={isSelected}
                onFavorite={onFavorite}
                onRowClick={onRowClick}
              />
            );
          })}
          <div>
            <Tooltip title="More Info">
              <IconButton>
                <InfoIcon />
              </IconButton>
            </Tooltip>
          </div>
        </div>
        <IconButton
          sx={{ position: 'absolute', top: 8, right: 8 }}
          onClick={onClose}
        >
          <CloseIcon />
        </IconButton>
        <div
          className="resize-handle"
          style={{
            position: 'absolute',
            bottom: 0,
            right: 0,
            width: 20,
            height: 20,
            cursor: 'se-resize',
          }}
        />
      </Paper>
    </ThemeProvider>
  );
});

export default PopupContent;
