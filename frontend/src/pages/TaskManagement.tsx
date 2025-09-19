import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow as PlayIcon,
  Visibility as ViewIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { apiService } from '../services/apiService';

interface Task {
  task_id: string;
  name: string;
  description: string;
  task_type: string;
  status: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  result?: any;
  error?: string;
}

const TaskManagement: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  
  // Form state
  const [newTask, setNewTask] = useState({
    name: '',
    description: '',
    task_type: 'code_generation',
    parameters: '{}'
  });

  const taskTypes = [
    { value: 'code_generation', label: 'Code Generation' },
    { value: 'code_review', label: 'Code Review' },
    { value: 'github_automation', label: 'GitHub Automation' },
    { value: 'dependency_audit', label: 'Dependency Audit' }
  ];

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const response = await apiService.listTasks();
      setTasks(response.tasks || []);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async () => {
    try {
      let parameters;
      try {
        parameters = JSON.parse(newTask.parameters);
      } catch (e) {
        setError('Invalid JSON in parameters');
        return;
      }

      const response = await apiService.createTask({
        name: newTask.name,
        description: newTask.description,
        task_type: newTask.task_type,
        parameters
      });

      setCreateDialogOpen(false);
      setNewTask({
        name: '',
        description: '',
        task_type: 'code_generation',
        parameters: '{}'
      });
      loadTasks();
    } catch (err: any) {
      setError(err.message || 'Failed to create task');
    }
  };

  const handleExecuteTask = async (taskId: string) => {
    try {
      await apiService.executeTask(taskId);
      // Refresh tasks after a short delay to see the status change
      setTimeout(loadTasks, 1000);
    } catch (err: any) {
      setError(err.message || 'Failed to execute task');
    }
  };

  const handleViewTask = (task: Task) => {
    setSelectedTask(task);
    setViewDialogOpen(true);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'running':
        return 'warning';
      case 'pending':
        return 'info';
      default:
        return 'default';
    }
  };

  const getExampleParameters = (taskType: string) => {
    switch (taskType) {
      case 'code_generation':
        return JSON.stringify({
          prompt: "Create a Python function to sort a list",
          language: "python"
        }, null, 2);
      case 'code_review':
        return JSON.stringify({
          code: "def hello(): print('Hello World')",
          analysis_type: "review"
        }, null, 2);
      case 'github_automation':
        return JSON.stringify({
          action_type: "create_pull_request",
          repository: "user/repo",
          branch: "feature-branch"
        }, null, 2);
      case 'dependency_audit':
        return JSON.stringify({
          audit_type: "npm",
          project_path: "./frontend"
        }, null, 2);
      default:
        return '{}';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Task Management
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadTasks}
            disabled={loading}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Create Task
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} sx={{ textAlign: 'center', py: 4 }}>
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : tasks.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} sx={{ textAlign: 'center', py: 4 }}>
                    No tasks found. Create your first task to get started.
                  </TableCell>
                </TableRow>
              ) : (
                tasks.map((task) => (
                  <TableRow key={task.task_id}>
                    <TableCell>
                      <Typography variant="subtitle2">{task.name}</Typography>
                      <Typography variant="caption" color="textSecondary">
                        {task.description}
                      </Typography>
                    </TableCell>
                    <TableCell>{task.task_type}</TableCell>
                    <TableCell>
                      <Chip
                        label={task.status}
                        color={getStatusColor(task.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {new Date(task.created_at).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => handleViewTask(task)}
                        title="View Details"
                      >
                        <ViewIcon />
                      </IconButton>
                      {task.status === 'pending' && (
                        <IconButton
                          size="small"
                          onClick={() => handleExecuteTask(task.task_id)}
                          title="Execute Task"
                          color="primary"
                        >
                          <PlayIcon />
                        </IconButton>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Create Task Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Create New Task</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Task Name"
                value={newTask.name}
                onChange={(e) => setNewTask({ ...newTask, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Description"
                value={newTask.description}
                onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Task Type</InputLabel>
                <Select
                  value={newTask.task_type}
                  label="Task Type"
                  onChange={(e) => {
                    const taskType = e.target.value;
                    setNewTask({
                      ...newTask,
                      task_type: taskType,
                      parameters: getExampleParameters(taskType)
                    });
                  }}
                >
                  {taskTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={6}
                label="Parameters (JSON)"
                value={newTask.parameters}
                onChange={(e) => setNewTask({ ...newTask, parameters: e.target.value })}
                helperText="Enter task parameters as JSON"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateTask}
            variant="contained"
            disabled={!newTask.name.trim()}
          >
            Create Task
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Task Dialog */}
      <Dialog
        open={viewDialogOpen}
        onClose={() => setViewDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Task Details</DialogTitle>
        <DialogContent>
          {selectedTask && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={6}>
                <Typography variant="subtitle2">Task ID:</Typography>
                <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                  {selectedTask.task_id}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle2">Status:</Typography>
                <Chip
                  label={selectedTask.status}
                  color={getStatusColor(selectedTask.status) as any}
                  size="small"
                />
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2">Description:</Typography>
                <Typography variant="body2">{selectedTask.description}</Typography>
              </Grid>
              {selectedTask.result && (
                <Grid item xs={12}>
                  <Typography variant="subtitle2">Result:</Typography>
                  <Box sx={{ bgcolor: 'grey.100', p: 2, borderRadius: 1, mt: 1 }}>
                    <pre style={{ whiteSpace: 'pre-wrap', margin: 0, fontSize: '0.875rem' }}>
                      {JSON.stringify(selectedTask.result, null, 2)}
                    </pre>
                  </Box>
                </Grid>
              )}
              {selectedTask.error && (
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="error">Error:</Typography>
                  <Typography variant="body2" color="error">
                    {selectedTask.error}
                  </Typography>
                </Grid>
              )}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TaskManagement;