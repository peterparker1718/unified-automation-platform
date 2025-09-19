import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Container, AppBar, Toolbar, Typography, Box } from '@mui/material';
import Dashboard from './pages/Dashboard';
import CodexTrigger from './pages/CodexTrigger';
import TaskManagement from './pages/TaskManagement';
import DependencyAudit from './pages/DependencyAudit';
import Navigation from './components/Navigation';

function App() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Unified Automation Platform
          </Typography>
        </Toolbar>
      </AppBar>
      
      <Navigation />
      
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/codex" element={<CodexTrigger />} />
          <Route path="/tasks" element={<TaskManagement />} />
          <Route path="/audit" element={<DependencyAudit />} />
        </Routes>
      </Container>
    </Box>
  );
}

export default App;