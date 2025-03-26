import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { Box, Paper, Typography, Container } from '@mui/material';
import AuthContext from '../contexts/AuthContext';

const AuthLayout = () => {
  const { isAuthenticated } = React.useContext(AuthContext);
  
  // If already authenticated, redirect to dashboard
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#f5f8fb',
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={3}
          sx={{
            padding: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <Typography component="h1" variant="h4" gutterBottom>
            CLAI Chat
          </Typography>
          
          <Outlet />
        </Paper>
      </Container>
    </Box>
  );
};

export default AuthLayout;
