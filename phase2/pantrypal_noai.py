"""
PantryPal MVP - Pure Python, Zero AI, No API Keys
===================================================
SETUP:
    pip install flask

RUN:
    python pantrypal_noai.py

Then open: http://localhost:5000
"""

from flask import Flask, request, jsonify
import re
from difflib import SequenceMatcher

app = Flask(__name__)

# =============================================================================
#  RECIPE DATABASE  (50 recipes, fully hardcoded — no internet needed)
# =============================================================================
RECIPES = [
    {
        "name": "Classic Fried Rice",
        "emoji": "🍳",
        "description": "A satisfying one-pan meal that turns leftover rice into something amazing. Quick, filling, and endlessly customizable.",
        "ingredients": ["rice", "egg", "soy sauce", "garlic", "onion", "oil", "green onion", "sesame oil"],
        "required": ["rice", "egg", "soy sauce"],
        "time": "20 min",
        "difficulty": "Easy",
    },
    {
        "name": "Spaghetti Aglio e Olio",
        "emoji": "🍝",
        "description": "A legendary Italian pantry pasta — just garlic, olive oil, and pasta. Simple ingredients, incredible flavor.",
        "ingredients": ["spaghetti", "garlic", "olive oil", "parsley", "red pepper flakes", "parmesan"],
        "required": ["spaghetti", "garlic", "olive oil"],
        "time": "25 min",
        "difficulty": "Easy",
    },
    {
        "name": "Veggie Omelette",
        "emoji": "🍳",
        "description": "Fluffy eggs folded around whatever vegetables you have on hand. Great for breakfast, lunch, or a lazy dinner.",
        "ingredients": ["egg", "onion", "bell pepper", "tomato", "cheese", "butter", "salt", "pepper"],
        "required": ["egg"],
        "time": "15 min",
        "difficulty": "Easy",
    },
    {
        "name": "Chicken Stir-Fry",
        "emoji": "🥘",
        "description": "Tender chicken and crisp vegetables tossed in a savory sauce. A weeknight staple that comes together in minutes.",
        "ingredients": ["chicken", "soy sauce", "garlic", "ginger", "broccoli", "carrot", "onion", "oil", "cornstarch"],
        "required": ["chicken", "soy sauce"],
        "time": "25 min",
        "difficulty": "Medium",
    },
    {
        "name": "Tomato Basil Pasta",
        "emoji": "🍅",
        "description": "Fresh tomatoes and basil tossed with hot pasta and a splash of olive oil. Tastes like summer in a bowl.",
        "ingredients": ["pasta", "tomato", "basil", "garlic", "olive oil", "parmesan", "salt", "pepper"],
        "required": ["pasta", "tomato"],
        "time": "20 min",
        "difficulty": "Easy",
    },
    {
        "name": "Bean & Rice Burrito Bowl",
        "emoji": "🌯",
        "description": "A hearty, protein-packed bowl with seasoned beans over fluffy rice. Customize with whatever toppings you have.",
        "ingredients": ["rice", "black beans", "cumin", "garlic", "lime", "cilantro", "salsa", "cheese", "sour cream"],
        "required": ["rice", "black beans"],
        "time": "20 min",
        "difficulty": "Easy",
    },
    {
        "name": "Pancakes",
        "emoji": "🥞",
        "description": "Fluffy, golden pancakes from scratch using pantry staples. Perfect for breakfast or a breakfast-for-dinner situation.",
        "ingredients": ["flour", "egg", "milk", "butter", "sugar", "baking powder", "salt", "vanilla"],
        "required": ["flour", "egg", "milk"],
        "time": "20 min",
        "difficulty": "Easy",
    },
    {
        "name": "Grilled Cheese Sandwich",
        "emoji": "🥪",
        "description": "The ultimate comfort food — buttery, crispy bread with gooey melted cheese inside. Hard to beat.",
        "ingredients": ["bread", "cheese", "butter"],
        "required": ["bread", "cheese", "butter"],
        "time": "10 min",
        "difficulty": "Easy",
    },
    {
        "name": "Potato Soup",
        "emoji": "🥣",
        "description": "Creamy, warming soup made from simple ingredients. Add cheese and bacon bits on top if you have them.",
        "ingredients": ["potato", "onion", "garlic", "butter", "milk", "chicken broth", "cheese", "flour", "salt", "pepper"],
        "required": ["potato", "onion", "milk"],
        "time": "40 min",
        "difficulty": "Medium",
    },
    {
        "name": "Egg Fried Noodles",
        "emoji": "🍜",
        "description": "Quick noodles stir-fried with egg and a savory sauce. Ready in under 15 minutes and endlessly satisfying.",
        "ingredients": ["noodles", "egg", "soy sauce", "garlic", "green onion", "sesame oil", "oil"],
        "required": ["noodles", "egg", "soy sauce"],
        "time": "15 min",
        "difficulty": "Easy",
    },
    {
        "name": "Tuna Pasta",
        "emoji": "🐟",
        "description": "Canned tuna tossed with pasta, lemon, and capers — a Mediterranean-inspired meal from pantry staples.",
        "ingredients": ["pasta", "tuna", "olive oil", "lemon", "garlic", "capers", "parsley", "black pepper"],
        "required": ["pasta", "tuna"],
        "time": "20 min",
        "difficulty": "Easy",
    },
    {
        "name": "Avocado Toast",
        "emoji": "🥑",
        "description": "Creamy avocado smashed on crunchy toast with a squeeze of lemon. Top with an egg for extra protein.",
        "ingredients": ["bread", "avocado", "lemon", "salt", "red pepper flakes", "egg", "olive oil"],
        "required": ["bread", "avocado"],
        "time": "10 min",
        "difficulty": "Easy",
    },
    {
        "name": "Lentil Soup",
        "emoji": "🥣",
        "description": "A hearty, nourishing soup made from lentils and warming spices. Packed with protein and fiber.",
        "ingredients": ["lentils", "onion", "garlic", "carrot", "cumin", "turmeric", "tomato", "olive oil", "lemon"],
        "required": ["lentils", "onion"],
        "time": "45 min",
        "difficulty": "Easy",
    },
    {
        "name": "Quesadillas",
        "emoji": "🫓",
        "description": "Crispy tortillas filled with melted cheese and whatever else you have around. A universal crowd-pleaser.",
        "ingredients": ["tortilla", "cheese", "butter", "black beans", "salsa", "sour cream", "jalapeño"],
        "required": ["tortilla", "cheese"],
        "time": "15 min",
        "difficulty": "Easy",
    },
    {
        "name": "Banana Smoothie",
        "emoji": "🍌",
        "description": "A thick, creamy smoothie that takes 2 minutes to make. Naturally sweet and loaded with energy.",
        "ingredients": ["banana", "milk", "yogurt", "honey", "peanut butter"],
        "required": ["banana", "milk"],
        "time": "5 min",
        "difficulty": "Easy",
    },
    {
        "name": "French Toast",
        "emoji": "🍞",
        "description": "Thick slices of bread dipped in a sweet egg custard and fried until golden. A breakfast classic.",
        "ingredients": ["bread", "egg", "milk", "butter", "cinnamon", "vanilla", "sugar", "maple syrup"],
        "required": ["bread", "egg", "milk"],
        "time": "15 min",
        "difficulty": "Easy",
    },
    {
        "name": "Shakshuka",
        "emoji": "🍳",
        "description": "Eggs poached in a spiced tomato and pepper sauce. Serve straight from the pan with crusty bread.",
        "ingredients": ["egg", "tomato", "bell pepper", "onion", "garlic", "cumin", "paprika", "olive oil", "feta"],
        "required": ["egg", "tomato"],
        "time": "30 min",
        "difficulty": "Medium",
    },
    {
        "name": "Mac and Cheese",
        "emoji": "🧀",
        "description": "Creamy, cheesy macaroni made from scratch — way better than the box. A timeless comfort classic.",
        "ingredients": ["macaroni", "cheese", "milk", "butter", "flour", "salt", "pepper", "mustard"],
        "required": ["macaroni", "cheese", "milk", "butter"],
        "time": "30 min",
        "difficulty": "Medium",
    },
    {
        "name": "Chicken Soup",
        "emoji": "🍲",
        "description": "A simple, healing chicken soup with vegetables. Perfect for cold days or when you need something comforting.",
        "ingredients": ["chicken", "carrot", "celery", "onion", "garlic", "chicken broth", "noodles", "salt", "pepper", "parsley"],
        "required": ["chicken", "carrot", "onion"],
        "time": "50 min",
        "difficulty": "Medium",
    },
    {
        "name": "Peanut Butter Noodles",
        "emoji": "🥜",
        "description": "Noodles tossed in a rich, savory peanut butter sauce with a kick of chili. Ready in 15 minutes.",
        "ingredients": ["noodles", "peanut butter", "soy sauce", "garlic", "ginger", "sesame oil", "lime", "chili flakes", "green onion"],
        "required": ["noodles", "peanut butter", "soy sauce"],
        "time": "15 min",
        "difficulty": "Easy",
    },
    {
        "name": "Stuffed Bell Peppers",
        "emoji": "🫑",
        "description": "Bell peppers filled with a savory rice and meat mixture, then baked until tender. A colorful, satisfying meal.",
        "ingredients": ["bell pepper", "rice", "ground beef", "tomato", "onion", "garlic", "cheese", "olive oil"],
        "required": ["bell pepper", "rice"],
        "time": "50 min",
        "difficulty": "Medium",
    },
    {
        "name": "Garlic Butter Shrimp",
        "emoji": "🍤",
        "description": "Plump shrimp sautéed in garlic butter with a squeeze of lemon. On the table in under 15 minutes.",
        "ingredients": ["shrimp", "butter", "garlic", "lemon", "parsley", "salt", "pepper", "red pepper flakes"],
        "required": ["shrimp", "butter", "garlic"],
        "time": "15 min",
        "difficulty": "Easy",
    },
    {
        "name": "Vegetable Curry",
        "emoji": "🍛",
        "description": "A fragrant, warming curry loaded with vegetables and coconut milk. Serve over rice for a complete meal.",
        "ingredients": ["potato", "onion", "garlic", "ginger", "coconut milk", "curry powder", "tomato", "oil", "rice"],
        "required": ["potato", "onion", "coconut milk"],
        "time": "40 min",
        "difficulty": "Medium",
    },
    {
        "name": "Hummus & Pita",
        "emoji": "🧆",
        "description": "Silky smooth homemade hummus made from canned chickpeas. Ready in 5 minutes with a blender.",
        "ingredients": ["chickpeas", "tahini", "lemon", "garlic", "olive oil", "salt", "cumin", "pita"],
        "required": ["chickpeas", "lemon"],
        "time": "10 min",
        "difficulty": "Easy",
    },
    {
        "name": "Corn Fritters",
        "emoji": "🌽",
        "description": "Crispy golden fritters bursting with sweet corn. Great as a snack, side dish, or light meal with sour cream.",
        "ingredients": ["corn", "flour", "egg", "milk", "green onion", "cheese", "salt", "pepper", "oil"],
        "required": ["corn", "flour", "egg"],
        "time": "25 min",
        "difficulty": "Easy",
    },
    {
        "name": "BLT Sandwich",
        "emoji": "🥓",
        "description": "The classic bacon, lettuce, and tomato sandwich. Crispy, fresh, and ready in 10 minutes.",
        "ingredients": ["bread", "bacon", "lettuce", "tomato", "mayonnaise", "salt", "pepper"],
        "required": ["bread", "bacon", "tomato"],
        "time": "10 min",
        "difficulty": "Easy",
    },
    {
        "name": "Scrambled Eggs on Toast",
        "emoji": "🍳",
        "description": "Creamy, buttery scrambled eggs piled on crispy toast. Deceptively simple and incredibly good.",
        "ingredients": ["egg", "butter", "bread", "salt", "pepper", "chives", "milk"],
        "required": ["egg", "bread", "butter"],
        "time": "10 min",
        "difficulty": "Easy",
    },
    {
        "name": "Minestrone Soup",
        "emoji": "🥣",
        "description": "A hearty Italian vegetable soup with beans and pasta. Great for using up random vegetables.",
        "ingredients": ["tomato", "onion", "garlic", "carrot", "celery", "zucchini", "pasta", "cannellini beans", "olive oil", "basil"],
        "required": ["tomato", "onion", "pasta"],
        "time": "45 min",
        "difficulty": "Medium",
    },
    {
        "name": "Baked Potato",
        "emoji": "🥔",
        "description": "A fluffy baked potato loaded with toppings. Incredibly simple but incredibly satisfying.",
        "ingredients": ["potato", "butter", "cheese", "sour cream", "bacon", "green onion", "salt", "olive oil"],
        "required": ["potato"],
        "time": "60 min",
        "difficulty": "Easy",
    },
    {
        "name": "Egg Drop Soup",
        "emoji": "🍲",
        "description": "Silky ribbons of egg in a simple, warming broth. A Chinese restaurant classic you can make at home in minutes.",
        "ingredients": ["egg", "chicken broth", "green onion", "sesame oil", "soy sauce", "cornstarch", "ginger"],
        "required": ["egg", "chicken broth"],
        "time": "15 min",
        "difficulty": "Easy",
    },
    {
        "name": "Fried Egg Rice Bowl",
        "emoji": "🍚",
        "description": "A fried egg over a bowl of hot rice with soy sauce and sesame oil. The simplest satisfying meal possible.",
        "ingredients": ["rice", "egg", "soy sauce", "sesame oil", "green onion", "butter"],
        "required": ["rice", "egg"],
        "time": "15 min",
        "difficulty": "Easy",
    },
    {
        "name": "Tomato Rice",
        "emoji": "🍅",
        "description": "Rice cooked in spiced tomato — a one-pot comfort meal with bold flavor and minimal cleanup.",
        "ingredients": ["rice", "tomato", "onion", "garlic", "cumin", "oil", "chicken broth", "cilantro"],
        "required": ["rice", "tomato", "onion"],
        "time": "30 min",
        "difficulty": "Easy",
    },
    {
        "name": "Pasta Carbonara",
        "emoji": "🍝",
        "description": "A Roman classic — silky egg and cheese sauce coating hot pasta with crispy bacon. Rich and indulgent.",
        "ingredients": ["pasta", "egg", "parmesan", "bacon", "garlic", "black pepper", "salt"],
        "required": ["pasta", "egg", "parmesan", "bacon"],
        "time": "25 min",
        "difficulty": "Medium",
    },
    {
        "name": "Chicken Quesadilla",
        "emoji": "🌮",
        "description": "Shredded chicken and melted cheese in a crispy tortilla. Serve with salsa and sour cream.",
        "ingredients": ["tortilla", "chicken", "cheese", "onion", "bell pepper", "cumin", "butter", "salsa"],
        "required": ["tortilla", "chicken", "cheese"],
        "time": "20 min",
        "difficulty": "Easy",
    },
    {
        "name": "Mushroom Risotto",
        "emoji": "🍄",
        "description": "Creamy, velvety risotto with earthy mushrooms. Takes patience but the result is restaurant-quality.",
        "ingredients": ["arborio rice", "mushroom", "onion", "garlic", "butter", "parmesan", "white wine", "chicken broth", "olive oil"],
        "required": ["arborio rice", "mushroom", "onion"],
        "time": "45 min",
        "difficulty": "Hard",
    },
    {
        "name": "Sweet Potato Mash",
        "emoji": "🍠",
        "description": "Fluffy, sweet mashed sweet potatoes with butter and a pinch of cinnamon. A perfect comforting side dish.",
        "ingredients": ["sweet potato", "butter", "milk", "cinnamon", "salt", "brown sugar"],
        "required": ["sweet potato", "butter"],
        "time": "30 min",
        "difficulty": "Easy",
    },
    {
        "name": "Greek Salad",
        "emoji": "🥗",
        "description": "Crisp vegetables, olives, and feta in a tangy olive oil dressing. Fresh, easy, and no cooking required.",
        "ingredients": ["tomato", "cucumber", "red onion", "feta", "olives", "olive oil", "lemon", "oregano"],
        "required": ["tomato", "cucumber", "feta"],
        "time": "10 min",
        "difficulty": "Easy",
    },
    {
        "name": "Chickpea Stew",
        "emoji": "🥘",
        "description": "A hearty, protein-rich stew with chickpeas in a spiced tomato base. Delicious with crusty bread.",
        "ingredients": ["chickpeas", "tomato", "onion", "garlic", "cumin", "paprika", "olive oil", "spinach", "lemon"],
        "required": ["chickpeas", "tomato", "onion"],
        "time": "30 min",
        "difficulty": "Easy",
    },
    {
        "name": "Banana Oat Cookies",
        "emoji": "🍪",
        "description": "Two-ingredient cookies made from banana and oats. No sugar, no flour — surprisingly delicious.",
        "ingredients": ["banana", "oats", "chocolate chips", "peanut butter", "cinnamon"],
        "required": ["banana", "oats"],
        "time": "20 min",
        "difficulty": "Easy",
    },
    {
        "name": "Caprese Salad",
        "emoji": "🍅",
        "description": "Sliced tomatoes and mozzarella layered with fresh basil and a drizzle of olive oil. Italian simplicity at its best.",
        "ingredients": ["tomato", "mozzarella", "basil", "olive oil", "balsamic vinegar", "salt", "pepper"],
        "required": ["tomato", "mozzarella", "basil"],
        "time": "10 min",
        "difficulty": "Easy",
    },
    {
        "name": "Sausage & Pepper Pasta",
        "emoji": "🌶️",
        "description": "Spicy Italian sausage with sweet peppers and onions over pasta. A bold, satisfying dinner.",
        "ingredients": ["pasta", "sausage", "bell pepper", "onion", "garlic", "tomato", "olive oil", "parmesan"],
        "required": ["pasta", "sausage", "bell pepper"],
        "time": "35 min",
        "difficulty": "Medium",
    },
    {
        "name": "Ramen Upgrade",
        "emoji": "🍜",
        "description": "Instant ramen transformed with a soft egg, soy sauce, and whatever toppings you have. Way better than the packet.",
        "ingredients": ["ramen", "egg", "soy sauce", "green onion", "garlic", "sesame oil", "butter", "corn"],
        "required": ["ramen", "egg"],
        "time": "15 min",
        "difficulty": "Easy",
    },
    {
        "name": "Veggie Fried Rice",
        "emoji": "🍚",
        "description": "Colorful vegetables stir-fried with rice and egg in a savory soy sauce. A great way to clear the fridge.",
        "ingredients": ["rice", "egg", "carrot", "peas", "corn", "onion", "soy sauce", "garlic", "sesame oil", "oil"],
        "required": ["rice", "egg", "soy sauce"],
        "time": "20 min",
        "difficulty": "Easy",
    },
    {
        "name": "Oatmeal",
        "emoji": "🥣",
        "description": "Creamy stovetop oatmeal topped with fruit, honey, and nuts. Fueling and fast.",
        "ingredients": ["oats", "milk", "banana", "honey", "cinnamon", "almonds", "butter"],
        "required": ["oats", "milk"],
        "time": "10 min",
        "difficulty": "Easy",
    },
    {
        "name": "Taco Bowl",
        "emoji": "🌮",
        "description": "Seasoned ground beef over rice with all your favorite taco fixings. A deconstructed taco in a bowl.",
        "ingredients": ["ground beef", "rice", "taco seasoning", "cheese", "sour cream", "salsa", "lettuce", "tomato", "lime"],
        "required": ["ground beef", "rice"],
        "time": "30 min",
        "difficulty": "Easy",
    },
    {
        "name": "Egg Salad Sandwich",
        "emoji": "🥚",
        "description": "Creamy egg salad with mustard and herbs tucked between soft bread. Classic deli-style at home.",
        "ingredients": ["egg", "bread", "mayonnaise", "mustard", "celery", "onion", "salt", "pepper"],
        "required": ["egg", "bread", "mayonnaise"],
        "time": "15 min",
        "difficulty": "Easy",
    },
    {
        "name": "Mashed Potatoes",
        "emoji": "🥔",
        "description": "Fluffy, buttery mashed potatoes — the ultimate comfort side dish. Goes with almost anything.",
        "ingredients": ["potato", "butter", "milk", "salt", "pepper", "garlic", "chives"],
        "required": ["potato", "butter", "milk"],
        "time": "30 min",
        "difficulty": "Easy",
    },
    {
        "name": "Cheese & Veggie Frittata",
        "emoji": "🧆",
        "description": "A baked egg dish loaded with vegetables and cheese. Like a crustless quiche — great for any meal.",
        "ingredients": ["egg", "cheese", "spinach", "onion", "bell pepper", "milk", "garlic", "olive oil", "salt"],
        "required": ["egg", "cheese", "milk"],
        "time": "35 min",
        "difficulty": "Medium",
    },
    {
        "name": "Pita Pizza",
        "emoji": "🍕",
        "description": "Crispy pita topped with tomato sauce, cheese, and whatever toppings you have. Pizza night, no dough required.",
        "ingredients": ["pita", "tomato sauce", "cheese", "olive oil", "basil", "garlic", "oregano"],
        "required": ["pita", "tomato sauce", "cheese"],
        "time": "15 min",
        "difficulty": "Easy",
    },
    {
        "name": "Steak & Eggs",
        "emoji": "🥩",
        "description": "A classic hearty plate of pan-seared steak with fried eggs. Simple, protein-packed, and delicious.",
        "ingredients": ["steak", "egg", "butter", "garlic", "salt", "pepper", "rosemary"],
        "required": ["steak", "egg", "butter"],
        "time": "20 min",
        "difficulty": "Medium",
    },
]

