import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Authentication
import AuthContext from './contexts/AuthContext';
import { getStoredToken, isTokenValid } from './utils/auth';

// Layouts
import DashboardLayout from './layouts/DashboardLayout';
import AuthLayout from './layouts/AuthLayout';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Organizations from './pages/Organizations';
import ChatBots from './pages/ChatBots';
import ChatBotDetail from './pages/ChatBotDetail';
import Conversations from './pages/Conversations';
import ConversationDetail from './pages/ConversationDetail';
import Leads from './pages/Leads';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';

const theme = createTheme({
  palette: {
    primary: {
      main: '#0088CC',
    },
    secondary: {
      main: '#19857b',
    },
    background: {
      default: '#f5f8fb',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
});

// Protected route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = React.useContext(AuthContext);
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const token = getStoredToken();
    if (token && isTokenValid(token)) {
      setIsAuthenticated(true);
      // Set user from token claims
      setUser(JSON.parse(atob(token.split('.')[1])));
    }
    setLoading(false);
  }, []);
  
  const authContextValue = {
    isAuthenticated,
    user,
    login: (token, user) => {
      localStorage.setItem('auth_token', token);
      setIsAuthenticated(true);
      setUser(user);
    },
    logout: () => {
      localStorage.removeItem('auth_token');
      setIsAuthenticated(false);
      setUser(null);
    }
  };
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthContext.Provider value={authContextValue}>
        <Router>
          <Routes>
            {/* Auth routes */}
            <Route element={<AuthLayout />}>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
            </Route>
            
            {/* Dashboard routes */}
            <Route element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }>
              <Route path="/" element={<Dashboard />} />
              <Route path="/organizations" element={<Organizations />} />
              <Route path="/chatbots" element={<ChatBots />} />
              <Route path="/chatbots/:id" element={<ChatBotDetail />} />
              <Route path="/conversations" element={<Conversations />} />
              <Route path="/conversations/:id" element={<ConversationDetail />} />
              <Route path="/leads" element={<Leads />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/settings" element={<Settings />} />
            </Route>
            
            {/* 404 route */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Router>
      </AuthContext.Provider>
    </ThemeProvider>
  );
};

