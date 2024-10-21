import React, { useState, useEffect } from 'react';
import { IconButton, Badge, Popover, List, ListItem, ListItemText, Button, Typography, CircularProgress, TextField } from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import AddAlertIcon from '@mui/icons-material/AddAlert';
import DeleteIcon from '@mui/icons-material/Delete';

const apiUrl = process.env.REACT_APP_API_URL || 'https://hashbrowns:3002';

const AlertManager = ({ onAlertClick }) => {
  const [alerts, setAlerts] = useState([]);
  const [anchorEl, setAnchorEl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [newItemName, setNewItemName] = useState('');

  useEffect(() => {
    fetchAlerts();
    const intervalId = setInterval(fetchAlerts, 60000); // Fetch every 60 seconds
    return () => clearInterval(intervalId);
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

  const handleAddAlert = async () => {
    if (!newItemName) {
      setMessage('Item Name is required.');
      return;
    }
    try {
      const response = await fetch(`${apiUrl}/api/alerts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ item: { name: newItemName } }),
      });
      if (response.ok) {
        setNewItemName('');
        fetchAlerts();
      } else {
        throw new Error('Failed to add alert');
      }
    } catch (error) {
      console.error('Error adding alert:', error);
      setMessage('Failed to add alert. Please try again.');
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
        throw new Error('Failed to delete alert');
      }
    } catch (error) {
      console.error('Error deleting alert:', error);
      setMessage('Failed to delete alert. Please try again.');
    }
  };

  const handleAlertClick = async (itemName) => {
    setLoading(true);
    setMessage('');
    try {
      const currentDate = new Date();
      const startDate = currentDate.toISOString().split('T')[0];
      const endDate = new Date(currentDate.setDate(currentDate.getDate() + 90)).toISOString().split('T')[0];
      
      const response = await fetch(`${apiUrl}/api/get-auction-data?tableName=all_tables&startDate=${startDate}&endDate=${endDate}&searchTerm=${encodeURIComponent(itemName)}`);
      
      if (response.status === 404) {
        setMessage(`No items found for "${itemName}" in the next 90 days.`);
        onAlertClick([], itemName);
      } else if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      } else {
        const data = await response.json();
        onAlertClick(data, itemName);
        handleClose();
      }
    } catch (err) {
      console.error('Error fetching new items for alert:', err);
      setMessage(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
    setMessage('');
  };

  return (
    <>
      <IconButton color="inherit" onClick={handleClick}>
        <Badge badgeContent={alerts.length} color="secondary">
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
          </ListItem>
          <ListItem>
            <TextField
              label="Item Name"
              value={newItemName}
              onChange={(e) => setNewItemName(e.target.value)}
              size="small"
            />
            <Button startIcon={<AddAlertIcon />} onClick={handleAddAlert}>
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
            <ListItem key={alert.id} button onClick={() => handleAlertClick(alert.item_name)}>
              <ListItemText primary={alert.item_name} />
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

export default AlertManager;
