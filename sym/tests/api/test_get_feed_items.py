
import os
import requests
import json
import click

@click.command()
@click.option("--api-key", help="Sym API Key", default=None)
@click.option("--output-dir", help="Output directory", default=None)
@click.option("--stage", help="Sym API Stage (local, dev, prod) endpoint", default="local")
@click.option("--limit", help="How many items to return from the feed", default=4)
def get_feed_items(api_key, output_dir, stage, limit):
    sym_api_key = api_key

    if api_key is None:
        sym_api_key = os.environ.get("SYM_API_KEY")
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "data")
    if stage == "local":
        url_base = "http://localhost:8000"
    elif stage == "dev":
        url_base = "http://dev.sym.ai"
    elif stage == "prod":
        url_base = "http://sym.ai"
    else:
        raise Exception(f"Invalid stage: {stage}")



    headers = {"X-API-KEY":sym_api_key}
    r = requests.get(url_base+"/api/ode/default-feed", headers=headers)
    feed = r.json()
    print(feed)
    feed_id = feed["id"]

    #now get items from the feed
    
    headers = {"X-API-KEY":sym_api_key}
    r = requests.get(url_base+f"/api/ode/feed/{feed_id}/items?limit={limit}", headers=headers)
    print(r.status_code)
    if (r.status_code == 200):
        with open(os.path.join(output_dir, "feed_items.json"), "w") as f:
            f.write(json.dumps(r.json(), indent=2))
    else:
        
        print(r.text)

if __name__ == "__main__":
    get_feed_items()