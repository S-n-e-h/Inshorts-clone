import time
import random
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch

app = Flask(__name__)
CORS(app)

try:
    model_name = "sshleifer/distilbart-cnn-12-6"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    summarizer = pipeline("summarization", model=model, tokenizer=tokenizer,
                          device=0 if torch.cuda.is_available() else -1)
except Exception as e:
    print(f"Model initialization failed: {e}")
    summarizer = None

# Extract readable content from HTML
def extract_readable_content(soup):
    for tag in ['article', 'main', 'div.content', 'div.article']:
        element = soup.select_one(tag)
        if element:
            return element.get_text(separator='\n\n', strip=True)

    paragraphs = soup.find_all('p')
    content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
    return content if content else "No readable content found."

# Truncate input text to 1000 tokens
def truncate_to_1000_tokens(text, tokenizer):
    tokens = tokenizer.encode(text, truncation=False, add_special_tokens=False)
    truncated_tokens = tokens[:1000]
    truncated_text = tokenizer.decode(truncated_tokens, skip_special_tokens=True)
    return truncated_text

@app.route('/extract', methods=['POST'])
def extract_article():
    try:
        data = request.get_json()
        url = data.get('url') if data else None
        if not url:
            return jsonify({"error": "URL is required"}), 400

        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

        time.sleep(random.uniform(1, 3))  # polite scraping

        try:
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            response.raise_for_status()
        except requests.exceptions.SSLError:
            response = requests.get(url, headers=headers, timeout=10, verify=False, allow_redirects=True)
            response.raise_for_status()

        response.encoding = response.encoding or 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else "No title found"
        content = extract_readable_content(soup)

        if not content or content == "No readable content found.":
            return jsonify({
                "title": title,
                "content": "No readable content could be extracted.",
                "summary": "No summary available."
            })

        # Clean and truncate text
        content_clean = ' '.join(content.split())
        truncated_text = truncate_to_1000_tokens(content_clean, tokenizer)

        # Generate summary
        if summarizer:
            try:
                summary_result = summarizer(
                    truncated_text,
                    max_length=200,
                    min_length=100,
                    do_sample=False
                )[0]['summary_text']

                summary = ' '.join(summary_result.strip().split()[:150])  # max 100 words
            except Exception as e:
                print(f"Summarization error: {e}")
                summary = "Summary generation failed."
        else:
            summary = "Summarizer not available."

        return jsonify({
            "title": title,
            "content": truncated_text,
            "summary": summary
        })

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
