import React, { memo, useRef, useCallback } from 'react';
import { Paper, Typography, IconButton, List, ListItem, ListItemText } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { ThemeProvider, createTheme } from '@mui/material/styles';

const CategorizedCountsPopup = memo(({ categorizedData, onCategoryClick, onClose, popupState = {}, onPopupChange, darkMode }) => {
  const { position = { x: 50, y: 50 }, size = { width: 300, height: 400 } } = popupState;
  const isDragging = useRef(false);
  const dragStart = useRef({ x: 0, y: 0 });

  const handleMouseDown = useCallback((e) => {
    isDragging.current = true;
    dragStart.current = { x: e.clientX, y: e.clientY };
  }, []);

  const handleMouseMove = useCallback((e) => {
    if (isDragging.current) {
      const dx = e.clientX - dragStart.current.x;
      const dy = e.clientY - dragStart.current.y;
      const newState = { position: { x: position.x + dx, y: position.y + dy }, size };
      
      if (typeof onPopupChange === 'function') {
        onPopupChange(newState);
      }
      dragStart.current = { x: e.clientX, y: e.clientY };
    }
  }, [position, size, onPopupChange]);

  const handleMouseUp = useCallback(() => {
    isDragging.current = false;
  }, []);

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
          backgroundColor: darkMode ? '#424242' : '#fff',
          borderRadius: '8px',
          boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
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
            Categorized Counts
          </Typography>
          <List>
            {Object.entries(categorizedData).map(([category, items]) => (
              <ListItem 
                key={category} 
                button 
                onClick={() => onCategoryClick(category)}
                sx={{ 
                  '&:hover': {
                    backgroundColor: 'rgba(0, 0, 0, 0.04)',
                  },
                }}
              >
                <ListItemText 
                  primary={`${category}: ${items.length}`} 
                  sx={{
                    '& .MuiListItemText-primary': {
                      fontWeight: 'bold',
                    },
                  }}
                />
              </ListItem>
            ))}
          </List>
        </div>
        <IconButton
          sx={{ position: 'absolute', top: 8, right: 8 }}
          onClick={onClose}
        >
          <CloseIcon />
        </IconButton>
      </Paper>
    </ThemeProvider>
  );
});

export default CategorizedCountsPopup;