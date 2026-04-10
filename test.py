import pickle
from pathlib import Path

with open('estudo/ids_features.pkl', 'rb') as f:
    features = pickle.load(f)

print(f"Total de features: {len(features)}")
for i, f in enumerate(features[:78]):
    print(f"  {i+1}. {f}")