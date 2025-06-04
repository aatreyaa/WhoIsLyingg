
from flask import Flask, request, jsonify, render_template
import random
import json
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')

FALLBACK_PROMPTS = {
    "funny": [
        {
            "truth": "What's the weirdest thing you've eaten thinking it was something else?",
            "lie": "What's your favorite snack to eat at movies?"
        },
        {
            "truth": "When was the last time you talked to yourself out loud in public?",
            "lie": "What time do you usually wake up on weekends?"
        },
        {
            "truth": "What's the most ridiculous thing you've done to avoid talking to someone?",
            "lie": "What's your favorite way to spend a rainy day?"
        }
    ],
    "juicy": [
        {
            "truth": "Who in this room would you want to be stuck in an elevator with?",
            "lie": "Who's your favorite actor from the 90s?"
        },
        {
            "truth": "What's the most money you've spent on something completely useless?",
            "lie": "How much do you usually spend on lunch?"
        },
        {
            "truth": "What's your biggest turn-off in a person?",
            "lie": "What's your favorite type of music to work out to?"
        }
    ],
    "spicy": [
        {
            "truth": "What's the most inappropriate place you've ever had romantic thoughts?",
            "lie": "Where's your dream vacation destination?"
        },
        {
            "truth": "How many people have you kissed in one night?",
            "lie": "How many countries have you visited?"
        },
        {
            "truth": "What's your most embarrassing bedroom story?",
            "lie": "What's your most embarrassing cooking disaster?"
        }
    ],
    "embarrassing": [
        {
            "truth": "When was the last time you peed yourself laughing?",
            "lie": "When was the last time you went to bed before 10 PM?"
        },
        {
            "truth": "What's the most embarrassing thing you've done in front of a crush?",
            "lie": "What's the nicest thing you've done for a friend recently?"
        },
        {
            "truth": "Have you ever pretended to be sick to get out of something? What was it?",
            "lie": "Have you ever pretended to like a movie everyone else hated?"
        }
    ]
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_prompt", methods=["POST"])
def get_prompt():
    try:
        data = request.json
        category = data.get('category', 'funny') if data else 'funny'

        category_prompts = {
            "funny": "Generate hilarious, silly questions that will make everyone laugh",
            "juicy": "Generate intriguing, gossip-worthy questions that reveal interesting secrets",
            "spicy": "Generate bold, flirty questions that push boundaries (keep it party-appropriate)",
            "embarrassing": "Generate cringe-worthy, embarrassing questions that will make people blush"
        }

        if openai.api_key:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": f"""Generate a pair of questions for a party game. 
                        Category: {category}
                        {category_prompts.get(category, category_prompts['funny'])}

                        - The 'truth' question should fit the category perfectly
                        - The 'lie' question should be innocent but lead to the same TYPE of answer (number, name, date, color, etc.)
                        - Both answers should sound similar when spoken aloud

                        Return ONLY a JSON object with 'truth' and 'lie' keys."""
                    },
                    {
                        "role": "user", 
                        "content": f"Generate a {category} truth/lie question pair where answers will sound similar"
                    }
                ],
                temperature=0.9,
                max_tokens=200
            )
            content = response.choices[0].message['content'].strip()
            try:
                prompt_data = json.loads(content)
                return jsonify(prompt_data)
            except json.JSONDecodeError:
                return jsonify(random.choice(FALLBACK_PROMPTS.get(category, FALLBACK_PROMPTS['funny'])))
        else:
            return jsonify(random.choice(FALLBACK_PROMPTS.get(category, FALLBACK_PROMPTS['funny'])))
    except Exception as e:
        print(f"Error getting AI prompt: {e}")
        return jsonify(random.choice(FALLBACK_PROMPTS.get('funny')))

@app.route("/determine_winner", methods=["POST"])
def determine_winner():
    data = request.json
    players = data.get('players', [])
    liars = data.get('liars', [])
    did_liars_win = data.get('did_liars_win', False)

    if did_liars_win:
        winners = [players[i] for i in liars]
        winner_type = "Liars"
        message = "successfully fooled everyone!"
    else:
        winners = [players[i] for i in range(len(players)) if i not in liars]
        winner_type = "Truth Tellers"
        message = "caught the liars!"

    return jsonify({
        "winners": winners,
        "winner_type": winner_type,
        "message": message
    })

@app.route("/share_game", methods=["POST"])
def share_game():
    data = request.json
    players = data.get('players', [])
    winners = data.get('winners', [])
    winner_type = data.get('winner_type', '')
    truth_question = data.get('truth', '')

    share_data = {
        "title": "Who Is Lying? 🎭",
        "summary": f"Just played with {len(players)} players!",
        "winners": ", ".join(winners),
        "winner_type": winner_type,
        "question": truth_question,
        "player_count": len(players)
    }

    return jsonify(share_data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