# =============================================================================
#  INGREDIENT MATCHING ENGINE
# =============================================================================

# Common words to strip so "half an onion" → "onion"
STOP_WORDS = {
    "a", "an", "the", "some", "bit", "of", "half", "few", "couple",
    "small", "large", "big", "medium", "fresh", "frozen", "canned",
    "leftover", "cooked", "raw", "diced", "chopped", "sliced",
    "cup", "cups", "tbsp", "tsp", "oz", "lb", "lbs", "pound", "pounds",
    "can", "jar", "bag", "bunch", "head", "clove", "cloves", "piece",
    "pieces", "and", "or", "with", "random", "misc", "various",
}

def normalize(text: str) -> str:
    """Lowercase, strip punctuation, remove stop words."""
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    tokens = [t for t in text.split() if t not in STOP_WORDS and len(t) > 1]
    return " ".join(tokens)

def fuzzy_match(a: str, b: str) -> float:
    """Return similarity ratio between two strings (0–1)."""
    return SequenceMatcher(None, a, b).ratio()

def ingredient_matches(user_ingredient: str, recipe_ingredient: str) -> bool:
    """
    Return True if a user ingredient matches a recipe ingredient.
    Uses substring and fuzzy matching to handle typos / partial names.
    e.g. "chix" matches "chicken", "soy" matches "soy sauce"
    """
    u = normalize(user_ingredient)
    r = normalize(recipe_ingredient)

    if not u or not r:
        return False

    # Exact match
    if u == r:
        return True

    # Substring match (either direction)
    if u in r or r in u:
        return True

    # Fuzzy match for short words (handles typos)
    if fuzzy_match(u, r) >= 0.80:
        return True

    # Word-level overlap: any single word in user matches any word in recipe
    u_words = set(u.split())
    r_words = set(r.split())
    if u_words & r_words:
        return True

    return False

