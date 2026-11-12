import streamlit as st

df_anomalias = detectar_anomalias(df_pedidos)


st.subheader("Detección de anomalías")
st.dataframe(df_anomalias)