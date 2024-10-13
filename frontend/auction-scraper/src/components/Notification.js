import React, { useState, useEffect } from 'react';
import { IconButton, Badge, Menu, MenuItem, Typography, Button, TextField } from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import CloseIcon from '@mui/icons-material/Close';

const apiUrl = process.env.REACT_APP_API_URL || 'https://hashbrowns:3002';

const Notification = () => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [newKeyword, setNewKeyword] = useState('');
  const [newItemName, setNewItemName] = useState('');

  useEffect(() => {
    const fetchNewAlerts = async () => {
      try {
        const response = await fetch(`${apiUrl}/api/alerts/new`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setNotifications(data);
      } catch (err) {
        console.error('Error fetching alerts:', err);
      }
    };

    fetchNewAlerts();
    const intervalId = setInterval(fetchNewAlerts, 60000); // Fetch every 60 seconds

    return () => clearInterval(intervalId);
  }, []);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleDismiss = async (id) => {
    try {
      const response = await fetch(`${apiUrl}/api/alerts/${id}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        setNotifications((prev) => prev.filter((notification) => notification.id !== id));
      } else {
        console.error('Failed to dismiss alert');
      }
    } catch (error) {
      console.error('Error dismissing alert:', error);
    }
  };

  const handleAddAlert = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/alerts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ keyword: newKeyword, item: { name: newItemName } }),
      });
      if (response.ok) {
        setNewKeyword('');
        setNewItemName('');
        fetchNewAlerts(); // Refresh alerts
      } else {
        console.error('Failed to add alert');
      }
    } catch (error) {
      console.error('Error adding alert:', error);
    }
  };

  return (
    <>
      <IconButton color="inherit" onClick={handleClick}>
        <Badge badgeContent={notifications.length} color="secondary">
          <NotificationsIcon />
        </Badge>
      </IconButton>
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >
        <MenuItem>
          <TextField
            label="Keyword"
            value={newKeyword}
            onChange={(e) => setNewKeyword(e.target.value)}
            size="small"
          />
          <TextField
            label="Item Name"
            value={newItemName}
            onChange={(e) => setNewItemName(e.target.value)}
            size="small"
          />
          <Button onClick={handleAddAlert}>Add Alert</Button>
        </MenuItem>
        {notifications.length === 0 ? (
          <MenuItem onClick={handleClose}>No new notifications</MenuItem>
        ) : (
          notifications.map((notification, index) => (
            <MenuItem key={index}>
              <Typography variant="body2">
                New item: <a href={notification.url} target="_blank" rel="noopener noreferrer">{notification.item_name}</a>
              </Typography>
              <IconButton size="small" onClick={() => handleDismiss(notification.id)}>
                <CloseIcon fontSize="small" />
              </IconButton>
            </MenuItem>
          ))
        )}
      </Menu>
    </>
  );
};

export default Notification;
