import React, { useState } from 'react';
import { Box, TextField, Button, Typography, Dialog, DialogActions, DialogContent, DialogTitle } from '@mui/material';

const apiUrl = process.env.REACT_APP_API_URL || 'https://hashbrowns:3002';

const AddAlert = ({ open, onClose }) => {
  const [itemName, setItemName] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [message, setMessage] = useState('');
  const [confirm, setConfirm] = useState(false);

  const handleSearch = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/alerts/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ item_name: itemName }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setSearchResults(data);
      setConfirm(true);
    } catch (err) {
      console.error('Error searching for item:', err);
      setMessage('Failed to search for item');
    }
  };

  const handleSubmit = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/alerts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ keyword: itemName, item: { name: itemName } }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setMessage(`Alert added: ${data.item_name}`);
      setItemName('');
      setSearchResults([]);
      setConfirm(false);
      onClose(); // Close the dialog after successful addition
    } catch (err) {
      console.error('Error adding alert:', err);
      setMessage('Failed to add alert');
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Add New Alert</DialogTitle>
      <DialogContent>
        <Box component="form" onSubmit={(e) => { e.preventDefault(); handleSearch(); }}>
          <TextField
            label="Item Name"
            value={itemName}
            onChange={(e) => setItemName(e.target.value)}
            required
            fullWidth
            margin="normal"
          />
          {message && <Typography variant="body2" color="error">{message}</Typography>}
        </Box>
        {confirm && (
          <Box>
            <Typography variant="body2">Found {searchResults.length} items:</Typography>
            {searchResults.map((result, index) => (
              <Typography key={index} variant="body2">{result.item_name}</Typography>
            ))}
            <Typography variant="body2">Do you want to add this alert?</Typography>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">Cancel</Button>
        {confirm ? (
          <Button onClick={handleSubmit} variant="contained" color="primary">Confirm</Button>
        ) : (
          <Button onClick={handleSearch} variant="contained" color="primary">Search</Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default AddAlert;
