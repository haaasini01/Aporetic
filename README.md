# Aporetic

An AI tutor that uses the Socratic method to help students learn through guided questions instead of direct answers.

## Features

- Interactive chat interface
- Socratic teaching method
- Fact checking with WolframAlpha
- Powered by Google Gemini AI
- Built with Streamlit and LangChain

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
- Copy `.env.example` to `.env`
- Add your API keys:
  - `GEMINI_API_KEY` 
  - `WOLFRAM_APP_ID`

3. Run the app:
```bash
streamlit run app.py
```

## Usage

1. Open the app in your browser
2. Ask a question you want to learn about
3. Socrates will guide you with hints and questions
4. Work through the problem step by step
5. Use the Clear button to start a new conversation

## Limitations

- Needs valid API keys for Gemini and WolframAlpha
- Limited to text-based learning
- May not work with very complex mathematical problems
