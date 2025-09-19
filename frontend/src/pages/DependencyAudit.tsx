import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Card,
  CardContent,
  CardActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress
} from '@mui/material';
import {
  Security as SecurityIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  PlayArrow as PlayIcon,
  ExpandMore as ExpandMoreIcon,
  FolderOpen as FolderIcon
} from '@mui/icons-material';

interface VulnerabilityReport {
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  package: string;
  version: string;
  description: string;
  fixedIn?: string;
}

interface AuditResult {
  auditType: string;
  projectPath: string;
  vulnerabilities: VulnerabilityReport[];
  totalPackages: number;
  lastScanned: string;
}

const DependencyAudit: React.FC = () => {
  const [auditType, setAuditType] = useState('npm');
  const [projectPath, setProjectPath] = useState('./');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [auditResults, setAuditResults] = useState<AuditResult[]>([]);

  // Mock vulnerability data for demonstration
  const mockVulnerabilities: VulnerabilityReport[] = [
    {
      type: 'npm',
      severity: 'high',
      package: 'lodash',
      version: '4.17.20',
      description: 'Prototype pollution vulnerability',
      fixedIn: '4.17.21'
    },
    {
      type: 'npm',
      severity: 'medium',
      package: 'axios',
      version: '0.21.1',
      description: 'Server-Side Request Forgery vulnerability',
      fixedIn: '0.21.2'
    },
    {
      type: 'pip',
      severity: 'critical',
      package: 'pillow',
      version: '8.0.0',
      description: 'Buffer overflow in JPEG decoder',
      fixedIn: '8.1.1'
    }
  ];

  const auditTypes = [
    { value: 'npm', label: 'NPM (Node.js)', description: 'Scan package.json and package-lock.json' },
    { value: 'pip', label: 'PyPI (Python)', description: 'Scan requirements.txt and setup.py' },
    { value: 'dockerfile', label: 'Dockerfile', description: 'Scan Docker images for vulnerabilities' },
    { value: 'all', label: 'All Types', description: 'Comprehensive scan of all dependency types' }
  ];

  const handleRunAudit = async () => {
    try {
      setLoading(true);
      setError(null);

      // Simulate API call with mock data
      await new Promise(resolve => setTimeout(resolve, 2000));

      const mockResult: AuditResult = {
        auditType,
        projectPath,
        vulnerabilities: mockVulnerabilities.filter(v => 
          auditType === 'all' || v.type === auditType
        ),
        totalPackages: auditType === 'npm' ? 156 : auditType === 'pip' ? 42 : 200,
        lastScanned: new Date().toISOString()
      };

      setAuditResults([mockResult, ...auditResults]);
    } catch (err: any) {
      setError(err.message || 'Failed to run security audit');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return <ErrorIcon color="error" />;
      case 'medium':
        return <WarningIcon color="warning" />;
      case 'low':
        return <CheckCircleIcon color="info" />;
      default:
        return <SecurityIcon />;
    }
  };

  const getSeverityCount = (result: AuditResult, severity: string) => {
    return result.vulnerabilities.filter(v => v.severity === severity).length;
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dependency Security Audit
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Scan your project dependencies for known security vulnerabilities across NPM, PyPI, and Docker images.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Audit Configuration */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Scan Configuration
            </Typography>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Audit Type</InputLabel>
              <Select
                value={auditType}
                label="Audit Type"
                onChange={(e) => setAuditType(e.target.value)}
              >
                {auditTypes.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Project Path"
              value={projectPath}
              onChange={(e) => setProjectPath(e.target.value)}
              sx={{ mb: 2 }}
              InputProps={{
                startAdornment: <FolderIcon sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />

            <Button
              fullWidth
              variant="contained"
              startIcon={loading ? <CircularProgress size={20} /> : <PlayIcon />}
              onClick={handleRunAudit}
              disabled={loading}
            >
              {loading ? 'Scanning...' : 'Run Security Audit'}
            </Button>

            {/* Audit Type Information */}
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                Scan Types
              </Typography>
              {auditTypes.map((type) => (
                <Card 
                  key={type.value} 
                  variant="outlined" 
                  sx={{ 
                    mb: 1, 
                    bgcolor: auditType === type.value ? 'primary.50' : 'inherit',
                    cursor: 'pointer'
                  }}
                  onClick={() => setAuditType(type.value)}
                >
                  <CardContent sx={{ py: 1 }}>
                    <Typography variant="subtitle2">{type.label}</Typography>
                    <Typography variant="caption" color="textSecondary">
                      {type.description}
                    </Typography>
                  </CardContent>
                </Card>
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* Audit Results */}
        <Grid item xs={12} md={8}>
          {auditResults.length === 0 ? (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <SecurityIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="textSecondary">
                No audit results yet
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Run your first security audit to see vulnerability reports here.
              </Typography>
            </Paper>
          ) : (
            <Box>
              {auditResults.map((result, index) => (
                <Paper key={index} sx={{ p: 3, mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Box>
                      <Typography variant="h6">
                        {auditTypes.find(t => t.value === result.auditType)?.label} Audit
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Path: {result.projectPath} • Scanned: {new Date(result.lastScanned).toLocaleString()}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="textSecondary">
                      {result.totalPackages} packages scanned
                    </Typography>
                  </Box>

                  {/* Severity Summary */}
                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    {['critical', 'high', 'medium', 'low'].map((severity) => {
                      const count = getSeverityCount(result, severity);
                      return (
                        <Grid item xs={3} key={severity}>
                          <Card variant="outlined">
                            <CardContent sx={{ textAlign: 'center', py: 1 }}>
                              {getSeverityIcon(severity)}
                              <Typography variant="h6">{count}</Typography>
                              <Typography variant="caption" sx={{ textTransform: 'capitalize' }}>
                                {severity}
                              </Typography>
                            </CardContent>
                          </Card>
                        </Grid>
                      );
                    })}
                  </Grid>

                  {/* Vulnerability Details */}
                  {result.vulnerabilities.length > 0 ? (
                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography variant="subtitle1">
                          Vulnerability Details ({result.vulnerabilities.length} found)
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List>
                          {result.vulnerabilities.map((vuln, vIndex) => (
                            <ListItem key={vIndex} divider>
                              <ListItemIcon>
                                {getSeverityIcon(vuln.severity)}
                              </ListItemIcon>
                              <ListItemText
                                primary={
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <Typography variant="subtitle2">
                                      {vuln.package}@{vuln.version}
                                    </Typography>
                                    <Chip
                                      label={vuln.severity}
                                      color={getSeverityColor(vuln.severity) as any}
                                      size="small"
                                    />
                                  </Box>
                                }
                                secondary={
                                  <Box>
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      {vuln.description}
                                    </Typography>
                                    {vuln.fixedIn && (
                                      <Typography variant="caption" color="success.main">
                                        Fixed in version: {vuln.fixedIn}
                                      </Typography>
                                    )}
                                  </Box>
                                }
                              />
                            </ListItem>
                          ))}
                        </List>
                      </AccordionDetails>
                    </Accordion>
                  ) : (
                    <Alert severity="success">
                      <Typography variant="subtitle2">No vulnerabilities found!</Typography>
                      <Typography variant="body2">
                        All scanned dependencies appear to be secure.
                      </Typography>
                    </Alert>
                  )}
                </Paper>
              ))}
            </Box>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default DependencyAudit;