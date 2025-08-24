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
    You may include arguments in the "args" field if needed.
    Example output: {{"action": "move", "args": {{"direction": "north"}}}}
    Second example: {{"action": "attack_guard", "args": {{"combatant": "guard"}}}}
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
            return {"action": "help", "args": {}}

    def parse_example(self):
        actions_in_city = ["move", "look", "talk", "inventory"]
        player_input = "I try to hit the guard"
        parsed = self.parse_action(player_input, actions_in_city)
        print(parsed)

    def narrate_action(self, action: dict, game_state: dict) -> str:
        """
        Generate narration for a parsed action and update game state if needed.
        
        Args:
            action (dict): { "tool": str, "args": dict }
            game_state (dict): dictionary storing the current game state
        
        Returns:
            narration (str): What the narrator says
        """
        
        tool = action.get("tool", "look")
        args = action.get("args", {})

        # Create a dynamic prompt
        prompt = f"""
    You are the narrator for a text RPG.
    The world state is: {json.dumps(game_state)}.
    The player has chosen the action: {tool} with arguments {args}.
    Write a short narration (2-3 sentences max) describing what happens next.
    Keep it immersive and consistent with the world state.
    Suggest a few possible actions, just narration.
    """
        
        response = ollama.chat(
            model="phi3",
            messages=[
                {"role": "system", "content": prompt}
            ]
        )
        
        return response["message"]["content"]


AI = AI_Control()
AI.parse_example()
