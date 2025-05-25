"""
Weed Mode - Transforms captions into chill, stoner-friendly language
"""

def get_weed_mode_prompt() -> str:
    return """Transform this caption into a chill, stoner-friendly version. Use slang like "dude", "man", "totally", "like", "whoa", etc. Make it sound relaxed and casual, like someone who's high is describing what's happening. 

Guidelines:
- Use simple, laid-back language
- Add filler words like "like", "you know", "man"
- Replace complex words with simpler alternatives
- Keep the core meaning but make it sound chill
- Add appropriate stoner expressions
- Keep it appropriate and not offensive

Example:
Original: "The detective carefully examined the evidence."
Transformed: "Dude, the detective was like, totally checking out all that evidence, man."
"""

def transform_to_weed_mode(text: str) -> str:
    """
    Apply weed mode transformation rules locally for quick processing
    """
    # Simple transformations for common words/phrases
    replacements = {
        'said': 'was like',
        'quickly': 'real quick',
        'suddenly': 'all of a sudden, dude',
        'immediately': 'right away, man',
        'carefully': 'real careful like',
        'obviously': 'totally',
        'definitely': 'for sure',
        'probably': 'probably, you know',
        'amazing': 'totally awesome',
        'terrible': 'super bogus',
        'angry': 'all mad and stuff',
        'excited': 'totally stoked',
        'surprised': 'like, whoa',
        'confused': 'all confused and stuff'
    }
    
    transformed = text
    for old, new in replacements.items():
        transformed = transformed.replace(old, new)
    
    # Add some stoner filler words
    if not any(word in transformed.lower() for word in ['dude', 'man', 'like']):
        if len(transformed) > 20:
            transformed = f"Like, {transformed}, man"
        else:
            transformed = f"{transformed}, dude"
    
    return transformed
