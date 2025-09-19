import React, { useState } from 'react';
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
  Card,
  CardContent,
  CardActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress
} from '@mui/material';
import { ExpandMore as ExpandMoreIcon, Code as CodeIcon, PlayArrow as PlayIcon } from '@mui/icons-material';
import Editor from '@monaco-editor/react';
import { apiService } from '../services/apiService';

interface GeneratedCode {
  code: string;
  language: string;
  prompt: string;
}

const CodexTrigger: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [language, setLanguage] = useState('python');
  const [maxTokens, setMaxTokens] = useState(2000);
  const [generatedCode, setGeneratedCode] = useState<GeneratedCode | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [analyzingCode, setAnalyzingCode] = useState(false);

  const handleGenerateCode = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.generateCode({
        prompt: prompt.trim(),
        language,
        max_tokens: maxTokens
      });

      setGeneratedCode({
        code: response.generated_code,
        language: response.language,
        prompt: response.prompt
      });
    } catch (err: any) {
      setError(err.message || 'Failed to generate code');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeCode = async () => {
    if (!generatedCode?.code) {
      setError('No code to analyze');
      return;
    }

    try {
      setAnalyzingCode(true);
      setError(null);

      const response = await apiService.analyzeCode({
        code: generatedCode.code,
        analysis_type: 'review'
      });

      setAnalysisResult(response.analysis);
    } catch (err: any) {
      setError(err.message || 'Failed to analyze code');
    } finally {
      setAnalyzingCode(false);
    }
  };

  const handleClearAll = () => {
    setPrompt('');
    setGeneratedCode(null);
    setAnalysisResult(null);
    setError(null);
  };

  const supportedLanguages = [
    'python',
    'javascript',
    'typescript',
    'java',
    'cpp',
    'csharp',
    'go',
    'rust',
    'sql',
    'html',
    'css'
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Codex Trigger Interface
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Generate code using OpenAI Codex. Enter your requirements and get AI-generated code instantly.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Input Section */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Code Generation Parameters
            </Typography>

            <Box sx={{ mb: 3 }}>
              <TextField
                fullWidth
                multiline
                rows={6}
                label="Prompt"
                placeholder="Describe what code you want to generate..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                variant="outlined"
              />
            </Box>

            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Language</InputLabel>
                  <Select
                    value={language}
                    label="Language"
                    onChange={(e) => setLanguage(e.target.value)}
                  >
                    {supportedLanguages.map((lang) => (
                      <MenuItem key={lang} value={lang}>
                        {lang.charAt(0).toUpperCase() + lang.slice(1)}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Max Tokens"
                  type="number"
                  value={maxTokens}
                  onChange={(e) => setMaxTokens(parseInt(e.target.value) || 2000)}
                  inputProps={{ min: 100, max: 4000 }}
                />
              </Grid>
            </Grid>

            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <PlayIcon />}
                onClick={handleGenerateCode}
                disabled={loading || !prompt.trim()}
                fullWidth
              >
                {loading ? 'Generating...' : 'Generate Code'}
              </Button>
              
              <Button
                variant="outlined"
                onClick={handleClearAll}
                disabled={loading}
              >
                Clear All
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Output Section */}
        <Grid item xs={12} lg={6}>
          {generatedCode && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Generated Code ({generatedCode.language})
              </Typography>

              <Box sx={{ height: 400, border: 1, borderColor: 'divider', borderRadius: 1, mb: 2 }}>
                <Editor
                  height="100%"
                  defaultLanguage={generatedCode.language}
                  value={generatedCode.code}
                  theme="vs-dark"
                  options={{
                    readOnly: false,
                    minimap: { enabled: false },
                    scrollBeyondLastLine: false,
                    fontSize: 14
                  }}
                />
              </Box>

              <Button
                variant="outlined"
                startIcon={analyzingCode ? <CircularProgress size={20} /> : <CodeIcon />}
                onClick={handleAnalyzeCode}
                disabled={analyzingCode}
                fullWidth
              >
                {analyzingCode ? 'Analyzing...' : 'Analyze Code'}
              </Button>
            </Paper>
          )}
        </Grid>

        {/* Analysis Results */}
        {analysisResult && (
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Code Analysis Results
              </Typography>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>Raw Analysis</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Box sx={{ bgcolor: 'grey.100', p: 2, borderRadius: 1 }}>
                    <pre style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
                      {JSON.stringify(analysisResult, null, 2)}
                    </pre>
                  </Box>
                </AccordionDetails>
              </Accordion>
            </Paper>
          </Grid>
        )}

        {/* Example Prompts */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Example Prompts
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                Try these example prompts to get started:
              </Typography>
              
              <Grid container spacing={2}>
                {[
                  'Create a Python function to calculate Fibonacci numbers',
                  'Write a React component for a todo list',
                  'Generate a SQL query to find top 10 customers by revenue',
                  'Create a Node.js Express API endpoint for user authentication',
                  'Write a Python script to scrape data from a website'
                ].map((example, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Card variant="outlined" sx={{ cursor: 'pointer' }} onClick={() => setPrompt(example)}>
                      <CardContent>
                        <Typography variant="body2">
                          {example}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CodexTrigger;