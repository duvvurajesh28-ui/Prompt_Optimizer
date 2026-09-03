# Module-level unit tests for Prompt Optimizer AI backend services.
# Verifies SQLite operations, prompt scoring logic, PDF export compile, and Mock optimizations.

import os
import shutil
import database as db
import prompt_scorer
import utils
import optimizer

def run_tests():
    print("==================================================")
    print("       STARTING BACKEND SERVICE UNIT TESTS        ")
    print("==================================================")
    
    # 1. Test Rule-based Scorer
    print("\n[1/4] Testing Prompt Quality Scorer...")
    vague_prompt = "write a resume"
    vague_score = prompt_scorer.calculate_initial_score(vague_prompt)
    print(f"Vague Prompt: '{vague_prompt}' | Calculated Score: {vague_score['overall']}/100")
    
    detailed_prompt = "Act as an ATS resume reviewer. Create an outline for a Senior React developer resume. Include skills, experience, and projects."
    detailed_score = prompt_scorer.calculate_initial_score(detailed_prompt)
    print(f"Detailed Prompt: '{detailed_prompt[:40]}...' | Calculated Score: {detailed_score['overall']}/100")
    
    assert detailed_score['overall'] > vague_score['overall'], "Detailed prompt should score higher than vague prompt"
    print("[SUCCESS] Scorer logic works successfully!")

    # 2. Test SQLite Database
    print("\n[2/4] Testing SQLite database functions...")
    # Initialize DB (which sets up path)
    db.init_db()
    print(f"DB initialized at: {db.DB_PATH}")
    assert os.path.exists(db.DB_PATH), "Database file should exist"
    
    # Insert Test Prompt
    inserted_id = db.save_prompt(
        original_prompt="test original",
        optimized_prompt="test optimized",
        model="ChatGPT",
        category="Coding",
        tone="Technical",
        length="Medium",
        score=85,
        score_details={"clarity": 80, "context": 90, "specificity": 80, "structure": 90, "completeness": 85},
        why_better={"formatting": "Tested grid structure", "context": "Added compiler context"}
    )
    print(f"Inserted test prompt. Primary Key returned: {inserted_id}")
    assert inserted_id is not None, "Inserted row ID should be returned"
    
    # Fetch History
    history = db.get_history()
    print(f"Retrieved history. Records found: {len(history)}")
    assert len(history) > 0, "History should contain at least 1 record"
    assert history[0]["original_prompt"] == "test original", "Retrieved prompt contents should match"
    
    # Toggle Favorite
    new_fav_status = db.toggle_favorite(inserted_id)
    print(f"Toggled favorite status. New status: {new_fav_status}")
    assert new_fav_status == 1, "Favorite status should toggle to 1"
    
    # Stats
    stats = db.get_stats()
    print(f"Gathered metrics - Total: {stats['total_prompts']}, Avg Score: {stats['avg_score']}, Favorites: {stats['favorites_count']}")
    assert stats["total_prompts"] > 0, "Total count should be greater than zero"
    assert stats["favorites_count"] == 1, "Favorites count should be exactly 1"
    
    # Delete Test Prompt
    db.delete_prompt(inserted_id)
    post_delete_history = db.get_history()
    assert len(post_delete_history) < len(history), "Record count should decrease after deletion"
    print("[SUCCESS] SQLite integration works successfully!")

    # 3. Test PDF compiler
    print("\n[3/4] Testing ReportLab PDF compiler...")
    pdf_bytes = utils.generate_pdf_report(
        original="Test draft",
        optimized="Act as a compiler.\nCompile this file.",
        model="Gemini",
        category="General",
        tone="Professional",
        length="Short",
        score=90,
        score_details={"clarity": 90, "context": 90, "specificity": 90, "structure": 90, "completeness": 90},
        why_better={"context": "Clean test case context", "formatting": "Clean borders"}
    )
    print(f"Generated PDF bytes length: {len(pdf_bytes)} bytes")
    assert len(pdf_bytes) > 0, "Generated PDF should have non-zero size"
    print("[SUCCESS] PDF generation compiled successfully!")

    # 4. Test Mock Optimizer
    print("\n[4/4] Testing Mock Optimization Fallback...")
    mock_res = optimizer.get_mock_optimization(
        original_prompt="hello world",
        target_model="ChatGPT",
        category="General",
        tone="Friendly",
        length="Short"
    )
    print("Mock Optimization response contains keys:", list(mock_res.keys()))
    assert "optimized_prompt" in mock_res, "Mock response must contain optimized prompt text"
    assert "score" in mock_res, "Mock response must contain score"
    print("[SUCCESS] Mock Optimizer behaves successfully!")
    
    print("\n==================================================")
    print("       ALL SERVICE MODULE TESTS COMPLETED         ")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
