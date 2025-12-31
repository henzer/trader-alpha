import csv
from pathlib import Path
from typing import List, Dict

LISTS_DIR = Path(__file__).parent.parent / "lists"

def get_symbols_from_csv(csv_filename: str) -> List[str]:
    csv_path = LISTS_DIR / csv_filename
    
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    symbols = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol = row.get('symbol', '').strip().upper()
            if symbol:
                symbols.append(symbol)
    
    return symbols

def get_all_lists() -> Dict[str, List[str]]:
    if not LISTS_DIR.exists():
        raise FileNotFoundError(f"Lists directory not found: {LISTS_DIR}")
    
    all_lists = {}
    
    for csv_file in LISTS_DIR.glob("*.csv"):
        list_name = csv_file.stem
        try:
            symbols = get_symbols_from_csv(csv_file.name)
            all_lists[list_name] = symbols
        except Exception as e:
            print(f"Warning: Failed to load {csv_file.name}: {e}")
    
    return all_lists

def get_all_symbols() -> List[str]:
    all_lists = get_all_lists()
    
    all_symbols = set()
    for symbols in all_lists.values():
        all_symbols.update(symbols)
    
    return sorted(list(all_symbols))

def get_symbol_to_lists_mapping() -> Dict[str, List[str]]:
    all_lists = get_all_lists()
    
    symbol_to_lists = {}
    for list_name, symbols in all_lists.items():
        for symbol in symbols:
            if symbol not in symbol_to_lists:
                symbol_to_lists[symbol] = []
            symbol_to_lists[symbol].append(list_name)
    
    return symbol_to_lists