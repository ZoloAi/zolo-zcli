# This file contains the fixes to apply to csv_adapter.py

# 1. Remove warning suppression (lines 10, 17-18):
# DELETE:
import warnings
# DELETE:
    # Suppress FutureWarning about DataFrame concatenation with empty entries
    warnings.filterwarnings('ignore', category=FutureWarning, module='pandas')

# 2. Add helper method after line 169 (before CRUD Operations section):
    def _append_row_to_df(self, df, new_row):
        """
        Safely append a row to DataFrame avoiding FutureWarning.
        
        Handles empty DataFrames properly to avoid pandas deprecation warning
        about concatenating with empty or all-NA entries.
        
        Args:
            df (DataFrame): Existing DataFrame
            new_row (dict): Dict of new row data
            
        Returns:
            DataFrame: DataFrame with new row appended
        """
        # Ensure all columns present in new row
        for col in df.columns:
            if col not in new_row:
                new_row[col] = None
        
        # Create new DataFrame with same columns
        new_df = pd.DataFrame([new_row], columns=df.columns)
        
        # If original is empty, just return the new one (avoids FutureWarning)
        if len(df) == 0:
            return new_df
        
        # Otherwise concatenate safely
        return pd.concat([df, new_df], ignore_index=True, sort=False)

# 3. Replace line 196:
# OLD:
        df = pd.concat([df, new_df], ignore_index=True, sort=False)
# NEW:
        df = self._append_row_to_df(df, new_row)

# 4. Replace line 314:
# OLD:
                df = pd.concat([df, new_df], ignore_index=True, sort=False)
# NEW:
                df = self._append_row_to_df(df, new_row)

# 5. Replace line 324:
# OLD:
            df = pd.concat([df, new_df], ignore_index=True, sort=False)
# NEW:
            df = self._append_row_to_df(df, new_row)
