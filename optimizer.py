import google.generativeai as genai
import json
import os

def check_api_key_validity(api_key):
    """Check if the provided Gemini API key is valid by running a lightweight request."""
    if not api_key:
        return False
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        # Try a quick prompt
        model.generate_content("test")
        return True
    except Exception:
        return False

def get_gemini_optimizer(original_prompt, target_model, category, tone, length, api_key=None):
    """
    Optimize the user's prompt using the Gemini API.
    If no API key is available or the call fails, falls back to a high-quality mockup system.
    """
    # Fetch key from parameter or environment
    key = api_key or os.environ.get("GEMINI_API_KEY")
    
    if not key:
        return get_mock_optimization(original_prompt, target_model, category, tone, length, "API key is missing. Using pre-configured mockup optimizer.")
    
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        system_instruction = (
            "You are a master Prompt Engineer specializing in optimizing prompts for AI models. "
            "Your task is to take a vague, simple prompt and rewrite it to be highly effective, structured, "
            "and tailored to the user's specified criteria: target model, category, tone, and length.\n\n"
            "You must return ONLY a JSON object that strictly adheres to the following structure:\n"
            "{\n"
            '  "optimized_prompt": "string (the fully rewritten prompt. Include markdown structure, headers, clear instructions)",\n'
            '  "score": integer (overall quality score 0-100),\n'
            '  "score_details": {\n'
            '    "clarity": integer (0-100),\n'
            '    "context": integer (0-100),\n'
            '    "specificity": integer (0-100),\n'
            '    "structure": integer (0-100),\n'
            '    "completeness": integer (0-100)\n'
            "  },\n"
            '  "why_better": {\n'
            '    "context": "string explaining how context was added or improved",\n'
            '    "objective": "string explaining how the main objective was clarified",\n'
            '    "formatting": "string explaining the structural improvements made (markdown, sections, bullet points)",\n'
            '    "specifics": "string explaining additional constraints or specific rules added",\n'
            '    "suitability": "string explaining why the prompt is optimized specifically for the target model"\n'
            "  },\n"
            '  "suggestions": "string containing 2-3 brief tips for the user on how they can improve prompts of this type"\n'
            "}"
        )
        
        user_prompt = (
            f"Original Prompt: {original_prompt}\n"
            f"Target Model: {target_model}\n"
            f"Category: {category}\n"
            f"Tone: {tone}\n"
            f"Output Length: {length}\n\n"
            "Analyze and optimize the prompt above. Return the structured JSON content."
        )
        
        response = model.generate_content(
            contents=user_prompt,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.2
            },
            system_instruction=system_instruction
        )
        
        # Parse the JSON response
        result = json.loads(response.text)
        return result
        
    except Exception as e:
        error_msg = f"Gemini API request failed ({str(e)}). Falling back to mock optimizer."
        return get_mock_optimization(original_prompt, target_model, category, tone, length, error_msg)

def get_mock_optimization(original_prompt, target_model, category, tone, length, reason=""):
    """Provide a realistic mock response when Gemini API is unavailable or key is invalid."""
    
    # Simple rule-based mock prompt builder
    length_desc = "detailed and comprehensive" if length == "Detailed" else "concise" if length == "Short" else "balanced"
    
    role = f"Act as a professional in the field of {category}." if category != "General" else "Act as an experienced AI assistant."
    
    if target_model == "GitHub Copilot" or category == "Coding":
        optimized = (
            f"# Target Model: {target_model} (Tone: {tone})\n"
            f"# Context: {category} coding helper\n\n"
            f"{role}\n"
            f"Write a highly robust, documented, and clean implementation of: '{original_prompt}'.\n\n"
            f"## Requirements\n"
            f"- Output syntax-valid code with comments explaining design choices.\n"
            f"- Implement proper error handling, input validation, and edge-case checks.\n"
            f"- Keep the code structure modular and highly optimized.\n"
            f"- Use style guidelines appropriate for the language.\n\n"
            f"## Return Format\n"
            f"- Provide the complete script code block first, followed by a brief summary of how it works."
        )
    elif target_model in ["Midjourney", "DALL·E"] or category == "Image Generation":
        optimized = (
            f"A high-resolution, detailed image prompt for {target_model}:\n\n"
            f"'{original_prompt}', cinematic lighting, octane render, 8k resolution, highly detailed, photorealistic, "
            f"vibrant color palette, masterfully composed, shot on 35mm lens, depth of field, {tone.lower()} style, "
            f"ideal aspect ratio 16:9 --v 6.0"
        )
    else:
        optimized = (
            f"## Role\n"
            f"{role} Use a {tone.lower()} tone to address the objective.\n\n"
            f"## Objective\n"
            f"Execute the following task: '{original_prompt}'. Make sure the response is {length_desc}.\n\n"
            f"## Key Constraints & Instructions\n"
            f"1. Structure the response using logical markdown sections with headers and lists.\n"
            f"2. Add relevant context, explaining any complex concepts clearly.\n"
            f"3. Eliminate boilerplate text and deliver high-value, actionable material.\n"
            f"4. Tailor formatting specifically for reading on {target_model}.\n\n"
            f"## Expected Output Format\n"
            f"- **Introduction**: Brief summary of the core answer.\n"
            f"- **Main Sections**: Ordered detailed points.\n"
            f"- **Key Takeaway**: A single summarizing sentence."
        )

    # Let's compute a mock quality score based on length of input prompt
    # Vague prompts have lower quality score
    input_len = len(original_prompt.split())
    if input_len <= 2:
        clarity_score = 30
        context_score = 20
        specificity_score = 15
        structure_score = 25
        completeness_score = 10
    elif input_len <= 5:
        clarity_score = 50
        context_score = 45
        specificity_score = 40
        structure_score = 45
        completeness_score = 35
    else:
        clarity_score = 70
        context_score = 60
        specificity_score = 65
        structure_score = 55
        completeness_score = 50
        
    overall_score = int((clarity_score + context_score + specificity_score + structure_score + completeness_score) / 5)

    why_better_data = {
        "context": f"Added role play context: '{role}' to guide model responses.",
        "objective": f"Clarified target goal: '{original_prompt}' with explicit structure.",
        "formatting": "Introduced structured Markdown headings and checklist requirements.",
        "specifics": f"Demanded {length_desc} length, error checks, and eliminated boilerplate text.",
        "suitability": f"Formatted output structure to fit the parsing limits and conversational context of {target_model}."
    }

    return {
        "optimized_prompt": optimized,
        "score": overall_score,
        "score_details": {
            "clarity": clarity_score,
            "context": context_score,
            "specificity": specificity_score,
            "structure": structure_score,
            "completeness": completeness_score
        },
        "why_better": why_better_data,
        "suggestions": "Try adding specific target audiences and output formats to your initial prompt to raise the starting quality score.",
        "mock_notice": reason if reason else "Using mock optimizer (Offline mode)"
    }
