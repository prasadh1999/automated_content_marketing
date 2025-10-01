# Automated Content Marketing Assistant

This is a simple Python application built with Streamlit that helps automate content marketing tasks. You can provide a blog post URL, a YouTube URL, or paste in a text transcript, and the tool will generate a concise summary, engaging tweets, a LinkedIn post, and relevant SEO keywords.

This project is designed for beginners and includes a placeholder for integrating a powerful language model like Gemini, with a safe, local fallback for immediate use.

## Features

- **Multiple Input Options:** Use a URL for a blog or YouTube video, or simply paste text.
- **Content Scraping:** Automatically fetches content from blogs using `requests` and `BeautifulSoup`.
- **YouTube Transcripts:** Extracts full video transcripts using `youtube-transcript-api`.
- **AI-Powered Content Generation:** Includes a function stub (`llm_generate`) for you to connect your preferred Large Language Model (LLM).
- **Safe Fallback:** A simple, non-LLM generator runs by default, making the app usable without an LLM API key.
- **Simple UI:** A clean and straightforward user interface powered by Streamlit.

## How to Run

Follow these steps to get the application running on your local machine.

### 1. Prerequisites

- Python 3.7+ installed on your system.
- `pip` (Python's package installer).

### 2. Setup & Installation

**A. Clone or Download the Project**

First, get the project files onto your computer. You can either download the source code as a ZIP file or clone the repository if you have Git installed.

**B. Create a Virtual Environment (Recommended)**

It's a best practice to create a virtual environment to keep the project's dependencies isolated.

**On Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**C. Install Dependencies**

Install all the required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 3. Run the Application

With your virtual environment active and dependencies installed, run the Streamlit app with the following command:

```bash
streamlit run app.py
```

Your web browser should automatically open a new tab with the running application. If not, the command line will provide a local URL (usually `http://localhost:8501`) that you can visit.

### 4. (Optional) Add Your LLM API Key

To unlock the full power of this tool, you can replace the `fallback_generator` call inside the `llm_generate` function in `app.py` with an actual API call to a service like Google's Gemini.

For example:

```python
# In app.py

def llm_generate(prompt: str) -> str:
    # Replace this with your actual API call
    # Example for Gemini API (you would need to set it up)
    # import google.generativeai as genai
    # genai.configure(api_key="YOUR_API_KEY")
    # model = genai.GenerativeModel('gemini-pro')
    # response = model.generate_content(prompt)
    # return response.text

    # The original fallback is below
    return fallback_generator(prompt)
```
