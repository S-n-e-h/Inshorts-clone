Inshorts Clone
This is a lightweight clone of the Inshorts news website. It fetches short news snippets from a public News API and provides access to the full news articles by scraping the source websites. For users who prefer concise information, the website also uses an AI model (DistilBART) to summarize full articles into approximately 60 words.

Features
Short news feed powered by a News API

Full article extraction via web scraping

Summarization of full articles into 60 words using DistilBART

Simple and intuitive user interface

Tech Stack
Frontend: HTML, CSS, JavaScript

Backend: Python (for scraping and summarization)

API: News API

AI Model: DistilBART from HuggingFace for summarization

Web Scraping: BeautifulSoup

How It Works
The app fetches short news articles using a public News API.

When the user clicks on "Read More", the full article is scraped from the original news website.

The full content is passed through the DistilBART model, which compresses it into a concise 60-word summary.

Setup Instructions
Clone the repository:
  git clone https://github.com/yourusername/inshorts-clone.git
  cd inshorts-clone
Install dependencies:
  For Python backend:
    pip install -r requirements.txt

Running the App
python news_server.py

Future Improvements
Add news categories (technology, business, sports, etc.)
Deploy the app using Netlify (frontend) and Render/Heroku (backend)

License
This project is licensed under the MIT License.
