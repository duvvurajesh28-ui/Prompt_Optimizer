# Module to score prompt quality locally before and after optimization.

def calculate_initial_score(prompt_text):
    """
    Perform a fast, rule-based analysis of the input prompt's quality.
    Returns a dictionary of detailed scores (0-100) and an overall score.
    """
    if not prompt_text or not prompt_text.strip():
        return {
            "overall": 0,
            "clarity": 0,
            "context": 0,
            "specificity": 0,
            "structure": 0,
            "completeness": 0
        }
        
    words = prompt_text.strip().split()
    word_count = len(words)
    lowercase_text = prompt_text.lower()
    
    # 1. Clarity (0-100): Is it action-oriented?
    action_words = ["write", "create", "generate", "code", "explain", "how", "analyze", "why", "design", "develop", "act as", "simulate"]
    action_score = 30 if any(act in lowercase_text for act in action_words) else 10
    length_bonus_clarity = min(word_count * 3, 70)
    clarity = min(action_score + length_bonus_clarity, 100)
    
    # 2. Context (0-100): Does it supply background?
    context_words = ["role", "persona", "background", "audience", "scenario", "context", "assuming", "imagine", "situation"]
    context_score = 40 if any(ctx in lowercase_text for ctx in context_words) else 10
    length_bonus_context = min(word_count * 2.5, 60)
    context = min(context_score + length_bonus_context, 100)
    
    # 3. Specificity (0-100): Are there exact requirements?
    specificity_indicators = ["specifically", "example", "avoid", "only", "must", "should", "don't", "include", "exclude", "limit"]
    specificity_score = 30 if any(spec in lowercase_text for spec in specificity_indicators) else 10
    has_numbers = 20 if any(char.isdigit() for char in prompt_text) else 0
    length_bonus_specificity = min(word_count * 2, 50)
    specificity = min(specificity_score + has_numbers + length_bonus_specificity, 100)
    
    # 4. Structure (0-100): Is it formatted or bulleted?
    has_newlines = 30 if "\n" in prompt_text else 0
    has_bullets = 30 if any(bullet in prompt_text for bullet in ["- ", "* ", "1.", "2."]) else 0
    length_bonus_structure = min(word_count * 1.5, 40)
    structure = min(has_newlines + has_bullets + length_bonus_structure, 100)
    # Ensure a baseline structure score for minimal text
    structure = max(structure, min(word_count * 4, 40))
    
    # 5. Completeness (0-100): Does it look like a fully fledged prompt?
    completeness = int((clarity + context + specificity + structure) / 4)
    # Deduct if extremely short
    if word_count < 3:
        completeness = max(10, completeness - 40)
    elif word_count < 7:
        completeness = max(20, completeness - 20)
        
    overall = int((clarity + context + specificity + structure + completeness) / 5)
    
    return {
        "overall": overall,
        "clarity": clarity,
        "context": context,
        "specificity": specificity,
        "structure": structure,
        "completeness": completeness
    }
