import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import warnings

warnings.filterwarnings('ignore')

# File path (update this as needed)
file_path = r"C:\Users\amans\Downloads\Assesment\DA_Task_2.xlsx"

# Just load the file
def load_excel(path):
    return pd.read_excel(path)

# Quick data overview
def explore_data(df):
    print(f"\nDataset: {df.shape[0]} rows x {df.shape[1]} cols\n")
    for col in df.columns:
        print(f"{col}: {df[col].dtype}, {df[col].nunique()} unique")
        if df[col].isnull().sum():
            print(f" - Missing: {df[col].isnull().sum()}")
        if df[col].dtype in ['int64', 'float64']:
            print(f" - Range: {df[col].min()} → {df[col].max()}")

# Fill missing and normalize
def clean_up(df):
    df_clean = df.copy()
    for col in df_clean.columns:
        if df_clean[col].isnull().sum():
            if df_clean[col].dtype in ['int64', 'float64']:
                df_clean[col].fillna(df_clean[col].median(), inplace=True)
            else:
                df_clean[col].fillna(df_clean[col].mode()[0], inplace=True)
    # Basic text cleaning
    obj_cols = df_clean.select_dtypes(include='object').columns
    for col in obj_cols:
        df_clean[col] = df_clean[col].astype(str).str.strip().str.upper()
    return df_clean

# Pick out useful columns manually or heuristically
def select_key_columns(df):
    importance = {}
    for col in df.columns:
        score = 0
        if 'complaint' in col.lower() or 'cause' in col.lower():
            score += 10
        if df[col].dtype in ['int64', 'float64'] and df[col].isnull().sum() < len(df)*0.1:
            score += 5
        importance[col] = score
    top_cols = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5]
    return [col for col, _ in top_cols]

# Show some visuals
def draw_charts(df, key_cols):
    plt.figure(figsize=(12, 4))
    col1 = key_cols[0]

    plt.subplot(1, 2, 1)
    if df[col1].dtype == 'object':
        df[col1].value_counts().head(5).plot(kind='bar')
        plt.title(f'{col1} Distribution')
    else:
        sns.histplot(df[col1], kde=True)
        plt.title(f'{col1} Histogram')

    plt.subplot(1, 2, 2)
    num_cols = df.select_dtypes(include=[np.number])
    if len(num_cols.columns) > 1:
        sns.heatmap(num_cols.corr(), annot=True, cmap='coolwarm')
        plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.show()

# Very basic keyword extraction
def tag_text_fields(df):
    tags = {}
    keywords = {
        "failures": ['leak', 'fail', 'crack', 'noise'],
        "components": ['engine', 'battery', 'fuel', 'brake'],
        "actions": ['replace', 'repair', 'fix']
    }

    for col in df.select_dtypes(include='object').columns:
        text = ' '.join(df[col].astype(str)).lower()
        tags[col] = {
            k: [word for word in wordlist if word in text]
            for k, wordlist in keywords.items()
        }
    return tags

def report_findings(df, tags):
    print("\n--- Summary ---")
    print(f"Total records: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    fail_list = sum([v['failures'] for v in tags.values()], [])
    if fail_list:
        common_fail = Counter(fail_list).most_common(1)[0]
        print(f"Most frequent failure type: {common_fail[0]}")
    comp_list = sum([v['components'] for v in tags.values()], [])
    if comp_list:
        common_comp = Counter(comp_list).most_common(1)[0]
        print(f"Most affected component: {common_comp[0]}")

    print("\nSuggestions:")
    print("- Focus on recurring failure types")
    print("- Improve components with frequent issues")
    print("- Clean data entry errors early to avoid downstream issues")

def run_analysis():
    try:
        df = load_excel(file_path)
        explore_data(df)
        cleaned = clean_up(df)
        top_cols = select_key_columns(cleaned)
        draw_charts(cleaned, top_cols)
        tags = tag_text_fields(cleaned)
        report_findings(cleaned, tags)
        cleaned.to_csv('cleaned_dataset.csv', index=False)
        print("Cleaned data saved as 'cleaned_dataset.csv'")
    except Exception as e:
        print(f"Something went wrong: {e}")

if __name__ == "__main__":
    run_analysis()
