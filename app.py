import streamlit as st
import os
import pandas as pd
import json
from datetime import datetime

# Import local modules
import database as db
import optimizer
import prompt_scorer
import templates
import utils

# Page Configuration
st.set_page_config(
    page_title="Prompt Optimizer AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database
db.init_db()

# Load Custom CSS
CSS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "style.css")
if os.path.exists(CSS_PATH):
    with open(CSS_PATH, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Session State Initialization
if "prompt_input" not in st.session_state:
    st.session_state.prompt_input = ""
if "last_optimized" not in st.session_state:
    st.session_state.last_optimized = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard 🚀"
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "Gemini"
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "General"
if "selected_tone" not in st.session_state:
    st.session_state.selected_tone = "Professional"
if "selected_length" not in st.session_state:
    st.session_state.selected_length = "Medium"
if "voice_active" not in st.session_state:
    st.session_state.voice_active = False

# Callback to set input text from templates
def load_template(prompt_text, category, model_default="ChatGPT"):
    st.session_state.prompt_input = prompt_text
    st.session_state.selected_category = category
    st.session_state.selected_model = model_default
    # Reset last optimized so they see the new prompt first
    st.session_state.last_optimized = None

# Sidebar Content
with st.sidebar:
    st.markdown('<div class="main-header" style="font-size:1.8rem !important; text-align:left;">✨ PromptAI</div>', unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 0.9rem; margin-top:-10px; margin-bottom: 20px;'>Transform simple prompts into masterpieces</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation Menus
    st.markdown("### Navigation")
    pages = ["Dashboard 🚀", "History ⏳", "Statistics 📊"]
    
    for p in pages:
        if st.button(p, key=f"nav_{p}", use_container_width=True, 
                     type="primary" if st.session_state.current_page == p else "secondary"):
            st.session_state.current_page = p
            st.rerun()
            
    st.markdown("---")
    
    # API Key Configuration
    st.markdown("### API Settings")
    api_key_env = os.environ.get("GEMINI_API_KEY", "")
    has_env_key = len(api_key_env) > 0
    
    key_placeholder = "••••••••••••••••" if has_env_key else "Enter Gemini API Key..."
    user_api_key = st.text_input("Gemini API Key", type="password", placeholder=key_placeholder, help="Enter your Google Gemini API key. If left blank, we fallback to the environment key or a smart offline mock optimizer.")
    
    api_key_to_use = user_api_key if user_api_key else api_key_env
    
    if api_key_to_use:
        st.success("API key configured! (Gemini Live Mode)")
    else:
        st.info("No API key set. Running in Smart Offline Mock Mode.")
        
    st.markdown("---")
    
    # Predefined Templates Section
    st.markdown("### Quick Templates")
    st.write("Click a template to load it instantly:")
    
    for category_name, details in templates.TEMPLATES.items():
        # Standard templates
        label = f"{details['icon']} {category_name}"
        if st.button(label, key=f"tpl_{category_name}", use_container_width=True):
            # Midjourney / DALL-E default to Midjourney model, others to Gemini/ChatGPT
            default_model = "Midjourney" if category_name == "Image Prompt" else "Gemini"
            load_template(details["prompt"], details["category"], default_model)
            st.toast(f"Loaded {category_name} template!")
            st.rerun()

# ----------------- MAIN PAGES -----------------

# Page 1: Dashboard
if st.session_state.current_page == "Dashboard 🚀":
    st.markdown('<div class="main-header">Prompt Optimizer AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Upgrade your AI interactions with clear, structured, and contextual prompt variations</div>', unsafe_allow_html=True)
    
    # Main Form Area
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📝 Draft Your Prompt</div>', unsafe_allow_html=True)
        
        # Audio Input Feature
        audio_col1, audio_col2 = st.columns([5, 1])
        with audio_col1:
            prompt_input = st.text_area(
                "Simple Vague Prompt",
                value=st.session_state.prompt_input,
                height=120,
                placeholder="Example: Write a resume... or Create a python function...",
                label_visibility="collapsed"
            )
            st.session_state.prompt_input = prompt_input
        
        with audio_col2:
            st.write("")
            st.write("")
            voice_btn = st.button("🎙️ Voice Input", use_container_width=True)
            if voice_btn:
                # Simulating voice transcription for portfolio-ready bonus feature
                st.session_state.prompt_input = "Act as an investment analyst and summarize the latest trends in renewable energy stocks."
                st.toast("Simulated Voice Input: 'Act as an investment analyst...'")
                st.rerun()
                
        # Word Counter
        word_count = len(prompt_input.strip().split()) if prompt_input else 0
        st.markdown(f"<p style='color: #64748b; font-size: 0.8rem; text-align: right; margin-top: -10px;'>Word Count: {word_count} | Characters: {len(prompt_input)}</p>", unsafe_allow_html=True)
        
        # Parameters selectors in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            models_list = ["ChatGPT", "Gemini", "Claude", "Midjourney", "DALL·E", "GitHub Copilot"]
            # Keep index matching session state
            sel_model_idx = models_list.index(st.session_state.selected_model) if st.session_state.selected_model in models_list else 1
            selected_model = st.selectbox("AI Model Target", models_list, index=sel_model_idx)
            st.session_state.selected_model = selected_model
            
        with col2:
            categories_list = ["General", "Coding", "Content Writing", "Marketing", "Resume", "Image Generation", "Research", "Education", "Business"]
            sel_cat_idx = categories_list.index(st.session_state.selected_category) if st.session_state.selected_category in categories_list else 0
            selected_category = st.selectbox("Prompt Category", categories_list, index=sel_cat_idx)
            st.session_state.selected_category = selected_category
            
        with col3:
            tones_list = ["Professional", "Friendly", "Creative", "Technical", "Academic", "Formal"]
            sel_tone_idx = tones_list.index(st.session_state.selected_tone) if st.session_state.selected_tone in tones_list else 0
            selected_tone = st.selectbox("Desired Tone", tones_list, index=sel_tone_idx)
            st.session_state.selected_tone = selected_tone
            
        with col4:
            lengths_list = ["Short", "Medium", "Detailed"]
            sel_len_idx = lengths_list.index(st.session_state.selected_length) if st.session_state.selected_length in lengths_list else 1
            selected_length = st.radio("Output Length", lengths_list, index=sel_len_idx, horizontal=True)
            st.session_state.selected_length = selected_length
            
        # Action Buttons
        btn_col1, btn_col2, btn_col3 = st.columns([3, 1, 1])
        
        with btn_col1:
            optimize_btn = st.button("✨ Optimize Prompt", type="primary", use_container_width=True)
            
        with btn_col2:
            clear_btn = st.button("🧹 Clear", use_container_width=True)
            if clear_btn:
                st.session_state.prompt_input = ""
                st.session_state.last_optimized = None
                st.rerun()
                
        with btn_col3:
            # Suggest before optimization bonus feature
            suggest_btn = st.button("💡 Pre-check Suggestion", use_container_width=True)
            if suggest_btn:
                if not prompt_input.strip():
                    st.warning("Please enter a prompt draft first.")
                else:
                    initial_score_data = prompt_scorer.calculate_initial_score(prompt_input)
                    st.session_state.last_optimized = {
                        "pre_check": True,
                        "score_details": initial_score_data,
                        "original_prompt": prompt_input
                    }
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        
    # Process optimization request
    if optimize_btn:
        if not prompt_input.strip():
            st.error("Please enter a prompt to optimize.")
        else:
            with st.spinner("Analyzing and rewriting your prompt using Gemini API..."):
                # Get Optimization result
                result = optimizer.get_gemini_optimizer(
                    original_prompt=prompt_input,
                    target_model=selected_model,
                    category=selected_category,
                    tone=selected_tone,
                    length=selected_length,
                    api_key=api_key_to_use
                )
                
                # Check for mock notice
                if "mock_notice" in result:
                    st.toast(result["mock_notice"], icon="⚠️")
                
                # Calculate initial quality scores locally
                initial_scores = prompt_scorer.calculate_initial_score(prompt_input)
                
                # Bundle optimization result with original details for display
                st.session_state.last_optimized = {
                    "pre_check": False,
                    "original_prompt": prompt_input,
                    "optimized_prompt": result["optimized_prompt"],
                    "score": result["score"],
                    "score_details": result["score_details"],
                    "initial_score_details": initial_scores,
                    "why_better": result["why_better"],
                    "suggestions": result.get("suggestions", ""),
                    "model": selected_model,
                    "category": selected_category,
                    "tone": selected_tone,
                    "length": selected_length
                }
                
                # Save into database history
                try:
                    db.save_prompt(
                        original_prompt=prompt_input,
                        optimized_prompt=result["optimized_prompt"],
                        model=selected_model,
                        category=selected_category,
                        tone=selected_tone,
                        length=selected_length,
                        score=result["score"],
                        score_details=result["score_details"],
                        why_better=result["why_better"]
                    )
                    st.success("Successfully optimized and saved to History!")
                except Exception as e:
                    st.error(f"Failed to save to database history: {str(e)}")
                    
                st.rerun()

    # ---------------- DISPLAY OPTIMIZATION RESULTS ----------------
    opt_data = st.session_state.last_optimized
    
    if opt_data:
        # Check if pre-check suggestion only
        if opt_data.get("pre_check", False):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">💡 Pre-Check Quality Assessment</div>', unsafe_allow_html=True)
            scores = opt_data["score_details"]
            
            st.write("Here is the estimated quality score of your draft prompt:")
            
            # Overall score circle or badge
            score_col, desc_col = st.columns([1, 4])
            with score_col:
                st.metric("Draft Score", f"{scores['overall']}/100")
            with desc_col:
                st.write("")
                if scores["overall"] < 40:
                    st.markdown("<p style='color:#ef4444; font-weight:bold;'>Needs Significant Improvement 🔴</p>", unsafe_allow_html=True)
                    st.write("This prompt is very brief or lacks action-oriented language. It will yield highly generic AI outputs.")
                elif scores["overall"] < 70:
                    st.markdown("<p style='color:#eab308; font-weight:bold;'>Moderate Quality 🟡</p>", unsafe_allow_html=True)
                    st.write("You have defined a task, but adding clear formatting, output structures, or background constraints will improve responses.")
                else:
                    st.markdown("<p style='color:#22c55e; font-weight:bold;'>High Quality 🟢</p>", unsafe_allow_html=True)
                    st.write("Excellent! This prompt already contains details and structural keys. Optimization will polish the formatting.")

            # Metrics Breakdown Bars
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                st.write("Clarity")
                st.progress(scores["clarity"] / 100.0)
                st.write("Context")
                st.progress(scores["context"] / 100.0)
                st.write("Specificity")
                st.progress(scores["specificity"] / 100.0)
            with sub_col2:
                st.write("Structure")
                st.progress(scores["structure"] / 100.0)
                st.write("Completeness")
                st.progress(scores["completeness"] / 100.0)
                
            st.info("Click 'Optimize Prompt' above to generate an enhanced, ready-to-run structure.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            # Full Optimization Report Layout
            st.markdown("---")
            st.markdown('<div class="main-header" style="font-size:2rem !important; margin-bottom:1.5rem;">📊 Optimization Analytics</div>', unsafe_allow_html=True)
            
            # Score comparison
            initial_score = opt_data["initial_score_details"]["overall"]
            final_score = opt_data["score"]
            score_diff = final_score - initial_score
            
            col_sc1, col_sc2 = st.columns(2)
            
            with col_sc1:
                st.markdown('<div class="card" style="text-align: center;">', unsafe_allow_html=True)
                st.markdown("<div class='metric-label'>Original Quality Score</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-value' style='color:#ef4444;'>{initial_score}/100</div>", unsafe_allow_html=True)
                st.progress(initial_score / 100.0)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col_sc2:
                st.markdown('<div class="card" style="text-align: center;">', unsafe_allow_html=True)
                st.markdown("<div class='metric-label'>Optimized Quality Score</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-value' style='color:#10b981;'>{final_score}/100 (+{score_diff})</div>", unsafe_allow_html=True)
                st.progress(final_score / 100.0)
                st.markdown('</div>', unsafe_allow_html=True)

            # Details scoring progression bars
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">🔍 Metric Breakdown Comparison</div>', unsafe_allow_html=True)
            
            metrics = ["clarity", "context", "specificity", "structure", "completeness"]
            
            for m in metrics:
                init_val = opt_data["initial_score_details"].get(m, 0)
                final_val = opt_data["score_details"].get(m, 0)
                diff = final_val - init_val
                
                col_m1, col_m2 = st.columns([1, 4])
                with col_m1:
                    st.markdown(f"**{m.capitalize()}**")
                    st.write(f"Before: {init_val} | After: {final_val}")
                with col_m2:
                    st.write("")
                    st.progress(final_val / 100.0)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Side-by-side prompt comparison
            comp_col1, comp_col2 = st.columns(2)
            
            with comp_col1:
                st.markdown('<div class="card" style="border-left: 5px solid #ef4444; height: 100%;">', unsafe_allow_html=True)
                st.markdown('<div class="card-title" style="color: #ef4444;">🔴 Original Prompt</div>', unsafe_allow_html=True)
                st.markdown(f"<div style='white-space: pre-wrap; font-size: 0.95rem; min-height: 250px;'>{opt_data['original_prompt']}</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with comp_col2:
                st.markdown('<div class="card" style="border-left: 5px solid #10b981; height: 100%;">', unsafe_allow_html=True)
                st.markdown('<div class="card-title" style="color: #10b981;">🟢 Optimized Prompt</div>', unsafe_allow_html=True)
                
                # Show in text area so they can edit it or copy easily
                edited_optimized = st.text_area(
                    "Optimized Version (Editable)",
                    value=opt_data['optimized_prompt'],
                    height=250,
                    label_visibility="collapsed"
                )
                
                # If they edit, we update the data
                if edited_optimized != opt_data['optimized_prompt']:
                    opt_data['optimized_prompt'] = edited_optimized
                    
                st.markdown('</div>', unsafe_allow_html=True)
                
            # Quick actions toolbar under the comparison
            act_col1, act_col2, act_col3, act_col4 = st.columns(4)
            
            with act_col1:
                # Custom HTML script for copying to clipboard using JS to prevent pyperclip failures in headless servers
                # Streamlit doesn't support custom JS easily inside button, but we can write a clean HTML snippet
                html_copy_btn = f"""
                <script>
                function copyText() {{
                    const text = {json.dumps(opt_data['optimized_prompt'])};
                    navigator.clipboard.writeText(text).then(function() {{
                        alert("Prompt copied to clipboard!");
                    }}, function(err) {{
                        alert("Could not copy prompt: " + err);
                    }});
                }}
                </script>
                <button onclick="copyText()" style="
                    width: 100%;
                    background-color: #6366f1;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 8px;
                    font-weight: 600;
                    cursor: pointer;
                    margin-bottom: 10px;
                ">📋 Copy Prompt</button>
                """
                st.components.v1.html(html_copy_btn, height=50)
                
            with act_col2:
                # Download as TXT
                txt_content = utils.generate_txt_report(
                    original=opt_data['original_prompt'],
                    optimized=opt_data['optimized_prompt'],
                    model=opt_data['model'],
                    category=opt_data['category'],
                    tone=opt_data['tone'],
                    length=opt_data['length'],
                    score=opt_data['score'],
                    why_better=opt_data['why_better']
                )
                st.download_button(
                    label="💾 Download TXT",
                    data=txt_content,
                    file_name=f"prompt_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                
            with act_col3:
                # Download as PDF
                pdf_data = utils.generate_pdf_report(
                    original=opt_data['original_prompt'],
                    optimized=opt_data['optimized_prompt'],
                    model=opt_data['model'],
                    category=opt_data['category'],
                    tone=opt_data['tone'],
                    length=opt_data['length'],
                    score=opt_data['score'],
                    score_details=opt_data['score_details'],
                    why_better=opt_data['why_better']
                )
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_data,
                    file_name=f"prompt_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
            with act_col4:
                # Toggle Favorite (since we don't have prompt_id here without querying, we can check the latest inserted prompt)
                if st.button("⭐ Mark Favorite", use_container_width=True):
                    history = db.get_history(limit=1) # Let's fetch history to get last added ID
                    if history:
                        last_id = history[0]["id"]
                        db.toggle_favorite(last_id)
                        st.success("Added to favorites!")
                    else:
                        st.error("No prompt found in history database.")
            
            # Why It Is Better details
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">✔ Why It Is Better</div>', unsafe_allow_html=True)
            
            why_better = opt_data["why_better"]
            if isinstance(why_better, dict):
                col_wb1, col_wb2 = st.columns(2)
                with col_wb1:
                    st.markdown(f"**✔ Added Context**")
                    st.write(why_better.get("context", "Role-play and situational context were injected."))
                    
                    st.markdown(f"**✔ Clear Objective**")
                    st.write(why_better.get("objective", "The core task was separated from structural details."))
                    
                    st.markdown(f"**✔ Specific constraints**")
                    st.write(why_better.get("specifics", "Explicit constraints regarding length and detail limits were defined."))
                with col_wb2:
                    st.markdown(f"**✔ Better Formatting**")
                    st.write(why_better.get("formatting", "Introduced clean Markdown layout headers and lists."))
                    
                    st.markdown(f"**✔ Target Model Suitability**")
                    st.write(why_better.get("suitability", f"Refined rules to fit the specific prompt parsing behavior of {opt_data['model']}."))
            else:
                st.write(why_better)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # AI Suggestions
            if opt_data.get("suggestions"):
                st.markdown('<div class="card" style="background-color: rgba(99, 102, 241, 0.05);">', unsafe_allow_html=True)
                st.markdown('<div class="card-title">💡 Pro Tips for Future Prompts</div>', unsafe_allow_html=True)
                st.write(opt_data["suggestions"])
                st.markdown('</div>', unsafe_allow_html=True)

# Page 2: History
elif st.session_state.current_page == "History ⏳":
    st.markdown('<div class="main-header">Prompt History</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Search, retrieve, favorite, or remove past optimized prompts</div>', unsafe_allow_html=True)
    
    # Filter Row
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        search_query = st.text_input("Search prompts", placeholder="Type keywords...")
    with col_f2:
        categories = ["All", "General", "Coding", "Content Writing", "Marketing", "Resume", "Image Generation", "Research", "Education", "Business"]
        filter_cat = st.selectbox("Filter Category", categories)
    with col_f3:
        models = ["All", "ChatGPT", "Gemini", "Claude", "Midjourney", "DALL·E", "GitHub Copilot"]
        filter_model = st.selectbox("Filter Model", models)
    with col_f4:
        st.write("")
        st.write("")
        only_favs = st.checkbox("⭐ Favorites Only")
        
    # Fetch data
    history = db.get_history(
        search_query=search_query,
        filter_category=filter_cat,
        filter_model=filter_model,
        only_favorites=only_favs
    )
    
    if not history:
        st.info("No matching prompts found in your history.")
    else:
        st.write(f"Found {len(history)} optimization records:")
        
        # Display list of cards
        for item in history:
            is_fav_star = "★" if item["is_favorite"] == 1 else "☆"
            fav_color = "#eab308" if item["is_favorite"] == 1 else "#64748b"
            
            with st.expander(f"{is_fav_star} [{item['created_at']}] {item['category']} prompt optimized for {item['model']} (Score: {item['score']}/100)"):
                # Side-by-side inside expander
                hist_col1, hist_col2 = st.columns(2)
                with hist_col1:
                    st.markdown("**Original Prompt:**")
                    st.code(item["original_prompt"], language="text")
                with hist_col2:
                    st.markdown("**Optimized Prompt:**")
                    st.code(item["optimized_prompt"], language="text")
                    
                # Action buttons inside expander
                sub_btn1, sub_btn2, sub_btn3, sub_btn4 = st.columns(4)
                with sub_btn1:
                    if st.button("📥 Load into Workspace", key=f"load_{item['id']}", use_container_width=True):
                        st.session_state.prompt_input = item["original_prompt"]
                        st.session_state.selected_model = item["model"]
                        st.session_state.selected_category = item["category"]
                        st.session_state.selected_tone = item["tone"]
                        st.session_state.selected_length = item["length"]
                        
                        # Set last optimized so they see it in dashboard
                        st.session_state.last_optimized = {
                            "pre_check": False,
                            "original_prompt": item["original_prompt"],
                            "optimized_prompt": item["optimized_prompt"],
                            "score": item["score"],
                            "score_details": item["score_details"],
                            "initial_score_details": prompt_scorer.calculate_initial_score(item["original_prompt"]),
                            "why_better": item["why_better"],
                            "model": item["model"],
                            "category": item["category"],
                            "tone": item["tone"],
                            "length": item["length"]
                        }
                        st.session_state.current_page = "Dashboard 🚀"
                        st.toast("Loaded history item into dashboard workspace!")
                        st.rerun()
                        
                with sub_btn2:
                    fav_label = "⭐ Unfavorite" if item["is_favorite"] == 1 else "⭐ Favorite"
                    if st.button(fav_label, key=f"fav_{item['id']}", use_container_width=True):
                        db.toggle_favorite(item["id"])
                        st.toast("Updated favorite status!")
                        st.rerun()
                        
                with sub_btn3:
                    if st.button("🗑️ Delete", key=f"del_{item['id']}", use_container_width=True):
                        db.delete_prompt(item["id"])
                        st.toast("Prompt deleted from history.")
                        st.rerun()
                        
                with sub_btn4:
                    # PDF Download
                    pdf_data_item = utils.generate_pdf_report(
                        original=item['original_prompt'],
                        optimized=item['optimized_prompt'],
                        model=item['model'],
                        category=item['category'],
                        tone=item['tone'],
                        length=item['length'],
                        score=item['score'],
                        score_details=item['score_details'],
                        why_better=item['why_better']
                    )
                    st.download_button(
                        label="📄 Download PDF",
                        data=pdf_data_item,
                        file_name=f"prompt_report_{item['id']}.pdf",
                        mime="application/pdf",
                        key=f"dl_pdf_{item['id']}",
                        use_container_width=True
                    )

# Page 3: Statistics Dashboard
elif st.session_state.current_page == "Statistics 📊":
    st.markdown('<div class="main-header">Statistics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Analyze performance metrics and usage details</div>', unsafe_allow_html=True)
    
    # Get stats
    stats = db.get_stats()
    
    if stats["total_prompts"] == 0:
        st.info("Optimize some prompts first to view statistics!")
    else:
        # KPI Row
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        
        with col_s1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{stats["total_prompts"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total Optimized</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_s2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{stats["avg_score"]}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Average Score</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_s3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value" style="font-size:1.4rem !important; line-height:1.8rem; height:1.8rem;">{stats["most_used_category"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Top Category</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_s4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{stats["favorites_count"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Starred Prompts</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Charts section
        st.markdown("### Visual Analytics")
        ch_col1, ch_col2 = st.columns(2)
        
        with ch_col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">📁 Prompts by Category</div>', unsafe_allow_html=True)
            
            # Category Distribution DataFrame
            cat_data = stats["category_distribution"]
            if cat_data:
                df_cat = pd.DataFrame(cat_data)
                df_cat.columns = ["Category", "Total Prompts", "Average Score"]
                # Streamlit bar chart
                st.bar_chart(data=df_cat.set_index("Category")["Total Prompts"], color="#6366f1")
            else:
                st.write("No category data.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with ch_col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">📈 Average Score by Category</div>', unsafe_allow_html=True)
            if cat_data:
                # Average score bar chart
                st.bar_chart(data=df_cat.set_index("Category")["Average Score"], color="#10b981")
            else:
                st.write("No score data.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Optimization volume trend
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📅 Optimization Trend (Last 14 Days)</div>', unsafe_allow_html=True)
        trend_data = stats["trend"]
        if trend_data:
            df_trend = pd.DataFrame(trend_data)
            df_trend.columns = ["Date", "OptimizationsCount"]
            df_trend = df_trend.sort_values("Date")
            st.line_chart(data=df_trend.set_index("Date")["OptimizationsCount"], color="#a855f7")
        else:
            st.write("No timeline trend data yet.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Recent prompts table
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">⏳ Recent Optimizations</div>', unsafe_allow_html=True)
        recent_prompts = stats["recent_prompts"]
        if recent_prompts:
            df_recent = pd.DataFrame(recent_prompts)[["created_at", "category", "model", "score", "original_prompt"]]
            df_recent.columns = ["Timestamp", "Category", "Target Model", "Quality Score", "Snippet"]
            df_recent["Snippet"] = df_recent["Snippet"].apply(lambda x: x[:60] + "..." if len(x) > 60 else x)
            st.dataframe(df_recent, use_container_width=True, hide_index=True)
        else:
            st.write("No recent prompt logs found.")
        st.markdown('</div>', unsafe_allow_html=True)
