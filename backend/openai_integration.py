"""OpenAI API integration module for the automation platform."""

import asyncio
from typing import Dict, List, Optional, Any
import openai
from tenacity import retry, wait_exponential, stop_after_attempt
import logging

from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenAIClient:
    """OpenAI API client with retry logic and error handling."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key. If None, uses settings.openai_api_key
        """
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
    
    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    async def generate_code(
        self, 
        prompt: str, 
        language: str = "python",
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate code using OpenAI Codex.
        
        Args:
            prompt: The prompt for code generation
            language: Programming language for the code
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated code as string
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"You are a helpful coding assistant. Generate {language} code based on the user's requirements."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                max_tokens=max_tokens or settings.openai_max_tokens,
                temperature=0.2
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            raise
    
    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    async def analyze_code(self, code: str, analysis_type: str = "review") -> Dict[str, Any]:
        """Analyze code for various purposes.
        
        Args:
            code: The code to analyze
            analysis_type: Type of analysis (review, security, performance, etc.)
            
        Returns:
            Analysis results as dictionary
        """
        try:
            prompt = f"""
            Analyze the following code for {analysis_type}:
            
            ```
            {code}
            ```
            
            Provide analysis in the following JSON format:
            {{
                "issues": ["list of issues found"],
                "suggestions": ["list of improvement suggestions"],
                "severity": "low|medium|high",
                "summary": "brief summary of analysis"
            }}
            """
            
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=settings.openai_max_tokens,
                temperature=0.1
            )
            
            # In a real implementation, you'd parse the JSON response
            return {
                "raw_response": response.choices[0].message.content.strip(),
                "analysis_type": analysis_type
            }
            
        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
            raise
    
    async def generate_automation_script(
        self, 
        task_description: str,
        platform: str = "github"
    ) -> str:
        """Generate automation scripts for various platforms.
        
        Args:
            task_description: Description of the automation task
            platform: Target platform (github, gitlab, etc.)
            
        Returns:
            Generated automation script
        """
        prompt = f"""
        Generate a {platform} automation script for the following task:
        {task_description}
        
        The script should:
        1. Be production-ready with error handling
        2. Include proper logging
        3. Follow best practices for {platform} automation
        4. Include necessary comments and documentation
        """
        
        return await self.generate_code(prompt, language="python")


# Global client instance
openai_client = OpenAIClient()