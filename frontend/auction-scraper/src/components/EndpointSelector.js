import React from 'react';
import { Select, MenuItem, FormControl, InputLabel } from '@mui/material';

const EndpointSelector = ({ selectedEndpoint, onEndpointChange }) => {
  const endpoints = [
    { name: 'Ending Today', value: 'ending_today' },
    { name: 'All Tables', value: 'all_tables' },
    { name: 'Backes', value: 'backes' },
    { name: 'Bidspotter', value: 'bidspotter' },
    { name: 'GovDeals', value: 'govdeals' },
    { name: 'GSA', value: 'gsa' },
    { name: 'Public Surplus', value: 'publicsurplus' },
    { name: 'SMC', value: 'smc' },
    { name: 'Proxibid', value: 'proxibid' },
    { name: 'Wisco Surplus Auctions', value: 'wiscosurp_auctions' },
    { name: 'HiBid', value: 'hibid' },
    { name: 'Heartland', value: 'heartland' },
  ];

  return (
    <FormControl variant="outlined" size="small" style={{ width: '200px', marginRight: '20px' }}>
      <InputLabel>Endpoint</InputLabel>
      <Select
        value={selectedEndpoint}
        onChange={(event) => onEndpointChange(event.target.value)}
        label="Endpoint"
      >
        {endpoints.map((endpoint) => (
          <MenuItem key={endpoint.value} value={endpoint.value}>
            {endpoint.name}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export default EndpointSelector;