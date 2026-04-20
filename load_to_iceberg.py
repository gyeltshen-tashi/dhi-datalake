# load_to_iceberg.py
import pandas as pd
import glob
import os
import re
import sys
from dotenv import load_dotenv
from trino.dbapi import connect
from configs import CONFIGS

# Load .env file if it exists
load_dotenv()

TRINO_HOST = os.getenv("TRINO_HOST", "100.85.189.71")
TRINO_PORT = int(os.getenv("TRINO_PORT", "8080"))


def to_trino_type(dtype):
    if 'datetime' in str(dtype):
        return 'TIMESTAMP(6)'
    elif 'int' in str(dtype):
        return 'BIGINT'
    elif 'float' in str(dtype):
        return 'DOUBLE'
    else:
        return 'VARCHAR'


def clean_col_name(col):
    col = re.sub(r'[^a-zA-Z0-9_]', '_', col)
    if col[0].isdigit():
        col = '_' + col
    return col


def format_value(val, dtype):
    if pd.isna(val):
        return 'NULL'
    elif 'datetime' in str(dtype):
        return f"TIMESTAMP '{val}'"
    elif 'int' in str(dtype) or 'float' in str(dtype):
        return str(val)
    else:
        val = str(val).replace("'", "''")
        return f"'{val}'"


