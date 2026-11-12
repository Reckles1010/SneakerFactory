"""Segmentación de clientes con KMeans (variables escaladas, k = 2..5, silhouette)."""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from data.config import RANDOM_SEED

MIN_CLIENTES = 20


def kmeans_clientes(rfm, ks=(2, 3, 4, 5), seed=RANDOM_SEED):
    """Devuelve dict con estado, comparación de k, asignación, perfil y cruce con RFM."""
    d = rfm[rfm["segmento_rfm"] != "Sin compras válidas"].copy()
    if len(d) < MIN_CLIENTES:
        return {"estado": "NO CALCULABLE", "motivo": f"Solo {len(d)} clientes con compras válidas (mínimo {MIN_CLIENTES}); "
                "no es defendible agrupar. Demostrar el modelo con el histórico sintético."}
    X = d[["recency_dias", "frequency", "monetary"]].astype(float)
    Xs = StandardScaler().fit_transform(X)
    filas, modelos = [], {}
    for k in [k for k in ks if k < len(d)]:
        km = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(Xs)
        filas.append({"k": k, "silhouette": float(silhouette_score(Xs, km.labels_)), "inercia": float(km.inertia_)})
        modelos[k] = km
    comp = pd.DataFrame(filas)
    k_best = int(comp.loc[comp["silhouette"].idxmax(), "k"])
    d["cluster"] = modelos[k_best].labels_
    perfil = d.groupby("cluster").agg(clientes=("id_cliente", "size"), recency_media=("recency_dias", "mean"),
                                        frecuencia_media=("frequency", "mean"), monetary_medio=("monetary", "mean"),
                                        monetary_mediana=("monetary", "median")).reset_index()
    perfil["proporcion_pct"] = perfil["clientes"] / perfil["clientes"].sum() * 100
    gm = X.mean()
    def nombre(r):
        if r["monetary_medio"] > gm["monetary"] and r["frecuencia_media"] > gm["frequency"]:
            return "Alto valor y frecuente"
        if r["recency_media"] > gm["recency_dias"] and r["frecuencia_media"] <= gm["frequency"]:
            return "Inactivos o de baja frecuencia"
        return "Intermedios"
    perfil["nombre"] = perfil.apply(nombre, axis=1)
    d = d.merge(perfil[["cluster", "nombre"]], on="cluster")
    cruce = pd.crosstab(d["nombre"], d["segmento_rfm"])
    return {"estado": "CALCULADO", "k_elegido": k_best, "comparacion_k": comp, "asignacion": d[["id_cliente", "cluster", "nombre"]],
            "perfil": perfil, "cruce_rfm": cruce,
            "nota": "Un clúster es un grupo matemático de recency/frecuencia/gasto escalados; no equivale automáticamente "
                    "a una categoría comercial. Se nombra por el perfil medio y se compara con las reglas RFM."}