def parse_user_ingredients(raw):
    """Split raw user text into individual ingredient tokens."""
    # Split on commas, semicolons, newlines, 'and'
    parts = re.split(r"[,;\n]+|\band\b", raw, flags=re.IGNORECASE)
    cleaned = []
    for part in parts:
        part = part.strip()
        if part:
            cleaned.append(part)
    return cleaned

def score_recipe(user_ingredients, recipe):
    """
    Score a recipe against the user's ingredient list.
    Returns None if the recipe can't be made at all (too few matches).
    """
    recipe_ings = recipe["ingredients"]
    required_ings = recipe.get("required", [])

    # Find which recipe ingredients the user has
    matched = []
    missing = []

    for r_ing in recipe_ings:
        found = any(ingredient_matches(u, r_ing) for u in user_ingredients)
        if found:
            matched.append(r_ing)
        else:
            missing.append(r_ing)

    total = len(recipe_ings)
    match_count = len(matched)
    coverage = match_count / total if total else 0

    # Check required ingredients — must have at least half of them
    required_matched = sum(
        1 for req in required_ings
        if any(ingredient_matches(u, req) for u in user_ingredients)
    )
    required_ratio = required_matched / len(required_ings) if required_ings else 1.0

    # Drop recipes where the user has fewer than 2 ingredients OR
    # less than 40% coverage OR less than half the required ingredients
    if match_count < 1 or coverage < 0.20 or required_ratio < 0.40:
        return None

    # Score: weighted sum of coverage and required-ingredient ratio
    score = (coverage * 0.6) + (required_ratio * 0.4)

    return {
        "name": recipe["name"],
        "emoji": recipe["emoji"],
        "description": recipe["description"],
        "usedIngredients": matched,
        "missingIngredients": missing,
        "time": recipe["time"],
        "difficulty": recipe["difficulty"],
        "score": score,
    }