def load_dataset(cfg):
    LOCAL_BASE = cfg['local_base']
    CATALOG = cfg['catalog']
    SCHEMA = cfg['schema']
    TABLE = cfg['table']
    location = cfg.get('location', f's3://data-lake-bucket/{SCHEMA}/{TABLE}/')

    print(f'\n{"="*60}')
    print(f'Loading: {CATALOG}.{SCHEMA}.{TABLE}')
    print(f'Source: {LOCAL_BASE}')
    print(f'{"="*60}\n')

    # Find all parquet files, skip duplicates
    files = sorted(glob.glob(f'{LOCAL_BASE}/**/*.parquet', recursive=True))
    files = [f for f in files if '(1)' not in f and '(2)' not in f]
    print(f'Found {len(files)} parquet files\n')

    if len(files) == 0:
        print(f'No files found in {LOCAL_BASE} — skipping.')
        return

    # Read all files
    print('Reading all parquet files...')
    dfs = []
    for f in files:
        df = pd.read_parquet(f)
        filename = os.path.basename(f)
        year_match = re.search(r'(\d{4})', filename)
        filename_year = int(year_match.group(1)) if year_match else 0

        # Only set year from filename if the data doesn't already have it
        if 'year' not in df.columns:
            df['year'] = filename_year
        elif df['year'].isnull().all() or (df['year'] == 0).all():
            # Year column exists but is empty or all zeros — use filename year
            df['year'] = filename_year
        # Otherwise keep the year that's already in the data

        df['source_file'] = filename
        print(f'  {filename} → {len(df)} rows')
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    print(f'\nTotal rows: {len(combined)}')
    print(f'Total columns: {len(combined.columns)}')

    # Drop junk columns
    junk_cols = [c for c in combined.columns if
                 c.startswith('Unnamed') or
                 c.startswith('KB___') or
                 len(c) > 50]
    if junk_cols:
        print(f'Dropping {len(junk_cols)} junk columns')
        combined = combined.drop(columns=junk_cols)
    print(f'Remaining columns: {len(combined.columns)}')

    # Clean column names
    combined.columns = [clean_col_name(c) for c in combined.columns]

    # Check for duplicate column names
    if len(combined.columns) != len(set(combined.columns)):
        print('WARNING: Duplicate column names found after cleaning:')
        seen = set()
        dupes = []
        for c in combined.columns:
            if c in seen:
                dupes.append(c)
            seen.add(c)
        print(f'  {dupes}')
        # Make duplicates unique by appending index
        new_cols = []
        seen = {}
        for c in combined.columns:
            if c in seen:
                seen[c] += 1
                new_cols.append(f'{c}_{seen[c]}')
            else:
                seen[c] = 0
                new_cols.append(c)
        combined.columns = new_cols

    # Build column definitions
    col_defs = ',\n    '.join([
        f'"{col}" {to_trino_type(dtype)}'
        for col, dtype in combined.dtypes.items()
    ])

    # Connect to Trino
    print('\nConnecting to Trino...')
    conn = connect(
        host=TRINO_HOST,
        port=TRINO_PORT,
        user='admin',
        catalog=CATALOG,
        schema=SCHEMA,
        request_timeout=300
    )
    cursor = conn.cursor()

    try:
        # Create schema if not exists
        cursor.execute(f'CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}')

        # Check if table exists — resume or create
        cursor.execute(f"SHOW TABLES IN {CATALOG}.{SCHEMA} LIKE '{TABLE}'")
        table_exists = cursor.fetchone() is not None

        if table_exists:
            print('Table already exists, checking compatibility...')
            cursor.execute(f'SELECT COUNT(*) FROM {CATALOG}.{SCHEMA}.{TABLE}')
            start_row = cursor.fetchone()[0]
            # Check column count matches
            cursor.execute(f'DESCRIBE {CATALOG}.{SCHEMA}.{TABLE}')
            existing_cols = len(cursor.fetchall())
            if existing_cols != len(combined.columns):
                print(f'WARNING: Column mismatch! Table has {existing_cols} cols, data has {len(combined.columns)} cols')
                print('Dropping and recreating table...')
                cursor.execute(f'DROP TABLE {CATALOG}.{SCHEMA}.{TABLE}')
                table_exists = False
                start_row = 0
            else:
                print(f'Resuming from row {start_row}...')

        if not table_exists:
            print('Creating table in Iceberg...')
            cursor.execute(f'''
                CREATE TABLE {CATALOG}.{SCHEMA}.{TABLE} (
                    {col_defs}
                )
                WITH (
                    format = 'PARQUET',
                    location = '{location}'
                )
            ''')
            print('Table created!')
            start_row = 0

        # Insert in batches with retry
        batch_size = 5000
        total = len(combined)
        print(f'\nInserting {total - start_row} remaining rows in batches of {batch_size}...')

        for i in range(start_row, total, batch_size):
            batch = combined.iloc[i:i+batch_size]
            rows = []
            for _, row in batch.iterrows():
                values = [format_value(row[col], combined.dtypes[col]) for col in combined.columns]
                rows.append(f"({', '.join(values)})")
            values_str = ', '.join(rows)

            for attempt in range(3):
                try:
                    cursor.execute(f'INSERT INTO {CATALOG}.{SCHEMA}.{TABLE} VALUES {values_str}')
                    break
                except Exception as e:
                    if attempt < 2:
                        print(f'  Retry {attempt+1} on batch {i}...')
                    else:
                        print(f'  FAILED on batch {i} after 3 attempts: {e}')
                        print(f'  Skipping batch and continuing...')
                        break

            print(f'  Progress: {min(i+batch_size, total)}/{total} rows inserted...')
    finally:
        conn.close()

    print(f'\n✓ Done! {TABLE} loaded into {CATALOG}.{SCHEMA}')


# ============================================================
# MAIN — run one dataset or all
# ============================================================
if len(sys.argv) < 2:
    datasets_to_run = list(CONFIGS.keys())
    print(f'No dataset specified — running all: {datasets_to_run}')
else:
    # Support multiple datasets: python3 script.py dataset1 dataset2
    datasets_to_run = []
    for arg in sys.argv[1:]:
        if arg not in CONFIGS:
            print(f'Unknown dataset: {arg} — skipping')
        else:
            datasets_to_run.append(arg)
    if not datasets_to_run:
        print(f'No valid datasets found. Available: {list(CONFIGS.keys())}')
        sys.exit(1)

for dataset in datasets_to_run:
    try:
        load_dataset(CONFIGS[dataset])
    except Exception as e:
        print(f'\n✗ Failed to load {dataset}: {e}')
        print('Continuing with next dataset...')

print('\n✓ All done!')