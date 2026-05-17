import tensorflow as tf
import pickle
import pandas as pd

# Carregar tudo
model = tf.keras.models.load_model('ids_deep_learning_model.keras')
with open('ids_scaler.pkl', 'rb') as f: scaler = pickle.load(f)
with open('ids_label_encoder.pkl', 'rb') as f: le = pickle.load(f)

# Para prever um novo dado:
# 1. df_novo = pd.read_csv(...)
# 2. df_scaled = scaler.transform(df_novo)
# 3. pred = model.predict(df_scaled)
# 4. nome_ataque = le.inverse_transform([np.argmax(pred)])