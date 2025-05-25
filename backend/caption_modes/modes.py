"""
Caption Modes - All caption transformation modes in one file
Easy to add new modes or modify existing ones
"""

import random
from typing import Dict, Callable

class CaptionModes:
    """Central hub for all caption transformation modes"""
    
    @staticmethod
    def get_all_modes() -> Dict[str, Dict[str, str]]:
        """
        Get all available caption modes with their prompts and descriptions
        
        Returns:
            Dict with mode names as keys and mode info as values
        """
        return {
            'original': {
                'name': 'Original',
                'description': 'Keep captions unchanged',
                'prompt': ''
            },
            'joey_diaz': {
                'name': 'Joey Diaz',
                'description': 'Transform into Joey Diaz\'s explosive storytelling style',
                'prompt': """Transform this caption into Joey Diaz's explosive storytelling style. Include his characteristic:
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
Transformed: "Listen to me, this lady's in there making dinner like my mother used to do back in North Bergen, I'm telling you! Reminds me of Sunday gravy, tremendous stuff!\""""
            },
            'theo_von': {
                'name': 'Theo Von',
                'description': 'Transform into Theo Von\'s absurd Southern storytelling style',
                'prompt': """Rewrite this caption in Theo Von's comedic style. Use his characteristic:
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
Transformed: "That fella just moseyed into that store like a possum wandering into a church potluck, you know? Reminds me of this time in Covington when my uncle Gary walked into a Blockbuster thinking it was a dentist office, bless his heart.\""""
            },
            'fact_check': {
                'name': 'Fact Check',
                'description': 'Add fact-checking annotations to captions',
                'prompt': """For this caption, add brief fact-checks or clarifications in brackets after any claims that might be historically, scientifically, or factually questionable. 

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
Transformed: "The Great Wall of China is visible from space. [❌ Incorrect: Not visible to naked eye from space]\""""
            },
            'trivia': {
                'name': 'Trivia',
                'description': 'Add interesting trivia and fun facts to captions',
                'prompt': """Add interesting trivia or fun facts related to anything mentioned in this caption. Include brief tidbits in brackets like [Fun fact: ...] or [Did you know: ...]. 

Guidelines:
- Keep facts relevant to people, places, objects, or concepts mentioned
- Make trivia entertaining and educational
- Use formats like [Fun fact: ...], [Did you know: ...], [Trivia: ...]
- Don't overwhelm the original caption
- Focus on surprising or little-known facts
- Keep additions concise (1-2 sentences max)

Example:
Original: "The detective examined the fingerprints."
Transformed: "The detective examined the fingerprints. [Fun fact: No two people have identical fingerprints, not even identical twins!]\""""
            },
            'weed': {
                'name': 'Chill/Stoner',
                'description': 'Transform into chill, stoner-friendly language',
                'prompt': """Transform this caption into a chill, stoner-friendly version. Use slang like "dude", "man", "totally", "like", "whoa", etc. Make it sound relaxed and casual, like someone who's high is describing what's happening. 

Guidelines:
- Use simple, laid-back language
- Add filler words like "like", "you know", "man"
- Replace complex words with simpler alternatives
- Keep the core meaning but make it sound chill
- Add appropriate stoner expressions
- Keep it appropriate and not offensive

Example:
Original: "The detective carefully examined the evidence."
Transformed: "Dude, the detective was like, totally checking out all that evidence, man.\""""
            },
            'pirate': {
                'name': 'Pirate',
                'description': 'Transform into pirate speak (Arr matey!)',
                'prompt': """Transform this caption into pirate speak. Use pirate vocabulary and expressions like:
- "Arr", "Ahoy", "Avast", "Ye", "Matey"
- Replace "you" with "ye", "your" with "yer"
- Add nautical terms where appropriate
- Keep the meaning but make it sound like a pirate is speaking
- Use phrases like "shiver me timbers", "batten down the hatches", etc.

Example:
Original: "The man opened the treasure chest."
Transformed: "Arr! The scurvy dog opened the treasure chest, he did! Shiver me timbers!\""""
            },
            'shakespearean': {
                'name': 'Shakespearean',
                'description': 'Transform into Shakespearean/Elizabethan English',
                'prompt': """Transform this caption into Shakespearean/Elizabethan English style. Use:
- "Thou", "thee", "thy", "thine" instead of "you", "your"
- "-eth" verb endings where appropriate
- Flowery, poetic language
- "Prithee", "forsooth", "verily", "hark", etc.
- More elaborate sentence structures
- Keep the meaning but make it sound like Shakespeare wrote it

Example:
Original: "The woman was singing beautifully."
Transformed: "Verily, the fair maiden doth sing with such beauteous voice that angels themselves would weep with joy!\""""
            },
            'narrator': {
                'name': 'David Attenborough',
                'description': 'Transform into nature documentary narration style',
                'prompt': """Transform this caption into David Attenborough-style nature documentary narration. Use:
- Scientific observation tone
- Phrases like "Here we observe", "In the wild", "Remarkable behavior"
- Educational and descriptive language
- Sense of wonder and discovery
- British documentary style
- Treat everyday human behavior like fascinating animal behavior

Example:
Original: "The man was eating pizza."
Transformed: "Here we observe the male human in his natural habitat, engaging in the ancient ritual of pizza consumption. Remarkable how he uses primitive tools to transfer sustenance to his mouth - truly fascinating behavior.\""""
            }
        }
    
    @staticmethod
    def get_quick_transforms() -> Dict[str, Callable[[str], str]]:
        """
        Get quick transformation functions for fallback/offline processing
        
        Returns:
            Dict with mode names and their quick transform functions
        """
        return {
            'joey_diaz': CaptionModes._quick_joey_diaz,
            'theo_von': CaptionModes._quick_theo_von,
            'fact_check': CaptionModes._quick_fact_check,
            'trivia': CaptionModes._quick_trivia,
            'weed': CaptionModes._quick_weed,
            'pirate': CaptionModes._quick_pirate,
            'shakespearean': CaptionModes._quick_shakespearean,
            'narrator': CaptionModes._quick_narrator
        }
    
    @staticmethod
    def _quick_joey_diaz(text: str) -> str:
        """Quick Joey Diaz style transformation"""
        starters = ["Listen to me,", "I'm telling you,", "Back in the day,", "Let me tell you something,"]
        enders = ["tremendous!", "I'm telling you!", "like you read about!", "unbelievable stuff!"]
        
        starter = random.choice(starters)
        ender = random.choice(enders)
        return f"{starter} {text.lower()} - {ender}"
    
    @staticmethod
    def _quick_theo_von(text: str) -> str:
        """Quick Theo Von style transformation"""
        phrases = [
            "bless his heart", "you know what I'm saying?", "that's wild, dude",
            "reminds me of this time in Louisiana", "like a possum in a prayer meeting",
            "wilder than a roadhouse on payday", "that's some real stuff right there"
        ]
        
        if len(text) > 30:
            phrase = random.choice(phrases)
            return f"{text}, {phrase}"
        else:
            return f"{text}, you know what I'm saying?"
    
    @staticmethod
    def _quick_fact_check(text: str) -> str:
        """Quick fact-checking transformation"""
        fact_checks = {
            "visible from space": "[❌ Incorrect: Not visible to naked eye from space]",
            "only uses 10% of brain": "[❌ Incorrect: Humans use virtually all of their brain]",
            "lightning never strikes twice": "[❌ Incorrect: Lightning often strikes the same place repeatedly]",
            "goldfish have 3-second memory": "[❌ Incorrect: Goldfish memory lasts months, not seconds]",
            "cracking knuckles causes arthritis": "[❌ Incorrect: No scientific evidence linking knuckle cracking to arthritis]"
        }
        
        for claim, check in fact_checks.items():
            if claim.lower() in text.lower():
                return f"{text} {check}"
        return text
    
    @staticmethod
    def _quick_trivia(text: str) -> str:
        """Quick trivia transformation"""
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
        
        text_lower = text.lower()
        for keyword, trivia in trivia_facts.items():
            if keyword in text_lower:
                return f"{text} {trivia}"
        return text
    
    @staticmethod
    def _quick_weed(text: str) -> str:
        """Quick weed/chill transformation"""
        replacements = {
            'said': 'was like', 'quickly': 'real quick', 'suddenly': 'all of a sudden, dude',
            'immediately': 'right away, man', 'carefully': 'real careful like', 'obviously': 'totally',
            'definitely': 'for sure', 'probably': 'probably, you know', 'amazing': 'totally awesome',
            'terrible': 'super bogus', 'angry': 'all mad and stuff', 'excited': 'totally stoked',
            'surprised': 'like, whoa', 'confused': 'all confused and stuff'
        }
        
        transformed = text
        for old, new in replacements.items():
            transformed = transformed.replace(old, new)
        
        # Add stoner filler if not present
        if not any(word in transformed.lower() for word in ['dude', 'man', 'like']):
            transformed = f"Like, {transformed}, man" if len(transformed) > 20 else f"{transformed}, dude"
        
        return transformed
    
    @staticmethod
    def _quick_pirate(text: str) -> str:
        """Quick pirate transformation"""
        replacements = {
            ' you ': ' ye ', ' your ': ' yer ', 'You ': 'Ye ', 'Your ': 'Yer ',
            'the ': 'the ', 'hello': 'ahoy', 'yes': 'aye', 'no': 'nay'
        }
        
        transformed = text
        for old, new in replacements.items():
            transformed = transformed.replace(old, new)
        
        pirate_starters = ["Arr!", "Ahoy!", "Avast!"]
        pirate_enders = ["matey!", "ye scurvy dog!", "shiver me timbers!"]
        
        starter = random.choice(pirate_starters)
        ender = random.choice(pirate_enders)
        
        return f"{starter} {transformed}, {ender}"
    
    @staticmethod
    def _quick_shakespearean(text: str) -> str:
        """Quick Shakespearean transformation"""
        replacements = {
            ' you ': ' thou ', ' your ': ' thy ', 'You ': 'Thou ', 'Your ': 'Thy ',
            ' are ': ' art ', ' is ': ' doth be ', 'have ': 'hath '
        }
        
        transformed = text
        for old, new in replacements.items():
            transformed = transformed.replace(old, new)
        
        if not transformed.startswith(('Verily', 'Forsooth', 'Prithee')):
            starters = ["Verily,", "Forsooth,", "Prithee,", "Hark!"]
            starter = random.choice(starters)
            transformed = f"{starter} {transformed.lower()}"
        
        return transformed
    
    @staticmethod
    def _quick_narrator(text: str) -> str:
        """Quick nature documentary narrator transformation"""
        starters = [
            "Here we observe", "In the wild", "Fascinating behavior shows us",
            "Remarkable footage reveals", "Nature demonstrates"
        ]
        
        enders = [
            "- truly remarkable behavior", "- absolutely fascinating",
            "- extraordinary to witness", "- magnificent creatures indeed"
        ]
        
        starter = random.choice(starters)
        ender = random.choice(enders)
        
        return f"{starter} {text.lower()}{ender}."

# Convenience functions for backward compatibility
def get_joey_diaz_mode_prompt() -> str:
    return CaptionModes.get_all_modes()['joey_diaz']['prompt']

def get_theo_von_mode_prompt() -> str:
    return CaptionModes.get_all_modes()['theo_von']['prompt']

def get_fact_check_mode_prompt() -> str:
    return CaptionModes.get_all_modes()['fact_check']['prompt']

def get_trivia_mode_prompt() -> str:
    return CaptionModes.get_all_modes()['trivia']['prompt']

def get_weed_mode_prompt() -> str:
    return CaptionModes.get_all_modes()['weed']['prompt']

# Quick transform functions for backward compatibility
def transform_to_joey_diaz_mode(text: str) -> str:
    return CaptionModes._quick_joey_diaz(text)

def transform_to_theo_von_mode(text: str) -> str:
    return CaptionModes._quick_theo_von(text)

def transform_to_fact_check_mode(text: str) -> str:
    return CaptionModes._quick_fact_check(text)

def transform_to_trivia_mode(text: str) -> str:
    return CaptionModes._quick_trivia(text)

def transform_to_weed_mode(text: str) -> str:
    return CaptionModes._quick_weed(text)
