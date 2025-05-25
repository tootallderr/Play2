"""
Trivia Mode - Adds interesting trivia and fun facts to captions
"""

def get_trivia_mode_prompt() -> str:
    return """Add interesting trivia or fun facts related to anything mentioned in this caption. Include brief tidbits in brackets like [Fun fact: ...] or [Did you know: ...]. 

Guidelines:
- Keep facts relevant to people, places, objects, or concepts mentioned
- Make trivia entertaining and educational
- Use formats like [Fun fact: ...], [Did you know: ...], [Trivia: ...]
- Don't overwhelm the original caption
- Focus on surprising or little-known facts
- Keep additions concise (1-2 sentences max)

Example:
Original: "The detective examined the fingerprints."
Transformed: "The detective examined the fingerprints. [Fun fact: No two people have identical fingerprints, not even identical twins!]"
"""

def transform_to_trivia_mode(text: str) -> str:
    """Add trivia based on common words/concepts"""
    trivia_facts = {
        "phone": "[Fun fact: The first mobile phone weighed 2.2 pounds!]",
        "coffee": "[Did you know: Coffee was originally discovered by goats in Ethiopia?]",
        "pizza": "[Trivia: Americans eat 3 billion pizzas per year!]",
        "car": "[Fun fact: The average car has over 30,000 parts!]",
        "computer": "[Did you know: The first computer bug was an actual bug - a moth!]",
        "book": "[Trivia: The smell of old books comes from vanilla-scented compounds!]",
        "music": "[Fun fact: Music can reduce physical pain by up to 25%!]",
        "water": "[Did you know: Water can exist as liquid, solid, and gas simultaneously!]",
        "heart": "[Trivia: Your heart beats about 100,000 times per day!]",
        "brain": "[Fun fact: Your brain uses 20% of your body's total energy!]"
    }
    
    result = text
    text_lower = text.lower()
    
    for keyword, trivia in trivia_facts.items():
        if keyword in text_lower:
            result = f"{text} {trivia}"
            break
    
    return result
