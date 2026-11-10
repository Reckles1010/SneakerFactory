import pandas as pd
from data.config import INPUT_DIR, FILES, ALIASES, CSV_SEPARATOR, CSV_ENCODING

for clave, nombre in FILES.items():
    ruta = INPUT_DIR / nombre
    if not ruta.exists():
        print(f"[NO EXISTE] {nombre}")
        continue
    df = pd.read_csv(ruta, sep=CSV_SEPARATOR, encoding=CSV_ENCODING, nrows=0)
    cols = {c.strip().lower() for c in df.columns}
    print(f"\n{nombre} -> columnas: {list(df.columns)}")
    for canonica, alias in ALIASES.get(clave, {}).items():
        if not cols & {a.lower() for a in alias}:
            print(f"   FALTA: {canonica} (alias: {alias})")