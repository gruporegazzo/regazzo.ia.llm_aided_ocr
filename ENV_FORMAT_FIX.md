# .env Format Fix for Boolean Values

## Issue
The original .env file had inline comments on boolean configuration lines:
```env
PADDLEOCR_USE_TABLE_RECOGNITION=True  # Enable table structure detection
```

This caused a ValueError when the `python-decouple` library tried to parse the boolean value:
```
ValueError: Invalid truth value: true # enable table structure detection
```

## Solution
Moved all comments to separate lines above the configuration values:
```env
# Enable table structure detection
PADDLEOCR_USE_TABLE_RECOGNITION=True
```

## Correct .env Format
```env
# LLM Configuration
USE_LOCAL_LLM=False
API_PROVIDER=OPENAI
ANTHROPIC_API_KEY=your-anthropic-api-key
OPENAI_API_KEY=your-openai-api-key
CLAUDE_MODEL_STRING=claude-3-haiku-20240307
OPENAI_COMPLETION_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# OCR Engine Configuration
# Options: TESSERACT or PADDLEOCR
OCR_ENGINE=TESSERACT
# Language for PaddleOCR (Portuguese)
PADDLEOCR_LANG=pt
# Enable table structure detection
PADDLEOCR_USE_TABLE_RECOGNITION=True
```

## Testing
The fix has been verified with:
- Configuration loading test passes
- Streamlit app starts without errors
- Boolean values are correctly parsed as `<class 'bool'>`
