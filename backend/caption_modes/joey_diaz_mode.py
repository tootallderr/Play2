"""
Joey Diaz Mode - Transforms captions into Joey Diaz's explosive storytelling style
"""

def get_joey_diaz_mode_prompt() -> str:
    return """Transform this caption into Joey Diaz's explosive storytelling style. Include his characteristic:
- High energy and passion
- Brooklyn/Jersey expressions
- Phrases like "Listen to me", "Back in the day", "I'm telling you"
- Colorful but appropriate language
- Stories about "the old neighborhood"
- Intense delivery style
- References to classic experiences
- Authentic street wisdom

Example:
Original: "The woman was cooking dinner."
Transformed: "Listen to me, this lady's in there making dinner like my mother used to do back in North Bergen, I'm telling you! Reminds me of Sunday gravy, tremendous stuff!"
"""

def transform_to_joey_diaz_mode(text: str) -> str:
    """Quick Joey Diaz style transformations"""
    joey_starters = [
        "Listen to me,",
        "I'm telling you,",
        "Back in the day,",
        "Let me tell you something,"
    ]
    
    joey_enders = [
        "tremendous!",
        "I'm telling you!",
        "like you read about!",
        "unbelievable stuff!"
    ]
    
    import random
    starter = random.choice(joey_starters)
    ender = random.choice(joey_enders)
    
    return f"{starter} {text.lower()} - {ender}"
