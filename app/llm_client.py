"""LLM client for solving quizzes."""
import logging
import json
from typing import Optional, Union, Dict, Any, List
from openai import AsyncOpenAI

from app.config import config
from app.tools.scraper import scrape_url, download_file
from app.tools.data_processor import process_pdf, process_csv, process_image
from app.tools.analyzer import analyze_dataframe, calculate_statistics
from app.tools.visualizer import create_chart, create_matplotlib_chart

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with OpenAI API with function calling."""
    
    def __init__(self):
        if not config.OPENAI_API_KEY:
            logger.warning("OpenAI API key not set")
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        self.model = "gpt-4-turbo-preview"  # Can be changed to gpt-4 or gpt-3.5-turbo
        self.functions = self._get_function_definitions()
        self.function_map = self._get_function_map()
    
    def _get_function_definitions(self) -> List[Dict[str, Any]]:
        """Define available functions for the LLM."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "scrape_url",
                    "description": "Scrape a URL and extract its content. Use this for web scraping tasks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to scrape"
                            }
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "download_file",
                    "description": "Download a file from a URL. Returns file info and base64 content if small enough.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL of the file to download"
                            }
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "process_pdf",
                    "description": "Process a PDF file from base64 content. Extracts text and metadata.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "base64_content": {
                                "type": "string",
                                "description": "Base64 encoded PDF content"
                            }
                        },
                        "required": ["base64_content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "process_csv",
                    "description": "Process a CSV file from base64 content. Returns DataFrame info and summary.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "base64_content": {
                                "type": "string",
                                "description": "Base64 encoded CSV content"
                            }
                        },
                        "required": ["base64_content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "process_image",
                    "description": "Process an image from base64 content. Returns image metadata.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "base64_content": {
                                "type": "string",
                                "description": "Base64 encoded image content (with or without data URI prefix)"
                            }
                        },
                        "required": ["base64_content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_dataframe",
                    "description": "Perform data analysis operations on a DataFrame (sum, mean, count, filter, groupby, sort).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "array",
                                "description": "List of dictionaries representing rows",
                                "items": {"type": "object"}
                            },
                            "operation": {
                                "type": "string",
                                "enum": ["sum", "mean", "count", "filter", "groupby", "sort"],
                                "description": "The operation to perform"
                            },
                            "column": {
                                "type": "string",
                                "description": "Column name for operations like sum, mean, sort"
                            },
                            "by": {
                                "type": "string",
                                "description": "Column name for groupby operation"
                            },
                            "agg": {
                                "type": "string",
                                "description": "Aggregation function for groupby (default: count)"
                            },
                            "ascending": {
                                "type": "boolean",
                                "description": "Sort order (default: true)"
                            }
                        },
                        "required": ["data", "operation"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_statistics",
                    "description": "Calculate statistics (count, mean, std, min, max, median, sum) for a numeric column.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "array",
                                "description": "List of dictionaries representing rows",
                                "items": {"type": "object"}
                            },
                            "column": {
                                "type": "string",
                                "description": "Column name to analyze"
                            }
                        },
                        "required": ["data", "column"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_chart",
                    "description": "Create a chart (bar, line, scatter, pie) from data. Returns base64 encoded image.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "array",
                                "description": "List of dictionaries representing rows",
                                "items": {"type": "object"}
                            },
                            "chart_type": {
                                "type": "string",
                                "enum": ["bar", "line", "scatter", "pie"],
                                "description": "Type of chart to create"
                            },
                            "x": {
                                "type": "string",
                                "description": "X-axis column name"
                            },
                            "y": {
                                "type": "string",
                                "description": "Y-axis column name"
                            },
                            "title": {
                                "type": "string",
                                "description": "Chart title"
                            }
                        },
                        "required": ["data", "chart_type", "x", "y"]
                    }
                }
            }
        ]
    
    def _get_function_map(self) -> Dict[str, callable]:
        """Map function names to actual functions."""
        return {
            "scrape_url": scrape_url,
            "download_file": download_file,
            "process_pdf": process_pdf,
            "process_csv": process_csv,
            "process_image": process_image,
            "analyze_dataframe": analyze_dataframe,
            "calculate_statistics": calculate_statistics,
            "create_chart": create_chart
        }
    
    async def solve_quiz(self, instructions: str, url: str) -> Optional[Union[bool, int, float, str, Dict]]:
        """
        Use LLM to solve quiz based on instructions with function calling.
        
        Args:
            instructions: Quiz instructions text
            url: Quiz URL (for context)
            
        Returns:
            Answer in appropriate format (bool, int, float, str, or dict)
        """
        system_prompt = """You are an expert data analyst and problem solver. Your task is to solve quizzes that involve:
- Web scraping and data sourcing
- Data preparation and cleansing
- Data analysis (filtering, sorting, aggregating, statistical analysis)
- Data visualization
- API interactions
- File processing (PDF, images, etc.)

You have access to tools for scraping, downloading files, processing data, analyzing, and visualizing.
Use these tools as needed to solve the quiz step by step.

Read the quiz instructions carefully and solve the problem. 
Your final answer should be in the format requested (boolean, number, string, base64 URI, or JSON object).
Be precise and accurate."""

        user_prompt = f"""Quiz URL: {url}

Quiz Instructions:
{instructions}

Solve this quiz step by step using the available tools. The final answer should be:
- A boolean (true/false) if the question asks for yes/no
- A number (integer or float) if the question asks for a numeric value
- A string if the question asks for text
- A base64 URI (data:image/png;base64,...) if the question asks for an image/chart
- A JSON object if the question asks for structured data

When you have the final answer, provide it clearly."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        max_iterations = 10  # Prevent infinite loops
        iteration = 0
        
        try:
            while iteration < max_iterations:
                iteration += 1
                logger.info(f"LLM iteration {iteration}")
                
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.functions if self.functions else None,
                    tool_choice="auto" if self.functions else None,
                    temperature=0.1,
                    max_tokens=2000
                )
                
                message = response.choices[0].message
                messages.append(message)
                
                # Check if LLM wants to call a function
                if message.tool_calls:
                    logger.info(f"LLM requested {len(message.tool_calls)} function call(s)")
                    
                    # Execute function calls
                    for tool_call in message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        logger.info(f"Calling {function_name} with args: {function_args}")
                        
                        if function_name in self.function_map:
                            try:
                                function = self.function_map[function_name]
                                result = await function(**function_args)
                                
                                # Add function result to messages
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "name": function_name,
                                    "content": json.dumps(result)
                                })
                            except Exception as e:
                                logger.error(f"Error executing {function_name}: {e}")
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "name": function_name,
                                    "content": json.dumps({"error": str(e)})
                                })
                        else:
                            logger.warning(f"Unknown function: {function_name}")
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": function_name,
                                "content": json.dumps({"error": f"Unknown function: {function_name}"})
                            })
                else:
                    # LLM provided final answer
                    answer_text = message.content.strip()
                    logger.info(f"LLM final response: {answer_text}")
                    
                    # Try to extract just the answer value
                    answer = self._extract_answer(answer_text)
                    return answer
            
            logger.error("Max iterations reached")
            return None
            
        except Exception as e:
            logger.error(f"Error calling LLM: {e}", exc_info=True)
            return None
    
    def _extract_answer(self, answer_text: str) -> Union[bool, int, float, str, Dict]:
        """Extract and parse answer from LLM response."""
        # Try to find JSON in the response
        json_match = None
        try:
            # Look for JSON objects
            import re
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, answer_text)
            if matches:
                json_match = json.loads(matches[-1])  # Take the last match
        except:
            pass
        
        if json_match:
            return json_match
        
        # Try to parse the whole text as JSON
        answer_text = answer_text.strip()
        try:
            parsed = json.loads(answer_text)
            return parsed
        except json.JSONDecodeError:
            pass
        
        # Try boolean
        if answer_text.lower() in ['true', 'false']:
            return answer_text.lower() == 'true'
        
        # Try number (look for numbers in the text)
        import re
        numbers = re.findall(r'-?\d+\.?\d*', answer_text)
        if numbers:
            try:
                if '.' in numbers[0]:
                    return float(numbers[0])
                else:
                    return int(numbers[0])
            except ValueError:
                pass
        
        # Return as string
        return answer_text

