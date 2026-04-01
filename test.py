import pickle
from pathlib import Path

with open(r'C:\Users\pc\OneDrive\Área de Trabalho\projeto-ids-ips\models\random_forest_server_model.pkl', 'rb') as f:
    dados = pickle.load(f)

print("Acurácia guardada:", round(dados.get('acuracia') * 100, 2), "%")
print("Tipo do modelo:", type(dados['modelo']).__name__)