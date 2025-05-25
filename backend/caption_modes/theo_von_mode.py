"""
Theo Von Mode - Transforms captions into Theo Von's absurd Southern storytelling style
"""

def get_theo_von_mode_prompt() -> str:
    return """Rewrite this caption in Theo Von's comedic style. Use his characteristic:
- Bizarre Southern metaphors and comparisons
- Random personal anecdotes that may or may not be true
- Louisiana/Southern expressions
- Absurd analogies that somehow make sense
- Self-deprecating humor
- Stream-of-consciousness tangents
- References to growing up in Louisiana
- Weird observations about life

Example:
Original: "The man walked into the store."
Transformed: "That fella just moseyed into that store like a possum wandering into a church potluck, you know? Reminds me of this time in Covington when my uncle Gary walked into a Blockbuster thinking it was a dentist office, bless his heart."
"""

def transform_to_theo_von_mode(text: str) -> str:
    """Quick Theo Von style transformations"""
    theo_phrases = [
        "bless his heart",
        "you know what I'm saying?",
        "that's wild, dude",
        "reminds me of this time in Louisiana",
        "like a possum in a prayer meeting",
        "wilder than a roadhouse on payday",
        "that's some real stuff right there"
    ]
    
    # Add Theo-style commentary
    import random
    if len(text) > 30:
        phrase = random.choice(theo_phrases)
        return f"{text}, {phrase}"
    else:
        return f"{text}, you know what I'm saying?"
