import pandas as pd
from typing import List, Dict, Optional

class DataTagger:
    def __init__(self):
        # Predefined tag categories (manual taxonomy based on domain knowledge)
        self.tags = {
            'Root_Cause': [
                'Not Tightened', 'Not Installed', 'Not Mentioned', 'Loosened', 'Not Included',
                'Out of Fitting', 'Blown', 'Poor Material', 'Leaking', 'Failed Sending',
                'No O-ring', 'Not Tighten', 'Out of Range', 'Lubricant Drip Down',
                'Fault', 'Internal Issue', 'Screwed in a Thread', 'Faulty'
            ],
            'Symptom_Condition': [
                'Loose', "Won't stay open", 'Crushed', 'Oil Running', 'Missing',
                'Oil Dripping', 'Oil Leak', 'Broke', 'Leak', 'Open', 'Hydraulic Leak',
                'Fold Uneven', 'Getting Fault Code', 'Not Working', 'Error Codes',
                'Product Leak', 'Does not Light'
            ],
            'Symptom_Component': [
                'Gas P-Clip', 'Fuel Door', 'Compressor Pressure Line', 'Not Mentioned',
                'Vector', 'Coupler', 'Mount SVM Sign', 'Harness', 'Rinse Tank',
                'Fuel Sender', 'Boom', 'Auto Boom', 'Condenser', 'Left-Air Duct',
                'Bulkhead Connector', 'Braided Steel', 'Intrip Unlocks', 'Sensor'
            ],
            'Fix_Condition': [
                'Retightened', 'Installed', 'Replaced', 'Topped Off', 'Not Mentioned',
                'Cleaned Out', 'Reseted', 'Repaired', 'Tightened'
            ],
            'Fix_Component': [
                'Gas P-Clip', 'Gas Strut', 'Braided Steel', 'O-Ring', 'Vector',
                'Coupler', 'Brackets', 'Hydraulic', 'Not Mentioned', 'NCV Harness',
                'Tube', 'Sensor', 'Counter', 'Threads', 'Left Air Duct',
                'Compressor Line', 'Intrip Unlocks', 'Bolts', 'Harness',
                'Pipe Fitting', 'Bulkhead Connector', 'SVM Sign', 'ELB'
            ]
        }

        # Keyword-to-tag mappings for matching logic
        self.keyword_map = {
            'tighten': ['Not Tightened', 'Not Tighten'],
            'install': ['Not Installed'],
            'loose': ['Loosened'],
            'missing': ['Missing', 'Not Included'],
            'leak': ['Leaking', 'Leak'],
            'blow': ['Blown'],
            'material': ['Poor Material'],
            'fault': ['Fault', 'Faulty'],
            'o-ring': ['No O-ring'],
            'open': ['Open', "Won't stay open"],
            'crush': ['Crushed'],
            'oil': ['Oil Running', 'Oil Dripping', 'Oil Leak'],
            'broke': ['Broke'],
            'hydraulic': ['Hydraulic Leak'],
            'code': ['Getting Fault Code', 'Error Codes'],
            'work': ['Not Working'],
            'light': ['Does not Light'],
            'door': ['Fuel Door'],
            'clip': ['Gas P-Clip'],
            'pressure': ['Compressor Pressure Line'],
            'harness': ['Harness', 'NCV Harness'],
            'tank': ['Rinse Tank'],
            'boom': ['Boom', 'Auto Boom'],
            'sensor': ['Sensor'],
            'connector': ['Bulkhead Connector'],
            'steel': ['Braided Steel'],
            'replace': ['Replaced'],
            'repair': ['Repaired'],
            'reset': ['Reseted'],
            'tighten_fix': ['Tightened', 'Retightened'],
            'clean': ['Cleaned Out'],
            'top': ['Topped Off']
        }

    def match_tag(self, text: str, category: List[str]) -> str:
        """Attempt to match text with a tag category using exact and keyword-based matching."""
        if not text or pd.isna(text):
            return "Not Mentioned"

        text_lower = text.lower()

        # Try exact match
        for item in category:
            if item.lower() in text_lower:
                return item

        # Try keyword mapping
        for keyword, candidates in self.keyword_map.items():
            if keyword in text_lower:
                for match in candidates:
                    if match in category:
                        return match

        return "Not Mentioned"

    def tag_row(self, complaint: str, cause: str, correction: str) -> Dict[str, str]:
        """Generate tags for a single row of data."""
        return {
            'Root_Cause': self.match_tag(cause, self.tags['Root_Cause']),
            'Symptom_Condition': self.match_tag(complaint, self.tags['Symptom_Condition']),
            'Symptom_Component': self.match_tag(complaint, self.tags['Symptom_Component']),
            'Fix_Condition': self.match_tag(correction, self.tags['Fix_Condition']),
            'Fix_Component': self.match_tag(correction, self.tags['Fix_Component']),
        }

    def tag_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply tagging logic to the full dataset."""
        df_tagged = df.copy()

        for col in ['Root_Cause', 'Symptom_Condition', 'Symptom_Component', 'Fix_Condition', 'Fix_Component']:
            df_tagged[col] = ""

        for index, row in df.iterrows():
            tags = self.tag_row(
                str(row.get('Complaint', '')),
                str(row.get('Cause', '')),
                str(row.get('Correction', ''))
            )
            for k, v in tags.items():
                df_tagged.at[index, k] = v

        return df_tagged


# Example usage
def main():
    sample_data = {
        'Primary_Key': ['SOQ003836-1', 'SOQ003837-1', 'SOQ003838-1', 'SOQ003870-1', 'SOQ003890-1'],
        'Order_Date': ['3/8/2023'] * 5,
        'Product_Category': ['SPRAYS'] * 5,
        'Complaint': [
            'GAS P-CLIP and air ducting still not tightened at factory',
            'Fuel door not stay open',
            'Fuel door crushed',
            'UNLOCKS were not installed',
            'WITH HAMMER AND SOCKET'
        ],
        'Cause': [
            'ALL 2 CLIPS, NUTS, AND BOLTS',
            'HYDRAULIC OIL RUNNING OUT',
            'COMPRESSOR PRESSURE LINE',
            'UNLOCKS WERE NOT INSTALLED',
            'COUPLER was leaking'
        ],
        'Correction': [
            'Not Mentioned',
            'Well Lubricated',
            'BATTLE PRODUCT ASSOCIATED',
            'PAN AND TESTED',
            'MISSING BRACKETS AND BOLTS'
        ]
    }

    df = pd.DataFrame(sample_data)

    tagger = DataTagger()
    tagged_df = tagger.tag_dataframe(df)

    print(tagged_df.to_string(index=False))
    tagged_df.to_csv("tagged_dataset_task1.csv", index=False)
    print("Saved tagged dataset to tagged_dataset_task1.csv")


if __name__ == "__main__":
    main()
