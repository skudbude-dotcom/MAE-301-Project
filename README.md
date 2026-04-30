[PantryPal MVP Demo Instructions Overview]
PantryPal is a web-based meal suggestion app. Users enter ingredients they already have, and the app returns three meal suggestions with descriptions, used ingredients, missing ingredients, cooking time, and difficulty.

[How to Obtain an Anthropic API Key]
Go to https://console.anthropic.com and create a free account (or sign in if you already have one).
Once logged in, navigate to API Keys in the left sidebar.
Click Create Key, give it a name (e.g. "PantryPal"), and copy the key — you won't be able to see it again after closing the dialog.
(Optional) Set a usage limit under Plans & Billing to avoid unexpected charges.
New accounts receive free credits to get started. Paid usage is billed per token beyond the free tier.

[Environment Setup] 
Install the required Python packages by typing this into the command window:
pip3 install flask anthropic

[Running the No-AI Baseline Version] 
The no-AI baseline does not require an API key. 
If the file is in the main project folder, run: 
python3 pantrypal_noai.py
Then open a browser and go to:
http://localhost:5000

[Running the AI-Assisted Version]
The AI-assisted version requires an Anthropic API key.
Set the API key in the terminal:
export ANTHROPIC_API_KEY=your_api_key_here
If the file is in the main project folder, run:
python3 pantrypal.py
Then open a browser and go to:
http://localhost:5000

[Minimal Demo]
To test the app, enter:
eggs, rice, soy sauce, garlic, onion
The app should return three meal suggestions.

[Notes]
The no-AI version is easiest to run because it does not require an API key. The AI-assisted version can handle more flexible natural-language input, but it requires a valid Anthropic API key.
