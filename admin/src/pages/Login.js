import React, { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  Link,
  CircularProgress
} from '@mui/material';
import AuthContext from '../contexts/AuthContext';
import { login } from '../services/authService';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login: authLogin } = React.useContext(AuthContext);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const data = await login(email, password);
      authLogin(data.access_token, { id: data.user_id, email });
    } catch (error) {
      setError(error.error || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      noValidate
      sx={{
        width: '100%',
        mt: 1
      }}
    >
      <Typography component="h2" variant="h6" gutterBottom>
        Sign In
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <TextField
        margin="normal"
        required
        fullWidth
        id="email"
        label="Email Address"
        name="email"
        autoComplete="email"
        autoFocus
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      
      <TextField
        margin="normal"
        required
        fullWidth
        name="password"
        label="Password"
        type="password"
        id="password"
        autoComplete="current-password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      
      <Button
        type="submit"
        fullWidth
        variant="contained"
        disabled={loading}
        sx={{ mt: 3, mb: 2 }}
      >
        {loading ? <CircularProgress size={24} /> : 'Sign In'}
      </Button>
      
      <Box sx={{ textAlign: 'center' }}>
        <Link component={RouterLink} to="/register" variant="body2">
          {"Don't have an account? Sign Up"}
        </Link>
      </Box>
    </Box>
  );
};

export default Login;
EOF

# Dashboard page
cat > admin/src/pages/Dashboard.js << 'EOF'
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  CircularProgress,
  Paper
} from '@mui/material';
import {
  ChatBubble as ChatBubbleIcon,
  Person as PersonIcon,
  Message as MessageIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material';
import { getOverviewAnalytics } from '../services/analyticsService';
import { getChatBots } from '../services/chatbotService';
import { getConversations } from '../services/conversationService';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend);

const Dashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [chatbots, setChatbots] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [analyticsData, chatbotsData, conversationsData] = await Promise.all([
          getOverviewAnalytics(),
          getChatBots(),
          getConversations({ page: 1, per_page: 5 })
        ]);
        
        setAnalytics(analyticsData);
        setChatbots(chatbotsData);
        setConversations(conversationsData.items);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
  // Prepare chart data
  const chartData = {
    labels: analytics?.daily_trend.map(day => day.date) || [],
    datasets: [
      {
        label: 'Conversations',
        data: analytics?.daily_trend.map(day => day.conversations) || [],
        borderColor: '#0088CC',
        backgroundColor: 'rgba(0, 136, 204, 0.1)',
        fill: true,
      }
    ]
  };
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  return (
    <Box>
      {/* Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <ChatBubbleIcon sx={{ color: 'primary.main', mr: 1 }} />
                <Typography variant="h6" component="div">
                  Chatbots
                </Typography>
              </Box>
              <Typography variant="h4" component="div">
                {chatbots.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <MessageIcon sx={{ color: 'primary.main', mr: 1 }} />
                <Typography variant="h6" component="div">
                  Conversations
                </Typography>
              </Box>
              <Typography variant="h4" component="div">
                {analytics?.total_conversations || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <PersonIcon sx={{ color: 'primary.main', mr: 1 }} />
                <Typography variant="h6" component="div">
                  Leads
                </Typography>
              </Box>
              <Typography variant="h4" component="div">
                {analytics?.lead_count || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUpIcon sx={{ color: 'primary.main', mr: 1 }} />
                <Typography variant="h6" component="div">
                  Conversion Rate
                </Typography>
              </Box>
              <Typography variant="h4" component="div">
                {((analytics?.lead_conversion_rate || 0) * 100).toFixed(1)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Chart */}
      <Paper sx={{ p: 2, mb: 4 }}>
        <Typography variant="h6" component="div" sx={{ mb: 2 }}>
          Conversation Trend
        </Typography>
        <Box sx={{ height: 300 }}>
          <Line 
            data={chartData} 
            options={{
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  beginAtZero: true
                }
              }
            }} 
          />
        </Box>
      </Paper>
      
      {/* Quick Actions */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Button 
            variant="contained" 
            fullWidth 
            onClick={() => navigate('/chatbots')}
            sx={{ height: '100%', py: 2 }}
          >
            Manage Chatbots
          </Button>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Button 
            variant="contained" 
            fullWidth 
            onClick={() => navigate('/conversations')}
            sx={{ height: '100%', py: 2 }}
          >
            View Conversations
          </Button>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Button 
            variant="contained" 
            fullWidth 
            onClick={() => navigate('/leads')}
            sx={{ height: '100%', py: 2 }}
          >
            Manage Leads
          </Button>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Button 
            variant="contained" 
            fullWidth 
            onClick={() => navigate('/analytics')}
            sx={{ height: '100%', py: 2 }}
          >
            Analytics
          </Button>
        </Grid>
      </Grid>
      
      {/* Recent Conversations */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" component="div" sx={{ mb: 2 }}>
          Recent Conversations
        </Typography>
        
        {conversations.length > 0 ? (
          <Box sx={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #ddd' }}>ID</th>
                  <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #ddd' }}>Started</th>
                  <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #ddd' }}>Status</th>
                  <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #ddd' }}>Source</th>
                  <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #ddd' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {conversations.map((conversation) => (
                  <tr key={conversation.id}>
                    <td style={{ padding: '8px', borderBottom: '1px solid #ddd' }}>{conversation.id}</td>
                    <td style={{ padding: '8px', borderBottom: '1px solid #ddd' }}>
                      {new Date(conversation.started_at).toLocaleString()}
                    </td>
                    <td style={{ padding: '8px', borderBottom: '1px solid #ddd' }}>
                      <span style={{
                        backgroundColor: conversation.status === 'active' ? '#e3f2fd' : '#f1f8e9',
                        color: conversation.status === 'active' ? '#0277bd' : '#558b2f',
                        padding: '3px 8px',
                        borderRadius: '4px',
                        fontSize: '0.8rem'
                      }}>
                        {conversation.status}
                      </span>
                    </td>
                    <td style={{ padding: '8px', borderBottom: '1px solid #ddd' }}>
                      {conversation.utm_source || 'Direct'}
                    </td>
                    <td style={{ padding: '8px', borderBottom: '1px solid #ddd' }}>
                      <Button 
                        variant="outlined" 
                        size="small" 
                        onClick={() => navigate(`/conversations/${conversation.id}`)}
                      >
                        View
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Box>
        ) : (
          <Typography variant="body2" color="text.secondary">
            No conversations yet.
          </Typography>
        )}
        
        <Box sx={{ mt: 2, textAlign: 'right' }}>
          <Button 
            variant="text" 
            onClick={() => navigate('/conversations')}
          >
            View All
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default Dashboard;
