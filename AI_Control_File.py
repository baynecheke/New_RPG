import ollama, json

class AI_Control:
    def __init__(self):
        pass

    def parse_action(self, player_text: str, available_actions: list):
        prompt = f"""
    You are the action parser for a text RPG.
    The player may only perform these actions now: {available_actions}.
    Convert the player's input into JSON with one of these actions.
    Return ONLY JSON. Do not invent other actions.
    """
        response = ollama.chat(
            model="phi3",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": player_text}
            ]
        )
        try:
            return json.loads(response['message']['content'])
        except json.JSONDecodeError:
            # fallback to a safe default
            return {"tool": "look", "args": {}}

    def parse_example(self):
        actions_in_city = ["move", "look", "talk", "inventory"]
        player_input = "I try to hit the guard"
        parsed = self.parse_action(player_input, actions_in_city)
        print(parsed)
AI = AI_Control()
AI.parse_example()
