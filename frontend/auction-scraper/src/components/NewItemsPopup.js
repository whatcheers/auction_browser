import React, { useState, useEffect } from 'react';
import { IconButton, Badge, Popover, List, ListItem, ListItemText, Button, Typography, CircularProgress } from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import AddAlertIcon from '@mui/icons-material/AddAlert';
import DeleteIcon from '@mui/icons-material/Delete';

const apiUrl = process.env.REACT_APP_API_URL || 'https://hashbrowns:3002';

const NewItemsPopup = ({ onAlertClick, onAddAlertClick, startDate, endDate }) => {
  const [alerts, setAlerts] = useState([]);
  const [anchorEl, setAnchorEl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    fetchAlerts();
  }, []);

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
      setMessage('Error fetching alerts. Please try again.');
    }
  };

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
    setIsOpen(true);
  };

  const handleClose = () => {
    setAnchorEl(null);
    setMessage('');
    setIsOpen(false);
  };

  const handleAlertClick = async (keyword) => {
    setLoading(true);
    setMessage('');
    try {
      const currentDate = new Date();
      const startDate = currentDate.toISOString().split('T')[0];
      const endDate = new Date(currentDate.setDate(currentDate.getDate() + 90)).toISOString().split('T')[0];
      
      const response = await fetch(`${apiUrl}/api/get-auction-data?tableName=all_tables&startDate=${startDate}&endDate=${endDate}&searchTerm=${encodeURIComponent(keyword)}`);
      
      if (response.status === 404) {
        setMessage(`No items found for "${keyword}" in the next 90 days.`);
        onAlertClick([], keyword);
      } else if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      } else {
        const data = await response.json();
        onAlertClick(data, keyword);
        handleClose();
      }
    } catch (err) {
      console.error('Error fetching new items for alert:', err);
      setMessage(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAlert = async (id, event) => {
    event.stopPropagation();
    try {
      const response = await fetch(`${apiUrl}/api/alerts/${id}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        fetchAlerts();
      } else {
        console.error('Failed to delete alert');
        setMessage('Failed to delete alert. Please try again.');
      }
    } catch (error) {
      console.error('Error deleting alert:', error);
      setMessage('Error deleting alert. Please try again.');
    }
  };

  return (
    <>
      <IconButton color="inherit" onClick={handleClick}>
        <Badge badgeContent={isOpen ? 0 : alerts.length} color="secondary">
          <NotificationsIcon />
        </Badge>
      </IconButton>
      <Popover
        open={Boolean(anchorEl)}
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
          {loading && (
            <ListItem>
              <CircularProgress size={24} />
            </ListItem>
          )}
          {message && (
            <ListItem>
              <Typography color="error">{message}</Typography>
            </ListItem>
          )}
          {alerts.map((alert) => (
            <ListItem key={alert.id} button onClick={() => handleAlertClick(alert.keyword)}>
              <ListItemText 
                primary={alert.keyword}
                secondary={`Item: ${alert.item_name}`}
              />
              <IconButton onClick={(event) => handleDeleteAlert(alert.id, event)}>
                <DeleteIcon />
              </IconButton>
            </ListItem>
          ))}
        </List>
      </Popover>
    </>
  );
};

export default NewItemsPopup;