def find_best_meals(raw_input, top_n=3):
    """Parse user input and return the top N recipe matches."""
    user_ingredients = parse_user_ingredients(raw_input)

    if not user_ingredients:
        return []

    scored = []
    for recipe in RECIPES:
        result = score_recipe(user_ingredients, recipe)
        if result:
            scored.append(result)

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)

    # Remove the internal score key before returning
    top = scored[:top_n]
    for meal in top:
        del meal["score"]

    return top

# =============================================================================
#  HTML FRONTEND (same visual style as before)
# =============================================================================

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PantryPal</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,400;0,600;0,800;1,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #faf6ef; font-family: 'DM Sans', sans-serif; min-height: 100vh; }

  .blob { position: fixed; border-radius: 50%; filter: blur(90px); opacity: 0.18; pointer-events: none; z-index: 0; }
  .blob-1 { width: 520px; height: 520px; background: #c97d4e; top: -160px; right: -160px; }
  .blob-2 { width: 420px; height: 420px; background: #6b8f60; bottom: 80px; left: -130px; }

  .wrap { position: relative; z-index: 1; max-width: 980px; margin: 0 auto; padding: 0 20px 80px; }

  .header { text-align: center; padding: 52px 0 30px; animation: fadeDown .6s ease both; }
  .logo-row { display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 8px; }
  .logo-icon { font-size: 44px; animation: wobble 3.5s ease-in-out infinite; }
  @keyframes wobble { 0%,100% { transform: rotate(-5deg); } 50% { transform: rotate(5deg); } }
  .title { font-family: 'Fraunces', serif; font-size: clamp(42px, 7vw, 62px); font-weight: 800; color: #2c1f0e; letter-spacing: -1.5px; line-height: 1; }
  .subtitle { font-size: 16px; color: #7a6650; font-weight: 300; max-width: 430px; margin: 0 auto; line-height: 1.65; }
  .no-ai-badge { display: inline-block; margin-top: 12px; background: #edf7ed; border: 1.5px solid #b6d9b6; color: #3a7a3a; font-size: 12px; font-weight: 500; padding: 5px 14px; border-radius: 999px; }

  .input-card { max-width: 640px; margin: 0 auto 44px; background: #fff9f2; border: 1.5px solid #e8ddd0; border-radius: 22px; padding: 28px; box-shadow: 0 8px 40px rgba(100,60,20,.08); animation: fadeUp .7s .15s ease both; }
  .card-label { font-family: 'Fraunces', serif; font-size: 18px; color: #2c1f0e; margin-bottom: 6px; display: block; }
  .card-hint { font-size: 13px; color: #9e8b78; font-style: italic; margin-bottom: 14px; }
  textarea { width: 100%; min-height: 110px; background: #faf6ef; border: 1.5px solid #ddd0c3; border-radius: 12px; padding: 14px 16px; font-family: 'DM Sans', sans-serif; font-size: 15px; color: #2c1f0e; resize: vertical; outline: none; line-height: 1.65; transition: border-color .2s, box-shadow .2s; }
  textarea:focus { border-color: #c97d4e; box-shadow: 0 0 0 3px rgba(201,125,78,.15); }
  textarea::placeholder { color: #bfb0a0; }
  .btn { margin-top: 16px; width: 100%; padding: 15px; background: #2c1f0e; color: #faf6ef; font-family: 'Fraunces', serif; font-size: 17px; font-weight: 700; border: none; border-radius: 13px; cursor: pointer; transition: transform .15s, background .2s, box-shadow .2s; }
  .btn:hover:not(:disabled) { background: #c97d4e; transform: translateY(-2px); box-shadow: 0 8px 24px rgba(201,125,78,.35); }
  .btn:disabled { opacity: .55; cursor: not-allowed; transform: none; }

  .loading { display: none; text-align: center; padding: 38px; animation: fadeUp .4s ease both; }
  .spinner { display: inline-block; width: 48px; height: 48px; border: 3px solid #e8ddd0; border-top-color: #c97d4e; border-radius: 50%; animation: spin .9s linear infinite; margin-bottom: 14px; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .loading p { font-family: 'Fraunces', serif; font-size: 18px; color: #7a6650; font-style: italic; }

  .error-box { display: none; max-width: 560px; margin: 0 auto 24px; background: #fff0ec; border: 1.5px solid #f5c4b8; color: #a03020; border-radius: 13px; padding: 15px 20px; font-size: 14px; text-align: center; }

  .results-title { display: none; font-family: 'Fraunces', serif; font-size: 26px; color: #2c1f0e; text-align: center; margin-bottom: 26px; animation: fadeUp .5s ease both; }
  .results-title span { color: #c97d4e; }

  .no-results { display: none; text-align: center; max-width: 500px; margin: 0 auto; background: #fff9f2; border: 1.5px solid #e8ddd0; border-radius: 16px; padding: 28px; }
  .no-results h3 { font-family: 'Fraunces', serif; font-size: 20px; color: #2c1f0e; margin-bottom: 10px; }
  .no-results p { font-size: 14px; color: #7a6650; line-height: 1.6; }

  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(270px, 1fr)); gap: 20px; }

  .flip-wrapper { perspective: 1200px; height: 355px; cursor: pointer; animation: fadeUp .5s ease both; }
  .flip-wrapper:nth-child(2) { animation-delay: .1s; }
  .flip-wrapper:nth-child(3) { animation-delay: .2s; }

  .flip-inner { position: relative; width: 100%; height: 100%; transform-style: preserve-3d; transition: transform .55s cubic-bezier(.4,0,.2,1); }
  .flip-inner.flipped { transform: rotateY(180deg); }

  .face { position: absolute; inset: 0; backface-visibility: hidden; border-radius: 18px; padding: 24px; border: 1.5px solid #e8ddd0; box-shadow: 0 5px 24px rgba(100,60,20,.08); transition: box-shadow .2s; }
  .face:hover { box-shadow: 0 10px 36px rgba(100,60,20,.14); }

  .front { background: #fff9f2; }
  .meal-emoji { font-size: 50px; display: block; margin-bottom: 10px; }
  .meal-name { font-family: 'Fraunces', serif; font-size: 21px; color: #2c1f0e; margin-bottom: 8px; line-height: 1.2; }
  .meal-desc { font-size: 13.5px; color: #7a6650; line-height: 1.65; margin-bottom: 14px; }
  .meta { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
  .badge { font-size: 12px; font-weight: 500; padding: 4px 11px; border-radius: 999px; background: #f0e8dc; color: #6b4f30; }
  .badge-diff { font-size: 12px; font-weight: 500; padding: 4px 11px; border-radius: 999px; color: #fff; }
  .flip-hint { position: absolute; bottom: 15px; right: 18px; font-size: 11.5px; color: #bfb0a0; font-style: italic; }

  .back { background: #2c1f0e; color: #faf6ef; transform: rotateY(180deg); }
  .back-section-title { font-size: 10px; color: #c97d4e; text-transform: uppercase; letter-spacing: .8px; font-weight: 600; margin-bottom: 7px; }
  .back-section-title + .tag-row { margin-bottom: 14px; }
  .tag-row { display: flex; flex-wrap: wrap; gap: 5px; }
  .tag { font-size: 12px; padding: 4px 10px; border-radius: 999px; }
  .tag-have { background: rgba(76,175,125,.2); color: #7ef5b0; }
  .tag-need { background: rgba(240,165,0,.2); color: #f0c84e; }
  .all-good { font-size: 13px; color: #7ef5b0; margin-top: 10px; }
  .back-hint { position: absolute; bottom: 15px; right: 18px; font-size: 11.5px; color: #7a6650; font-style: italic; }

  @keyframes fadeDown { from { opacity: 0; transform: translateY(-22px); } to { opacity: 1; transform: translateY(0); } }
  @keyframes fadeUp   { from { opacity: 0; transform: translateY(26px);  } to { opacity: 1; transform: translateY(0); } }
</style>
</head>
<body>
<div class="blob blob-1"></div>
<div class="blob blob-2"></div>
<div class="wrap">

  <header class="header">
    <div class="logo-row">
      <span class="logo-icon">🥘</span>
      <h1 class="title">PantryPal</h1>
    </div>
    <p class="subtitle">Type what's in your fridge. We'll find meals you can make right now.</p>
    <span class="no-ai-badge">⚡ 100% local — no AI, no API, no internet needed</span>
  </header>

  <div class="input-card">
    <label class="card-label" for="ingInput">What do you have?</label>
    <p class="card-hint">e.g. "eggs, rice, half an onion, soy sauce, garlic, leftover chicken"</p>
    <textarea id="ingInput" placeholder="List your ingredients here…"></textarea>
    <button class="btn" id="suggestBtn" onclick="getSuggestions()">🔍 Find Meals</button>
  </div>

  <div class="loading" id="loadingDiv">
    <div class="spinner"></div>
    <p>Checking your pantry…</p>
  </div>
  <div class="error-box" id="errorDiv"></div>

  <h2 class="results-title" id="resultsTitle">Best matches for your ingredients</h2>
  <div class="no-results" id="noResults">
    <h3>😅 No matches found</h3>
    <p>Try adding more ingredients — even basics like oil, salt, butter, or eggs help a lot!</p>
  </div>
  <div class="grid" id="grid"></div>

</div>

<script>
const DIFF_COLOR = { Easy: '#4caf7d', Medium: '#f0a500', Hard: '#e05a3a' };
let flipState = {};

async function getSuggestions() {
  const ing = document.getElementById('ingInput').value.trim();
  if (!ing) return;

  document.getElementById('suggestBtn').disabled = true;
  document.getElementById('loadingDiv').style.display = 'block';
  document.getElementById('errorDiv').style.display  = 'none';
  document.getElementById('resultsTitle').style.display = 'none';
  document.getElementById('noResults').style.display   = 'none';
  document.getElementById('grid').innerHTML = '';
  flipState = {};

  try {
    const res  = await fetch('/suggest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ingredients: ing })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Server error');

    if (data.meals.length === 0) {
      document.getElementById('noResults').style.display = 'block';
    } else {
      renderMeals(data.meals);
    }
  } catch (e) {
    const err = document.getElementById('errorDiv');
    err.style.display = 'block';
    err.textContent   = '⚠️ ' + e.message;
  }

  document.getElementById('loadingDiv').style.display = 'none';
  document.getElementById('suggestBtn').disabled = false;
}

function renderMeals(meals) {
  document.getElementById('resultsTitle').style.display = 'block';
  const grid = document.getElementById('grid');

  meals.forEach((m, i) => {
    const wrapper   = document.createElement('div');
    wrapper.className = 'flip-wrapper';
    wrapper.onclick = () => {
      flipState[i] = !flipState[i];
      inner.classList.toggle('flipped', flipState[i]);
    };

    const inner     = document.createElement('div');
    inner.className = 'flip-inner';

    const used    = m.usedIngredients    || [];
    const missing = m.missingIngredients || [];
    const diff    = m.difficulty || 'Easy';

    inner.innerHTML = `
      <div class="face front">
        <span class="meal-emoji">${m.emoji}</span>
        <div class="meal-name">${m.name}</div>
        <p class="meal-desc">${m.description}</p>
        <div class="meta">
          <span class="badge">⏱ ${m.time}</span>
          <span class="badge-diff" style="background:${DIFF_COLOR[diff] || '#888'}">${diff}</span>
        </div>
        <span class="flip-hint">Tap for ingredients →</span>
      </div>
      <div class="face back">
        <p class="back-section-title">✅ You have</p>
        <div class="tag-row">${used.map(t => '<span class="tag tag-have">'+t+'</span>').join('')}</div>
        ${missing.length > 0
          ? '<p class="back-section-title">🛒 You\'ll also need</p><div class="tag-row">'
            + missing.map(t => '<span class="tag tag-need">'+t+'</span>').join('')
            + '</div>'
          : '<p class="all-good">🎉 You have everything!</p>'}
        <span class="back-hint">← Tap to go back</span>
      </div>`;

    wrapper.appendChild(inner);
    grid.appendChild(wrapper);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('ingInput').addEventListener('keydown', e => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) getSuggestions();
  });
});
</script>
</body>
</html>"""


# =============================================================================
#  FLASK ROUTES
# =============================================================================

@app.route("/")
def index():
    return HTML_PAGE


@app.route("/suggest", methods=["POST"])
def suggest():
    data        = request.get_json(silent=True) or {}
    ingredients = data.get("ingredients", "").strip()

    if not ingredients:
        return jsonify({"error": "No ingredients provided"}), 400

    meals = find_best_meals(ingredients, top_n=3)
    return jsonify({"meals": meals})


# =============================================================================
#  ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print("\n🥘  PantryPal is running! (Pure Python — no AI, no API key)")
    print("   Open your browser at: http://localhost:5000")
    print("   Press Ctrl+C to stop.\n")
    app.run(debug=True, port=5000)
