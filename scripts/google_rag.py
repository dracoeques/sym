import requests
import os

def google_search(query):
    api_key = os.environ.get("GOOGLE_API_KEY")
    cse_id = os.environ.get("GOOGLE_CSE_ID")
    url = 'https://www.googleapis.com/customsearch/v1?q={}&key={}&cx={}'.format(query, api_key, cse_id)
    response = requests.get(url)
    return response.json()

def extract_snippets_from_results(results):
    return [item['snippet'] for item in results.get('items', [])]


if __name__ == "__main__":
    query = input("What is your google query")
    resp = google_search(query)
    snippets = extract_snippets_from_results(resp)
    print(snippets)