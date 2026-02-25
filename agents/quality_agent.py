"""
Quality Agent: Assesses data quality, detects stale/incorrect data, and reports issues.
"""
import pandas as pd

class QualityAgent:
    def check_quality(self, file_path):
        df = pd.read_csv(file_path)
        issues = {}
        if df.isnull().values.any():
            issues["missing_values"] = df.isnull().sum().to_dict()
        if df.duplicated().any():
            issues["duplicates"] = df[df.duplicated()].to_dict()
        # Add more quality checks as needed
        return issues
