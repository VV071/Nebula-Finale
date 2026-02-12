"""
Batch Stock Engine
Processes multiple stocks in sequence with rate-limiting to avoid API blocks
"""

import time
import json
import sys
import argparse
from typing import List, Dict, Any
from engine import StockEngine
from nsepython import nse_eq_symbols
import pandas as pd

class BatchProcessor:
    def __init__(self):
        self.engine = StockEngine()

    def get_all_nse_symbols(self) -> List[str]:
        """Fetch all equity symbols from NSE"""
        try:
            return nse_eq_symbols()
        except Exception as e:
            print(f"Error fetching symbols from NSE: {e}")
            return []

    def run_batch(self, symbols: List[str], exchange: str = "NSE", delay: float = 1.0, output_file: str = "batch_results.json"):
        """Run analysis on a list of symbols"""
        results = []
        total = len(symbols)
        print(f"Starting batch analysis for {total} symbols on {exchange}...")
        
        for i, symbol in enumerate(symbols):
            try:
                print(f"[{i+1}/{total}] Analyzing {symbol}...")
                result = self.engine.analyze_stock(symbol, exchange)
                results.append(result)
            except Exception as e:
                print(f"  FAILED: {symbol} - {str(e)}")
                results.append({
                    "symbol": symbol,
                    "exchange": exchange,
                    "error": str(e),
                    "status": "failed"
                })
            
            # Rate limiting
            if i < total - 1:
                time.sleep(delay)
                
        # Save results
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\nBatch analysis complete. Results saved to {output_file}")
        return results

def main():
    parser = argparse.ArgumentParser(description="Batch Stock Analysis Engine")
    parser.add_argument("--symbols", type=str, help="Comma-separated list of symbols (e.g. RELIANCE,TCS,INFY)")
    parser.add_argument("--exchange", type=str, default="NSE", help="Exchange (NSE, BSE, NASDAQ, etc.)")
    parser.add_argument("--limit", type=int, help="Limit the number of stocks to process (useful for testing)")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests in seconds (default: 1.0)")
    parser.add_argument("--output", type=str, default="batch_results.json", help="Output JSON file name")
    parser.add_argument("--all-nse", action="store_true", help="Process all stocks in NSE")

    args = parser.parse_args()
    processor = BatchProcessor()

    symbols_to_process = []

    if args.all_nse:
        symbols_to_process = processor.get_all_nse_symbols()
    elif args.symbols:
        symbols_to_process = [s.strip() for s in args.symbols.split(",")]
    else:
        print("Error: Specify --symbols or --all-nse")
        sys.exit(1)

    if args.limit:
        symbols_to_process = symbols_to_process[:args.limit]

    if not symbols_to_process:
        print("No symbols found to process.")
        sys.exit(1)

    processor.run_batch(
        symbols=symbols_to_process, 
        exchange=args.exchange, 
        delay=args.delay, 
        output_file=args.output
    )

if __name__ == "__main__":
    main()
