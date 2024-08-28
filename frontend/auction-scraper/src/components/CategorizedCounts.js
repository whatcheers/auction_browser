import React from 'react';
import { Box, Typography, List, ListItem, ListItemText } from '@mui/material';

const CategorizedCounts = ({ categorizedData, onCategoryClick }) => {
  return (
    <Box className="categorized-counts" sx={{ width: '300px', padding: '20px' }}>
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
    </Box>
  );
};

export default CategorizedCounts;