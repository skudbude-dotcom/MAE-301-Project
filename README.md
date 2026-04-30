PantryPal MVP Demo Instructions Overview: 
PantryPal is a web-based meal suggestion app. Users enter ingredients they already have, and the app returns three meal suggestions with descriptions, used ingredients, missing ingredients, cooking time, and difficulty.

Environment Setup 
Install the required Python packages: 
pip3 install flask anthropic

Running the No-AI Baseline Version 
The no-AI baseline does not require an API key. 
If the file is in the main project folder, run: 
python3 pantrypal_noai.py
Then open a browser and go to:
http://localhost:5000

Running the AI-Assisted Version
The AI-assisted version requires an Anthropic API key.
Set the API key in the terminal:
export ANTHROPIC_API_KEY=your_api_key_here
If the file is in the main project folder, run:
python3 pantrypal.py
If the file is inside the /mvp/src/ folder, run:
python3 src/pantrypal.py
Then open a browser and go to:
http://localhost:5000

Minimal Demo
To test the app, enter:
eggs, rice, soy sauce, garlic, onion
The app should return three meal suggestions.

Notes
The no-AI version is easiest to run because it does not require an API key. The AI-assisted version can handle more flexible natural-language input, but it requires a valid Anthropic API key.
