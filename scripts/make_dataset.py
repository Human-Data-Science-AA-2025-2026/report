import json
import pandas as pd
from pathlib import Path
import re
import os

def parse_eurostat(path):
    """
    Extract total Italian immigrants (all ages, both sexes) from a JSON-stat file.
    Selects: agedef=COMPLET, age=TOTAL, sex=T, citizen=IT.
    """
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    dims = data['id']
    sizes = data['size']
    cats = data['dimension']
    
    # Infer geo and time codes from metadata (usually single-valued in these files)
    geo_code = list(cats['geo']['category']['index'].keys())[0]
    time_code = list(cats['time']['category']['index'].keys())[0]
    
    target = {
        'freq': 'A',
        'citizen': 'IT',
        'agedef': 'COMPLET',
        'age': 'TOTAL',
        'unit': 'NR',
        'sex': 'T',
        'geo': geo_code,
        'time': time_code
    }
    
    # Calculate flat index (row-major)
    current_idx = 0
    for i, dim in enumerate(dims):
        code = target[dim]
        # In case the code is missing in this file
        if code not in cats[dim]['category']['index']:
            return None
        val_idx = cats[dim]['category']['index'][code]
        current_idx = current_idx * sizes[i] + val_idx
        
    val = data['value'].get(str(current_idx))
    return int(val) if val is not None else None

def parse_istat(path):
    """
    Parse an ISTAT CSV (tab-separated).
    Filters: CITIZENSHIP=IT, SEX=9 (Total), AGE=TOTAL.
    """
    df = pd.read_csv(path, sep='\t', encoding='utf-8-sig')
    
    # Clean string columns
    for col in ['CITIZENSHIP', 'SEX', 'AGE', 'COUNTRY_NEXT_RESID']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    mask = (df['CITIZENSHIP'] == 'IT') & \
           (df['SEX'] == '9') & \
           (df['AGE'] == 'TOTAL')
    
    filtered = df[mask].copy()
    
    # The value is in the column immediately after TIME_PERIOD (usually 'Osservazione' or unnamed)
    try:
        idx_year = list(df.columns).index('TIME_PERIOD')
        val_col = df.columns[idx_year + 1]
        filtered['VALUE'] = pd.to_numeric(filtered[val_col], errors='coerce')
    except (ValueError, IndexError):
        # Fallback to absolute index if column names are unexpected
        filtered['VALUE'] = pd.to_numeric(filtered.iloc[:, 15], errors='coerce')
        
    return filtered[['COUNTRY_NEXT_RESID', 'VALUE']]

def main():
    # Paths relative to this script
    base_dir = Path(__file__).parent.parent
    raw_dir = base_dir / 'data' / 'raw'
    output_path = base_dir / 'data' / 'merged_migration_data.csv'
    
    euro_regex = re.compile(r'^([A-Z]{2})-EUROSTAT-IMMIGRANTS-(\d{4})\.json$')
    istat_regex = re.compile(r'^IT-ISTAT-(\d{4})\.csv$')
    
    euro_data = []
    istat_data = []
    
    print(f"Scanning raw data in {raw_dir}...")
    
    files = sorted(list(raw_dir.glob('*')))
    for f in files:
        m_euro = euro_regex.match(f.name)
        if m_euro:
            country, year = m_euro.groups()
            val = parse_eurostat(f)
            if val is not None:
                euro_data.append({
                    'DESTINATION_STATE': country, 
                    'YEAR': int(year), 
                    'DEST_REGISTERED': val
                })
            continue
            
        m_istat = istat_regex.match(f.name)
        if m_istat:
            year = int(m_istat.group(1))
            df_istat = parse_istat(f)
            df_istat['YEAR'] = year
            istat_data.append(df_istat)
            
    if not euro_data or not istat_data:
        print("Error: Could not find any raw files to parse.")
        return

    df_euro = pd.DataFrame(euro_data)
    df_istat = pd.concat(istat_data).rename(columns={
        'COUNTRY_NEXT_RESID': 'DESTINATION_STATE', 
        'VALUE': 'ISTAT_DELETED'
    })
    
    # Merge datasets
    merged = pd.merge(df_euro, df_istat, on=['DESTINATION_STATE', 'YEAR'], how='inner')
    
    # Filter for the 8 destination countries mentioned in the methodology
    target_countries = ['AT', 'DE', 'DK', 'ES', 'FI', 'FR', 'NO', 'SE']
    merged = merged[merged['DESTINATION_STATE'].isin(target_countries)]
    
    # Final cleanup
    merged = merged[['DESTINATION_STATE', 'YEAR', 'ISTAT_DELETED', 'DEST_REGISTERED']]
    merged = merged.sort_values(['DESTINATION_STATE', 'YEAR']).reset_index(drop=True)
    
    # Remove duplicates if any (e.g. from overlapping files)
    merged = merged.drop_duplicates()
    
    merged.to_csv(output_path, index=False)
    print(f"Successfully merged {len(merged)} records into {output_path}")

if __name__ == '__main__':
    main()
