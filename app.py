from flask import Flask, render_template, request, redirect, url_for
import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# In-memory storage for wardrobe inventory
wardrobe_inventory = []
image_urls = []  # Store fetched image URLs for selection

@app.route('/', methods=['GET', 'POST'])
def index():
    global image_urls
    if request.method == 'POST':
        description = request.form.get('description')
        file = request.files.get('photo')
        selected_image = request.form.get('selected_image')

        # Handle image selection
        if selected_image:
            wardrobe_inventory.append({'description': description, 'filename': selected_image})
            image_urls = []  # Clear fetched images after selection
            return redirect(url_for('index'))

        # Handle file upload or web search
        if description:
            if file:
                # Save the uploaded file
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                wardrobe_inventory.append({'description': description, 'filename': filename})
            else:
                # Search for similar items on the web using Google Custom Search API
                search_url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    "key": GOOGLE_API_KEY,
                    "cx": GOOGLE_SEARCH_ENGINE_ID,
                    "q": f"{description} clothing",  # Append "clothing" to the query
                    "searchType": "image",
                    "imgType": "photo",  # Filter for photos
                    "safe": "active",  # Enable SafeSearch
                    "num": 5
                }
                response = requests.get(search_url, params=params)
                response.raise_for_status()
                search_results = response.json()

                # Extract image URLs
                image_urls = [item["link"] for item in search_results.get("items", [])]

    return render_template('index.html', inventory=wardrobe_inventory, image_urls=image_urls)

if __name__ == '__main__':
    app.run(debug=True)