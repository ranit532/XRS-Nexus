# ==============================================================================
# Fabric Notebook Utility: Data Quality
# Description: Reusable functions for DQ checks in Spark pipelines.
# ==============================================================================

from pyspark.sql import DataFrame
from pyspark.sql.functions import col

class DataQualityValidator:
    def __init__(self, df: DataFrame):
        self.df = df
        self.errors = []

    def check_nulls(self, columns: list):
        """Checks for nulls in specified primary/mandatory columns."""
        for c in columns:
            null_count = self.df.filter(col(c).isNull()).count()
            if null_count > 0:
                self.errors.append(f"Column '{c}' has {null_count} null checks failed.")
        return self

    def check_unique(self, column: str):
        """Checks uniqueness constraint on a column."""
        duplicate_count = self.df.groupBy(column).count().filter("count > 1").count()
        if duplicate_count > 0:
            self.errors.append(f"Column '{column}' has {duplicate_count} duplicate values.")
        return self

    def check_value_range(self, column: str, min_val, max_val):
        """Checks if values fall within a range."""
        out_of_range = self.df.filter((col(column) < min_val) | (col(column) > max_val)).count()
        if out_of_range > 0:
            self.errors.append(f"Column '{column}' has {out_of_range} values out of range [{min_val}, {max_val}].")
        return self

    def validate(self, raise_error=True):
        """Finalizes validation and optionally raises exception."""
        if self.errors:
            error_msg = "\n".join(self.errors)
            print(f"Data Quality Validation FAILED:\n{error_msg}")
            if raise_error:
                raise ValueError(f"DQ Checks Failed: {error_msg}")
            return False
        
        print("Data Quality Validation PASSED.")
        return True

# Example Usage in Notebook:
# from utils.data_quality import DataQualityValidator
# dq = DataQualityValidator(df)
# dq.check_nulls(["id", "date"]).check_unique("id").validate()
