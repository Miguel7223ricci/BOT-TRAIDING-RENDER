import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# --- Configuración ---
archivo_modelo_base = "modelo_trained_rf_pro.pkl"
archivo_senales_reales = "Senales_emitidas_registradas.csv"  # ⚠️ Nuevo archivo corregido
modelo_hibrido_salida = "modelo_hibrido.pkl"

# --- Cargar el modelo base (preentrenado con datos simulados) ---
try:
    modelo = joblib.load(archivo_modelo_base)
    print(f"✅ Modelo base cargado desde {archivo_modelo_base}")
except Exception as e:
    print(f"❌ Error al cargar modelo base: {e}")
    exit()

# --- Cargar señales reales etiquetadas ---
try:
    df = pd.read_csv(archivo_senales_reales)
    df.columns = df.columns.str.lower()
except FileNotFoundError:
    print("❌ Archivo de señales no encontrado.")
    exit()

# --- Validar que existan los campos necesarios ---
campos_necesarios = ["ema_35", "ema_50", "rsi", "adx", "resultado"]
for campo in campos_necesarios:
    if campo not in df.columns:
        print(f"❌ Falta la columna requerida: {campo}")
        exit()

# --- Filtrar señales válidas ---
df = df[df["resultado"].isin(["GANANCIA", "PERDIDA"])]
if len(df) < 10:
    print("❌ No hay suficientes señales etiquetadas para refinar el modelo.")
    exit()

# --- Entrenamiento con señales reales ---
X_real = df[["ema_35", "ema_50", "rsi", "adx"]]
y_real = df["resultado"]

modelo_refinado = RandomForestClassifier(n_estimators=100, random_state=42)
modelo_refinado.fit(X_real, y_real)

# --- Evaluación ---
y_pred = modelo_refinado.predict(X_real)
print("\n📊 Evaluación sobre datos reales:")
print(classification_report(y_real, y_pred))

# --- Guardar nuevo modelo hibrido ---
joblib.dump(modelo_refinado, modelo_hibrido_salida)
print(f"\n✅ Modelo híbrido guardado como: {modelo_hibrido_salida}")
