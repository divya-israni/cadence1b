# AI-Generated Match Summaries Setup

The system now includes AI-generated match summaries to help recruiters quickly understand candidate-job matches.

## Setup Options

### Option 1: Groq (Recommended - Fastest & Most Affordable) ⚡

1. Get an API key from [Groq](https://console.groq.com/keys)
2. Set environment variable:
   ```bash
   export GROQ_API_KEY=your_groq_api_key_here
   ```
3. Install dependency (if not already installed):
   ```bash
   pip install openai
   ```

**Where to put the API key:**
- **For development**: Add to your shell profile (`~/.zshrc` or `~/.bashrc`):
  ```bash
  echo 'export GROQ_API_KEY=your_groq_api_key_here' >> ~/.zshrc
  source ~/.zshrc
  ```
- **For production**: Set in your deployment environment variables (Heroku, AWS, etc.)
- **For testing**: Run in terminal before starting server:
  ```bash
  export GROQ_API_KEY=your_groq_api_key_here
  uvicorn app:app --reload
  ```

### Option 2: OpenAI (GPT-3.5/GPT-4)

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Set environment variable:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

### Option 3: Google Gemini

1. Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set environment variable:
   ```bash
   export GEMINI_API_KEY=your_api_key_here
   ```
3. Install dependency:
   ```bash
   pip install google-generativeai
   ```

### Option 4: No API (Fallback)

If no API keys are set, the system will use a template-based summary. This is less sophisticated but still provides useful information.

## Usage

Once configured, AI summaries will automatically appear in match results. The system will:
1. Try **Groq** first (if API key is set) - **Recommended for speed**
2. Try OpenAI second (if API key is set)
3. Try Gemini third (if API key is set)
4. Fall back to template-based summary if none are available

## Cost Considerations

- **Groq**: **FREE tier** (up to 14,400 requests/day), then very affordable
- **OpenAI GPT-3.5-turbo**: ~$0.002 per summary
- **Google Gemini**: Free tier available, then pay-as-you-go
- **Fallback**: Free (no API calls)

**Groq is recommended** because it's:
- ⚡ **Fastest** (ultra-low latency)
- 💰 **Most affordable** (free tier available)
- 🚀 **High quality** (uses Llama 3.1 70B model)

