import React, { useState, useEffect } from 'react';
import { Typography, List, ListItem, ListItemText, IconButton, Box } from '@mui/material';
import FavoriteIcon from '@mui/icons-material/Favorite';
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder';

const CategoryDetails = ({ category, items, onFavorite, onRowClick, selectedRows }) => {
    const [localItems, setLocalItems] = useState(items);

    useEffect(() => {
        setLocalItems(items);
    }, [items]);

    const handleFavorite = (item) => {
        const newFavoriteStatus = item.favorite === 'Y' ? 'N' : 'Y';
        const updatedItem = { ...item, favorite: newFavoriteStatus };
        
        // Update local state immediately
        setLocalItems(prevItems => 
            prevItems.map(i => i.url === item.url ? updatedItem : i)
        );

        // Call the parent's onFavorite function
        onFavorite(updatedItem);
    };

    console.log(`Items in CategoryDetails for ${category}:`, localItems);

    return (
        <Box className="category-details" sx={{ padding: 2 }}>
            <Typography variant="h6" gutterBottom>
                {category}
            </Typography>
            <List className="category-details-list">
                {localItems.length > 0 ? localItems.map((item) => (
                    <ListItem
                        key={item.url}
                        button
                        onClick={() => onRowClick(item.url)}
                        className={`category-details-item ${selectedRows.includes(item.url) ? 'selected' : ''}`}
                    >
                        <ListItemText
                            primary={
                                <Typography variant="subtitle1">
                                    <a href={item.url} target="_blank" rel="noopener noreferrer">
                                        {item.item_name}
                                    </a>
                                </Typography>
                            }
                            secondary={
                                <>
                                    <Typography variant="body2" color="textSecondary">
                                        Location: {item.location}
                                    </Typography>
                                    <Typography variant="body2" color="textSecondary">
                                        Time Left: {item.time_left}
                                    </Typography>
                                    <Typography variant="body2" color="textSecondary">
                                        Current Bid: {item.current_bid}
                                    </Typography>
                                </>
                            }
                        />
                        <IconButton onClick={(e) => {
                            e.stopPropagation();
                            handleFavorite(item);
                        }}>
                            {item.favorite === 'Y' ? <FavoriteIcon color="error" /> : <FavoriteBorderIcon />}
                        </IconButton>
                    </ListItem>
                )) : (
                    <ListItem>
                        <ListItemText primary="No items found in this category." />
                    </ListItem>
                )}
            </List>
        </Box>
    );
};

export default CategoryDetails;