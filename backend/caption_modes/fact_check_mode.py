"""
Fact-Check Mode - Adds fact-checking annotations to captions
"""

def get_fact_check_mode_prompt() -> str:
    return """For this caption, add brief fact-checks or clarifications in brackets after any claims that might be historically, scientifically, or factually questionable. 

Guidelines:
- Add [✓ Correct] for accurate statements
- Add [❌ Incorrect: actual fact] for wrong information  
- Add [⚠️ Disputed: brief explanation] for controversial topics
- Add [📊 Context: additional info] for statements needing context
- Keep additions concise and informative
- Don't fact-check obvious fictional content
- Focus on historical dates, scientific claims, statistics, etc.

Example:
Original: "The Great Wall of China is visible from space."
Transformed: "The Great Wall of China is visible from space. [❌ Incorrect: Not visible to naked eye from space]"
"""

def transform_to_fact_check_mode(text: str) -> str:
    """Quick fact-checking transformations for common claims"""
    fact_checks = {
        "visible from space": "[❌ Incorrect: Not visible to naked eye from space]",
        "only uses 10% of brain": "[❌ Incorrect: Humans use virtually all of their brain]",
        "lightning never strikes twice": "[❌ Incorrect: Lightning often strikes the same place repeatedly]",
        "goldfish have 3-second memory": "[❌ Incorrect: Goldfish memory lasts months, not seconds]",
        "cracking knuckles causes arthritis": "[❌ Incorrect: No scientific evidence linking knuckle cracking to arthritis]"
    }
    
    result = text
    for claim, check in fact_checks.items():
        if claim.lower() in text.lower():
            result = f"{text} {check}"
            break
    
    return result
