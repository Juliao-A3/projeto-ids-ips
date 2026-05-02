"""Compatibilidade com o predictor legado.

Este módulo reexporta a implementação Keras-first de `predictor_v2.py`
para manter o `sniffer_realtime.py` e outros consumidores funcionando
sem duplicar lógica.
"""

try:
    from . import predictor_v2 as _predictor_impl
except ImportError:
    import predictor_v2 as _predictor_impl

ModelPredictor = _predictor_impl.ModelPredictor
predict_flow = _predictor_impl.predict_flow
feature_names = getattr(_predictor_impl, "feature_names", [])
