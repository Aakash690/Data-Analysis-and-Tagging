import pandas as pd
from difflib import get_close_matches

# Load the Excel file
file_path = 'task1_data.xlsx'  # Make sure this file exists in the working directory
xls = pd.ExcelFile(file_path)

# Read input data and taxonomy sheet
tag_data = xls.parse(xls.sheet_names[0])
taxonomy_df = xls.parse('Taxonomy')

# Sanitize taxonomy column names
taxonomy_df.columns = taxonomy_df.columns.str.strip()

# Extract tag lists from taxonomy
root_causes = taxonomy_df['Root Cause'].dropna().unique().tolist()
symptom_conditions = taxonomy_df['Symptom Condition'].dropna().tolist()
symptom_components = taxonomy_df['Symptom Component'].dropna().tolist()
fix_conditions = taxonomy_df['Fix Condition'].dropna().tolist()
fix_components = taxonomy_df['Fix Component'].dropna().tolist()

def fuzzy_match(input_text, reference_list, cutoff=0.6):
    """Returns the closest match from a list based on fuzzy similarity"""
    if not isinstance(input_text, str) or not input_text.strip():
        return "Unknown"
    input_text = input_text.lower().strip()
    match = get_close_matches(input_text, [ref.lower() for ref in reference_list], n=1, cutoff=cutoff)
    if match:
        # Return the original casing from the reference list
        for original in reference_list:
            if original.lower() == match[0]:
                return original
    return "Unknown"

def apply_tags(row):
    """Tags each row with best-matching values from taxonomy"""
    if pd.isna(row.get('Root Cause')):
        row['Root Cause'] = fuzzy_match(row.get('Cause', ''), root_causes)

    if pd.isna(row.get('Symptom Condition 1')):
        row['Symptom Condition 1'] = fuzzy_match(row.get('Complaint', ''), symptom_conditions)

    if pd.isna(row.get('Symptom Component 1')):
        row['Symptom Component 1'] = fuzzy_match(row.get('Complaint', ''), symptom_components)

    if pd.isna(row.get('Fix Condition 1')):
        row['Fix Condition 1'] = fuzzy_match(row.get('Correction', ''), fix_conditions)

    if pd.isna(row.get('Fix Component 1')):
        row['Fix Component 1'] = fuzzy_match(row.get('Correction', ''), fix_components)

    return row

# Apply tagging logic to all rows
tagged_df = tag_data.apply(apply_tags, axis=1)

# Save output to Excel
output_path = 'task1_tagged_output.xlsx'
tagged_df.to_excel(output_path, index=False)

print(f"✅ Tagging complete. Output saved as '{output_path}'")
