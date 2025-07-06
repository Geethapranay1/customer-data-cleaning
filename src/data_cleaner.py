import pandas as pd
import numpy as np
import re
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple

class CustomerDataCleaner:
    
    def __init__(self):
        self.report = {
            'orig_shape': None,
            'final_shape': None,
            'found': {},
            'fixed': {},
            'quality': {}
        }
    
    def assess_data_quality(self, df: pd.DataFrame) -> Dict:
        assess = {
            'missing': df.isnull().sum().to_dict(),
            'dupes': df.duplicated().sum(),
            'types': df.dtypes.to_dict(),
            'unique': df.nunique().to_dict(),
            'memory': df.memory_usage(deep=True).sum() / 1024**2
        }
        
        num_cols = df.select_dtypes(include=[np.number]).columns
        assess['outliers'] = {}
        
        for col in num_cols:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outliers = df[(df[col] < lower) | (df[col] > upper)].shape[0]
            assess['outliers'][col] = outliers
        
        return assess
    
    def clean_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        cleaned = df.copy()
        
        high_missing = cleaned.columns[cleaned.isnull().mean() > 0.5]
        cleaned = cleaned.drop(columns=high_missing)
        
        for col in cleaned.columns:
            if cleaned[col].dtype == 'object':
                mode = cleaned[col].mode()
                if not mode.empty:
                    cleaned[col].fillna(mode[0], inplace=True)
            elif cleaned[col].dtype in ['int64', 'float64']:
                median = cleaned[col].median()
                cleaned[col].fillna(median, inplace=True)
        
        self.report['fixed']['missing'] = {
            'dropped_cols': list(high_missing),
            'imputed': df.isnull().sum().sum() - cleaned.isnull().sum().sum()
        }
        
        return cleaned
    
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        initial = len(df)
        cleaned = df.drop_duplicates()
        removed = initial - len(cleaned)
        
        self.report['fixed']['dupes'] = {
            'removed': removed,
            'rate': f"{(removed/initial)*100:.2f}%"
        }
        
        return cleaned
    
    def standardize_formats(self, df: pd.DataFrame) -> pd.DataFrame:
        cleaned = df.copy()
        
        if 'Email' in cleaned.columns:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            cleaned['Email_Valid'] = cleaned['Email'].str.match(email_pattern)
            cleaned.loc[~cleaned['Email_Valid'], 'Email'] = np.nan
        
        if 'Phone' in cleaned.columns:
            cleaned['Phone'] = cleaned['Phone'].astype(str).str.replace(r'[^\d]', '', regex=True)
            cleaned['Phone'] = cleaned['Phone'].str.replace(r'^(\d{10})$', r'(\1) \2-\3', regex=True)
        
        date_cols = ['Registration_Date']
        for col in date_cols:
            if col in cleaned.columns:
                cleaned[col] = pd.to_datetime(cleaned[col], errors='coerce')
        
        if 'Status' in cleaned.columns:
            cleaned['Status'] = cleaned['Status'].str.title()
        
        return cleaned
    
    def handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        cleaned = df.copy()
        num_cols = ['Age', 'Income']
        
        for col in num_cols:
            if col in cleaned.columns:
                q1 = cleaned[col].quantile(0.25)
                q3 = cleaned[col].quantile(0.75)
                iqr = q3 - q1
                
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                
                cleaned[col] = np.clip(cleaned[col], lower, upper)
        
        return cleaned
    
    def clean_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        print("Starting data cleaning process...")
        
        self.report['orig_shape'] = df.shape
        
        print("Assessing data quality...")
        self.report['found'] = self.assess_data_quality(df)
        
        print("Handling missing values...")
        cleaned = self.clean_missing_values(df)
        
        print("Removing duplicates...")
        cleaned = self.remove_duplicates(cleaned)
        
        print("Standardizing formats...")
        cleaned = self.standardize_formats(cleaned)
        
        print("Handling outliers...")
        cleaned = self.handle_outliers(cleaned)
        
        self.report['final_shape'] = cleaned.shape
        
        orig_quality = self._calc_quality_score(df)
        final_quality = self._calc_quality_score(cleaned)
        
        self.report['quality'] = {
            'orig': f"{orig_quality:.2f}%",
            'final': f"{final_quality:.2f}%",
            'improve': f"{final_quality - orig_quality:.2f}%"
        }
        
        print(f"Data cleaning completed!")
        print(f"Quality Score: {orig_quality:.1f}% -> {final_quality:.1f}% (+{final_quality-orig_quality:.1f}%)")
        
        return cleaned
    
    def _calc_quality_score(self, df: pd.DataFrame) -> float:
        total = df.shape[0] * df.shape[1]
        
        missing_penalty = (df.isnull().sum().sum() / total) * 100
        dupe_penalty = (df.duplicated().sum() / df.shape[0]) * 100
        
        quality = 100 - missing_penalty - dupe_penalty
        
        return max(0, quality)
    
    def generate_report(self) -> str:
        report = f"""
        DATA CLEANING REPORT
        ====================
        
        Dataset Overview:
        - Original Shape: {self.report['orig_shape']}
        - Final Shape: {self.report['final_shape']}
        - Rows Processed: {self.report['orig_shape'][0]:,}
        - Columns Processed: {self.report['orig_shape'][1]}
        
        Issues Identified:
        - Missing Values: {sum(self.report['found']['missing'].values()):,}
        - Duplicate Rows: {self.report['found']['dupes']:,}
        - Data Quality Issues: Multiple format inconsistencies
        
        Cleaning Actions:
        - Missing Values: {self.report['fixed']['missing']['imputed']:,} imputed
        - Duplicates: {self.report['fixed']['dupes']['removed']:,} removed
        - Formats: Email, phone, date standardization applied
        - Outliers: Handled using IQR method
        
        Quality Improvement:
        - Original Quality Score: {self.report['quality']['orig']}
        - Final Quality Score: {self.report['quality']['final']}
        - Improvement: {self.report['quality']['improve']}
        
        Data is now ready for analysis and modeling!
        """
        return report

if __name__ == "__main__":
    cleaner = CustomerDataCleaner()
    
    df = pd.read_csv('data/raw_customer_data.csv')
    cleaned_df = cleaner.clean_dataset(df)
    
    cleaned_df.to_csv('data/cleaned_customer_data.csv', index=False)
    
    print(cleaner.generate_report())