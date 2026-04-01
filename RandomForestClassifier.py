import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Compatibilidade com pickles antigos que referenciam RandomForestClassifier.dtype.
dtype = np.dtype
