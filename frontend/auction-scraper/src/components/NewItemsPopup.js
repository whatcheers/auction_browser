import React, { useState, useEffect } from 'react';
import { Badge, IconButton, Popover, List, ListItem, ListItemText, Typography, Button } from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import AddAlertIcon from '@mui/icons-material/AddAlert';

const apiUrl = process.env.REACT_APP_API_URL || 'https://hashbrowns:3002';

const NewItemsPopup = ({ onAddAlertClick }) => {
  const [alerts, setAlerts] = useState([]);
  const [anchorEl, setAnchorEl] = useState(null);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await fetch(`${apiUrl}/api/alerts`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setAlerts(data);
      } catch (err) {
        console.error('Error fetching alerts:', err);
      }
    };

    fetchAlerts();
    const intervalId = setInterval(fetchAlerts, 6 * 60 * 60 * 1000); // Check every 6 hours

    return () => clearInterval(intervalId);
  }, []);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);

  return (
    <>
      <IconButton color="inherit" onClick={handleClick}>
        <Badge badgeContent={alerts.length} color="secondary">
          <NotificationsIcon />
        </Badge>
      </IconButton>
      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <List>
          <ListItem>
            <Typography variant="h6">Alerts</Typography>
            <Button
              startIcon={<AddAlertIcon />}
              onClick={() => {
                onAddAlertClick();
                handleClose();
              }}
            >
              Add Alert
            </Button>
          </ListItem>
          {alerts.length === 0 ? (
            <ListItem>
              <ListItemText primary="No active alerts" />
            </ListItem>
          ) : (
            alerts.map((alert, index) => (
              <ListItem key={index}>
                <ListItemText 
                  primary={alert.keyword}
                  secondary={`Item: ${alert.item_name}`}
                />
              </ListItem>
            ))
          )}
        </List>
      </Popover>
    </>
  );
};

export default NewItemsPopup;