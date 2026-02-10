#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Analysis Script for Mentor Evaluation System
Analyzes and merges two xls files into a single CSV
"""

import sys
import warnings
warnings.filterwarnings('ignore')

try:
    import pandas as pd
    import xlrd
    print("✓ Libraries loaded successfully")
except ImportError as e:
    print(f"✗ Error importing libraries: {e}")
    print("Please run: pip install pandas xlrd openpyxl")
    sys.exit(1)


def analyze_xls_structure(file_path):
    """Analyze the structure of an xls file"""
    print(f"\n{'='*60}")
    print(f"Analyzing: {file_path}")
    print(f"{'='*60}")

    try:
        # Read the xls file
        df = pd.read_excel(file_path, engine='xlrd')

        print(f"\n📊 Data Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"\n📋 Column Names:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")

        print(f"\n🔍 Data Types:")
        print(df.dtypes)

        print(f"\n📝 First 3 rows:")
        print(df.head(3).to_string())

        print(f"\n📈 Basic Statistics:")
        print(df.describe(include='all').to_string())

        return df

    except Exception as e:
        print(f"✗ Error reading file: {e}")
        return None


def main():
    # Analyze both files
    mentor_df = analyze_xls_structure("导师信息.xls")
    evaluation_df = analyze_xls_structure("评价信息.xls")

    if mentor_df is None or evaluation_df is None:
        print("\n✗ Failed to read one or both files")
        return

    print(f"\n{'='*60}")
    print("Analysis Complete!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
