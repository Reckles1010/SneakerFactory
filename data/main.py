"""Ejecución autónoma básica del pipeline real desde consola."""
import argparse
from config import INPUT_DIR
from pipeline import load_and_validate
from analiticas import build_analytics

def main():
    parser = argparse.ArgumentParser(description="Sneaker Factory · análisis reproducible")
    parser.add_argument("--modo", choices=["real"], default="real")
    parser.add_argument("--entrada", default=str(INPUT_DIR))
    args = parser.parse_args()
    
    snapshot = load_and_validate(args.entrada)
    result = build_analytics(snapshot)
    
    print("ORIGEN: ACC · REAL")
    print("KPIs:", result["kpis"])
    print("DataFrames:", ", ".join(result.keys()))

if __name__ == "__main__":
    main()