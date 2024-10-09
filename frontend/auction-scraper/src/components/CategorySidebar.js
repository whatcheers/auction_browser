import React from 'react';
import { Box, List, ListItem, ListItemText, Typography, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

const CategorySidebar = ({ categorizedData, onClose, onCategoryClick }) => {
  return (
    <Box sx={{ width: 300, height: '100%', overflow: 'auto', bgcolor: 'background.paper', position: 'fixed', right: 0, top: 0, zIndex: 1000 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 2 }}>
        <Typography variant="h6">Categories</Typography>
        <IconButton onClick={onClose}>
          <CloseIcon />
        </IconButton>
      </Box>
      <List>
        {Object.entries(categorizedData).map(([category, items]) => (
          <ListItem 
            key={category} 
            button 
            onClick={() => onCategoryClick(category)}
          >
            <ListItemText 
              primary={`${category} (${items.length})`} 
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );
};

export default CategorySidebar;
