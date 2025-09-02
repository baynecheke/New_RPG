from httpx import stream
import ollama, json
from textwrap import dedent

class AI_Control:
    def __init__(self,):
        self.action = None

    def parse_choice(self, available_choices, player_text):
        prompt = dedent(f"""
    You are the choice parser for a text RPG.
    The player may only choose from these choices now: {", ".join(available_choices)}.
    Convert the player's input into JSON with one of these actions.
    Return ONLY JSON. Do not invent other actions.
    Return ONLY JSON in the form:
    {{"choice": "<one of the choices>"}}
    """)    
        
        response = ollama.chat(
            model="phi3",
            format="json",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": player_text}
            ]
        )
        try:
            
            parsed = json.loads(response['message']['content'])
            print(parsed.get("choice", "no").lower())
            answer = parsed.get("choice", "none").lower()
            if answer not in (available_choices):
                answer = "none"  # enforce valid fallback
            return answer.strip().lower()
        except json.JSONDecodeError:
            # fallback to a safe default
            self.action = {"choice": "None", }
            return self.action
 
    def parse_YN(self, player_text: str) -> str:
        """
        Parse yes/no answers robustly without using LLMs.
        Always returns 'yes' or 'no'.
        """
        yes_words = {"yes", "y", "yeah", "yep", "sure", "ok", "okay", "affirmative", "of course", "certainly"}
        no_words  = {"no", "n", "nope", "nah", "negative", "never"}

        text = player_text.strip().lower()

        # Direct checks
        if text in yes_words:
            return "yes"
        if text in no_words:
            return "no"

        # Partial matching (covers phrases like "yes please", "sure thing")
        for word in yes_words:
            if word in text:
                return "yes"
        for word in no_words:
            if word in text:
                return "no"

        # Fallback default
        return "no"

    def parse_action(self, player_text: str, available_actions: list):
        prompt = dedent(f"""
        You are an action parser for a text RPG.
        The player may only perform one of these actions: {available_actions}

        Return ONLY JSON in this format:
        {{"action": "one of the available actions"}}
        """)

        response = ollama.chat(
            model="phi3",
            format="json",
            options={"temperature": 0},   # deterministic & faster
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": player_text}
            ]
        )

        try:
            parsed = json.loads(response['message']['content'])
            action = parsed.get("action", "").lower()
            if action not in available_actions:
                action = "help"  # fallback
            self.action = {"action": action}
        except (json.JSONDecodeError, KeyError, TypeError):
            self.action = {"action": "help"}

        return self.action
   
    def parse_dialogue_player(self, player_dialogue, choices: list):
        prompt = dedent(f"""
    You are a dialogue parser for a game.  
    The player is speaking to an NPC.  
    You must choose one of the following actions: {", ".join(choices)}.  

    Return ONLY valid JSON in this format:
    {{"action": "<one_of_choices>"}}

    If the player is not clear, default to:
    {{"action": "talk"}}
    """)
        
        response = ollama.chat(
            model="phi3",
            format="json",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": player_dialogue}
            ]
        )
        try:
            
            self.action = json.loads(response['message']['content'])         # convert to dict

            return self.action
        except json.JSONDecodeError:
            # fallback to a safe default
            self.action = {"action": "talk"}
            return {"action": "talk", }
       

