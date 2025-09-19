import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Box, 
  Tabs, 
  Tab, 
  Paper 
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Code as CodeIcon,
  Assignment as TaskIcon,
  Security as SecurityIcon
} from '@mui/icons-material';

const Navigation: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const getTabValue = () => {
    switch (location.pathname) {
      case '/':
        return 0;
      case '/codex':
        return 1;
      case '/tasks':
        return 2;
      case '/audit':
        return 3;
      default:
        return 0;
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    const routes = ['/', '/codex', '/tasks', '/audit'];
    navigate(routes[newValue]);
  };

  return (
    <Paper elevation={1} sx={{ borderRadius: 0 }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs 
          value={getTabValue()} 
          onChange={handleTabChange}
          variant="fullWidth"
          aria-label="navigation tabs"
        >
          <Tab 
            icon={<DashboardIcon />} 
            label="Dashboard" 
            id="tab-0"
            aria-controls="tabpanel-0"
          />
          <Tab 
            icon={<CodeIcon />} 
            label="Codex Trigger" 
            id="tab-1"
            aria-controls="tabpanel-1"
          />
          <Tab 
            icon={<TaskIcon />} 
            label="Task Management" 
            id="tab-2"
            aria-controls="tabpanel-2"
          />
          <Tab 
            icon={<SecurityIcon />} 
            label="Dependency Audit" 
            id="tab-3"
            aria-controls="tabpanel-3"
          />
        </Tabs>
      </Box>
    </Paper>
  );
};

export default Navigation;