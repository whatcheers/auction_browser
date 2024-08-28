import React from 'react';
import { Button as MuiButton } from '@mui/material';

const Button = ({ children, onClick, disabled, ...props }) => {
  const handleClick = () => {
    console.debug('Button clicked');
    onClick();
  };

  console.debug('Rendering Button with disabled state:', disabled);

  return (
    <MuiButton
      variant="contained"
      color="primary"
      onClick={handleClick}
      disabled={disabled}
      className={`custom-button ${disabled ? 'disabled' : ''}`}
      {...props}
    >
      {children}
    </MuiButton>
  );
};

export default Button;
