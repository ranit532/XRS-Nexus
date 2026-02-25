"""
Data Structure Agent: Analyzes and describes the structure of datasets.
"""
import pandas as pd

class StructureAgent:
    def analyze_structure(self, file_path):
        df = pd.read_csv(file_path)
        return {
            "columns": list(df.columns),
            "dtypes": df.dtypes.apply(str).to_dict(),
            "num_rows": len(df)
        }
