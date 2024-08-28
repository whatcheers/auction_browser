import React, { useRef, memo } from 'react';
import Draggable from 'react-draggable';
import { Paper, Typography, IconButton, Tooltip } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import InfoIcon from '@mui/icons-material/Info';
import FavoriteIcon from '@mui/icons-material/Favorite';
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder';

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

const PopupContent = memo(({ features, onClose, onFavorite, onRowClick, selectedRows = [] }) => {
  const dragHandleRef = useRef(null);

  console.log('PopupContent: Received new props', { 
    featuresCount: features.length, 
    selectedRowsCount: selectedRows.length 
  });

  return (
    <Draggable handle=".handle" nodeRef={dragHandleRef}>
      <Paper
        ref={dragHandleRef}
        sx={{
          p: 2,
          backgroundColor: '#f5f5f5',
          borderRadius: '8px',
          boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
          minWidth: '300px',
          maxHeight: '400px',
          overflowY: 'auto',
          position: 'relative',
        }}
        className="handle"
      >
        <Typography variant="h6" gutterBottom>
          Details
        </Typography>
        {features.map((f) => {
  const item = f.get ? f.get('itemData') : f.itemData || f; // Support both Feature and plain object
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
        <IconButton
          sx={{ position: 'absolute', top: 8, right: 8 }}
          onClick={onClose}
        >
          <CloseIcon />
        </IconButton>
      </Paper>
    </Draggable>
  );
});

export default PopupContent;
