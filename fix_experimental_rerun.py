#!/usr/bin/env python3
"""
Script to replace st.experimental_rerun() with st.rerun() across all Python files
"""

import os
import re

def fix_experimental_rerun():
    """Replace st.experimental_rerun() with st.rerun() in all Python files"""
    
    # Get current directory
    current_dir = os.getcwd()
    
    # Pattern to match st.experimental_rerun()
    pattern = r'st\.experimental_rerun\(\)'
    replacement = 'st.rerun()'
    
    # Files to process
    files_to_fix = [
        'app.py',
        'voice_pay_page.py',
        'savings_goals_page.py',
        'emotion_insights_page.py',
        'subscriptions_page.py',
        'budget_alerts_page.py',
        'financial_assistant_page.py',
        'expense_prediction_page.py',
        'scan_receipt_page.py',
        'financial_health_page.py',
        'pay_later_page.py',
        'investment_tracker_page.py',
        'qr_code_page.py',
        'spending_challenge_page.py',
        'fraud_detection_page.py',
        'cashback_page.py',
        'spending_heatmap_page.py'
    ]
    
    fixed_files = []
    
    for filename in files_to_fix:
        filepath = os.path.join(current_dir, filename)
        
        if os.path.exists(filepath):
            try:
                # Read the file
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if file contains experimental_rerun
                if 'experimental_rerun' in content:
                    # Replace all occurrences
                    new_content = re.sub(pattern, replacement, content)
                    
                    # Write back to file
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    # Count replacements
                    count = len(re.findall(pattern, content))
                    fixed_files.append((filename, count))
                    print(f"Fixed {count} occurrences in {filename}")
                    
            except Exception as e:
                print(f"Error processing {filename}: {e}")
        else:
            print(f"File not found: {filename}")
    
    if fixed_files:
        print("\nSummary:")
        total_fixes = 0
        for filename, count in fixed_files:
            print(f"  {filename}: {count} replacements")
            total_fixes += count
        print(f"\nTotal replacements: {total_fixes}")
    else:
        print("No files needed fixing.")

if __name__ == "__main__":
    print("Fixing st.experimental_rerun() calls...")
    fix_experimental_rerun()
    print("Done!")