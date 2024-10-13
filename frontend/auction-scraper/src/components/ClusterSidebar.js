import React from 'react';
import { Paper, Typography, IconButton, List, ListItem, ListItemText, ListItemSecondaryAction, Box } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import FavoriteIcon from '@mui/icons-material/Favorite';
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder';

const ClusterSidebar = ({ data, onClose, onFavorite, onRowClick, selectedRows, darkMode }) => {
  return (
    <Paper
      elevation={3}
      sx={{
        position: 'absolute',
        top: '10px',
        right: '10px',
        width: '400px',
        maxHeight: 'calc(100% - 20px)',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: darkMode ? '#333' : '#fff',
        color: darkMode ? '#fff' : '#000',
        borderRadius: '8px',
        overflow: 'hidden',
      }}
    >
      <Box sx={{ 
        padding: '16px', 
        backgroundColor: darkMode ? '#444' : '#f0f0f0', 
        borderBottom: '1px solid',
        borderColor: darkMode ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.12)',
      }}>
        <Typography variant="h6">Cluster Items ({data.length})</Typography>
        <IconButton
          onClick={onClose}
          sx={{ position: 'absolute', top: 8, right: 8 }}
        >
          <CloseIcon />
        </IconButton>
      </Box>
      <List sx={{ flexGrow: 1, overflowY: 'auto', padding: 0 }}>
        {data.map((item, index) => (
          <ListItem
            key={item.id || item.url || `item-${index}`}
            onClick={() => onRowClick(item)}
            selected={selectedRows.includes(item.url)}
            sx={{ 
              cursor: 'pointer',
              '&:hover': {
                backgroundColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.04)',
              },
            }}
          >
            <ListItemText
              primary={
                <Typography variant="body1">
                  <a href={item.url} target="_blank" rel="noopener noreferrer" style={{ color: darkMode ? '#90caf9' : '#1976d2' }}>
                    {item.item_name || 'Unnamed Item'}
                  </a>
                </Typography>
              }
              secondary={
                <Box component="span">
                  <Typography variant="body2" component="span" display="block">Location: {item.location || 'Unknown'}</Typography>
                  <Typography variant="body2" component="span" display="block">Time Left: {item.time_left || 'N/A'}</Typography>
                  <Typography variant="body2" component="span" display="block">Current Bid: ${item.current_bid || 'N/A'}</Typography>
                </Box>
              }
            />
            <ListItemSecondaryAction>
              <IconButton edge="end" onClick={(e) => { e.stopPropagation(); onFavorite(item); }}>
                {item.favorite === 'Y' ? <FavoriteIcon color="error" /> : <FavoriteBorderIcon />}
              </IconButton>
            </ListItemSecondaryAction>
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default ClusterSidebar;
