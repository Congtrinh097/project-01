# Hugging Face Resume Generator Integration

## Overview
The Resume Generator feature has been updated to use Hugging Face's InferenceClient with Featherless AI provider instead of local LLaMA models. This provides better performance, easier deployment, and no need for local model files.

## Changes Made

### 1. Updated `backend/services/resume_generator.py`
- Replaced `LlamaModel` class with `HuggingFaceModel` class
- Uses `huggingface_hub.InferenceClient` with Featherless AI provider
- Supports `meta-llama/Llama-3.1-8B` model (default)
- Falls back to `MockLlamaModel` if Hugging Face is unavailable

### 2. Updated `backend/requirements.txt`
- Removed: `llama-cpp-python==0.2.20`
- Added: `huggingface-hub==0.20.1`

### 3. Updated `env.example`
- Removed: `MODEL_PATH` variable
- Added: `HF_TOKEN` - Your Hugging Face API token
- Added: `HF_MODEL_NAME` - Model name (optional, defaults to `meta-llama/Llama-3.1-8B`)

## Setup Instructions

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Get Hugging Face API Token
1. Go to [Hugging Face](https://huggingface.co/)
2. Sign up or log in
3. Go to Settings → Access Tokens
4. Create a new token with read permissions
5. Copy the token

### 3. Configure Environment Variables
Update your `.env` file (or create one from `env.example`):

```env
# Hugging Face Configuration (for Resume Generation)
HF_TOKEN=your_huggingface_token_here
HF_MODEL_NAME=meta-llama/Llama-3.1-8B  # Optional
```

### 4. Restart the Backend
```bash
# If running with Docker
docker-compose restart backend

# If running locally
uvicorn main:app --reload
```

## Usage

### API Endpoint
**POST** `/generate-resume`

**Request Body:**
```json
{
  "input_text": "Name: John Doe\nTitle: Software Engineer\nExperience: 5 years in web development\nSkills: JavaScript, React, Node.js\nEducation: B.Sc Computer Science"
}
```

**Response:**
```json
{
  "id": 1,
  "generated_text": "JOHN DOE\nSoftware Engineer\n...",
  "pdf_filename": "resume_20251017_123456.pdf",
  "download_url": "/download-resume/1",
  "file_size": 12345,
  "created_at": "2025-10-17T12:34:56"
}
```

## Supported Models

The default model is `meta-llama/Llama-3.1-8B`, but you can use other models supported by Featherless AI:

- `meta-llama/Llama-3.1-8B` (default)
- `meta-llama/Llama-3.1-70B`
- `meta-llama/Meta-Llama-3-8B-Instruct`
- And other models available via Featherless AI

To change the model, set the `HF_MODEL_NAME` environment variable.

## Fallback Mode

If the Hugging Face client fails to initialize (e.g., missing token or network issues), the system automatically falls back to `MockLlamaModel`, which generates synthetic resume examples using template logic.

**MockLlamaModel Behavior:**
- Uses template-based generation
- Produces deterministic results
- Good for testing and development
- Does not require API tokens or internet connection

## Benefits of Hugging Face Integration

1. **No Local Model Files**: No need to download large model files (several GB)
2. **Better Performance**: Cloud-based inference with optimized hardware
3. **Easy Deployment**: Works in any environment with internet access
4. **Scalability**: Handles concurrent requests efficiently
5. **Model Flexibility**: Easy to switch between different models
6. **Cost-Effective**: Pay-per-use pricing model

## Troubleshooting

### Error: "HF_TOKEN environment variable not set"
**Solution:** Make sure you've set the `HF_TOKEN` in your `.env` file and restarted the backend.

### Error: "huggingface_hub is not installed"
**Solution:** Run `pip install -r requirements.txt` in the backend directory.

### Error: "Failed to initialize Hugging Face client"
**Solution:** 
- Check your internet connection
- Verify your HF_TOKEN is valid
- Check the backend logs for detailed error messages

### System Falls Back to Mock Mode
**Solution:** 
- This is expected if HF_TOKEN is not set or invalid
- Check backend logs for the reason
- Mock mode is sufficient for testing, but won't generate AI-powered resumes

## Example Usage in Frontend

The frontend `GenerateResumeTab` component automatically uses this feature:

1. User enters their information in the text area
2. Clicks "Generate CV" button
3. Backend uses Hugging Face to generate professional resume text
4. PDF is generated and available for download
5. Resume text is displayed in the interface

## Migration from Local LLaMA

If you were previously using local LLaMA models:

1. Remove any downloaded model files from `./models/` directory
2. Update your environment variables (remove `MODEL_PATH`, add `HF_TOKEN`)
3. Restart the backend
4. No changes needed in the frontend

## Security Notes

- Keep your `HF_TOKEN` secure and never commit it to version control
- Use environment variables or secure secret management
- The token is only used for server-side API calls
- Frontend never sees or handles the HF_TOKEN

## Performance

- Average generation time: 5-15 seconds (depending on model and prompt length)
- Concurrent requests: Supported (handles multiple users)
- Rate limiting: Handled by Featherless AI / Hugging Face

## Future Enhancements

Possible improvements for future versions:
- Support for more model providers (Anthropic, Cohere, etc.)
- Caching of generated resumes
- Batch processing for multiple resumes
- Custom fine-tuned models for resume generation
- Resume templates and style selection

## References

- [Hugging Face Documentation](https://huggingface.co/docs)
- [Featherless AI](https://featherless.ai/)
- [InferenceClient API](https://huggingface.co/docs/huggingface_hub/package_reference/inference_client)

---

**Last Updated:** October 17, 2025  
**Version:** 2.0.0

