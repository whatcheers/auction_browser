import React, { useState, useEffect } from 'react';
import { IconButton, Badge, Menu, MenuItem, Typography } from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';

const apiUrl = process.env.REACT_APP_API_URL || 'https://hashbrowns:3002';

const Notification = () => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    const fetchLatestAlerts = async () => {
      try {
        const response = await fetch(`${apiUrl}/api/alerts/latest`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setNotifications(data);
      } catch (err) {
        console.error('Error fetching latest alerts:', err);
      }
    };

    const intervalId = setInterval(fetchLatestAlerts, 60000); // Fetch every 60 seconds

    return () => clearInterval(intervalId);
  }, []);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
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
        {notifications.length === 0 ? (
          <MenuItem onClick={handleClose}>No new notifications</MenuItem>
        ) : (
          notifications.map((notification, index) => (
            <MenuItem key={index} onClick={handleClose}>
              <Typography variant="body2">
                New item added: {notification.item_name}
              </Typography>
            </MenuItem>
          ))
        )}
      </Menu>
    </>
  );
};

export default Notification;
