import pandas as pd
import glob
import os
import re

input_folder = '/Users/tashigyeltshen/Downloads/DHI_IA/master_data/2024'
output_folder = '/Users/tashigyeltshen/Downloads/DHI_IA/parquet_files/drukair/master_data/2024'

os.makedirs(output_folder, exist_ok=True)
files = sorted(glob.glob(f'{input_folder}/*.xlsx') + glob.glob(f'{input_folder}/*.xls'))
print(f'Found {len(files)} Excel files')


def clean_name(name):
    name = str(name).strip()
    name = re.sub(r'\s+', '_', name)
    name = name.replace('/', '_')
    name = name.upper()  # Normalize case to prevent D_Class vs D_CLASS duplicates
    return name


def make_unique_columns(cols):
    seen = {}
    new_cols = []
    for col in cols:
        col = clean_name(col)

        # Drop unnamed/junk columns by returning None
        if re.match(r'^UNNAMED', col) or re.match(r'^_\d+$', col):
            new_cols.append(None)
            continue

        seen[col] = seen.get(col, 0) + 1
        if seen[col] == 1:
            new_cols.append(col)
        else:
            new_cols.append(f'{col}_{seen[col]}')
    return new_cols


print('\nConverting each Excel → Parquet...')
for f in files:
    filename = os.path.basename(f)
    base_name = os.path.splitext(filename)[0]

    try:
        df = pd.read_excel(f, engine='openpyxl')
    except Exception:
        try:
            df = pd.read_excel(f, engine='xlrd')
        except Exception as e:
            print(f'  ✗ Failed to read {filename}: {e}')
            continue

    print(f'Reading {filename}...')
    df = df.dropna(how='all')

    # Clean and deduplicate column names
    new_cols = make_unique_columns(df.columns)

    # Drop columns marked as None (unnamed/junk)
    keep = [i for i, c in enumerate(new_cols) if c is not None]
    df = df.iloc[:, keep]
    df.columns = [new_cols[i] for i in keep]

    print(f'  → {len(df)} rows, {len(df.columns)} columns')

    # Strip whitespace from string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()

    output_path = f'{output_folder}/passenger_traffic_{base_name}.parquet'
    df.to_parquet(output_path, engine='pyarrow', index=False)
    print(f'  → saved {len(df)} rows to {os.path.basename(output_path)}')

print(f'\n✅ Done! Parquet files saved in: {output_folder}')