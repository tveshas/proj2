# Quiz Solver API

An LLM-powered application that automatically solves data-related quizzes involving web scraping, data analysis, and visualization.

## Features

- **API Endpoint**: Accepts POST requests with quiz tasks
- **Secret Validation**: Verifies requests using a secret string
- **JavaScript Rendering**: Uses Playwright to render JavaScript-heavy quiz pages
- **LLM-Powered Solving**: Uses OpenAI GPT-4 with function calling to interpret and solve quizzes
- **Function Tools**: Includes tools for web scraping, file processing, data analysis, and visualization
- **Quiz Chaining**: Automatically handles quiz chains (correct answer → next URL)
- **Retry Logic**: Retries wrong answers within the 3-minute timeout window
- **Multiple Answer Formats**: Supports boolean, number, string, base64 URI, and JSON answers

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Set environment variables** in `.env`:
   ```
   EMAIL=your-email@example.com
   SECRET=your-secret-string
   OPENAI_API_KEY=your-openai-api-key
   HOST=0.0.0.0
   PORT=8000
   ```

4. **Run the server**:
   ```bash
   python run.py
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST `/quiz`

Accepts quiz task requests.

**Request Body**:
```json
{
  "email": "your-email@example.com",
  "secret": "your-secret-string",
  "url": "https://example.com/quiz-834"
}
```

**Responses**:
- `200 OK`: Secret valid, quiz processing started
- `400 Bad Request`: Invalid JSON payload
- `403 Forbidden`: Invalid secret

### GET `/health`

Health check endpoint.

### GET `/`

Root endpoint with API information.

## Testing

Test with the demo endpoint:
```bash
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "secret": "your-secret-string",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

## Project Structure

```
p2/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── quiz_solver.py       # Core quiz solving logic
│   ├── browser.py           # Playwright browser automation
│   ├── llm_client.py        # OpenAI LLM integration with function calling
│   └── tools/               # LLM function tools
│       ├── __init__.py
│       ├── scraper.py       # Web scraping tools
│       ├── data_processor.py # File processing (PDF, CSV, images)
│       ├── analyzer.py      # Data analysis tools
│       └── visualizer.py    # Chart generation tools
├── requirements.txt
├── LICENSE
├── README.md
└── run.py
```

## License

MIT License

