import { useState, useEffect } from 'react';
import { api } from '../src/services/api';

export interface ModeloInfo {
  nome:        string;
  data_treino: string;
  acuracia:    number;
  versao:      string;
  features:    string[];
  n_features:  number;
  tipo:        string;
  tamanho_kb:  number;
}

export interface TreinarConfig {
  origem:        string;
  contamination: number;
  test_size:     number;
  max_amostras:  number;
}

export function useGestaoIA() {
  const [modelo, setModelo]         = useState<ModeloInfo | null>(null);
  const [modelos, setModelos]       = useState<any[]>([]);
  const [estatisticas, setEstat]    = useState<any>(null);
  const [treino, setTreino]         = useState<any>(null);
  const [inspecao, setInspecao]     = useState<any>(null);
  const [loading, setLoading]       = useState(false);
  const [treinando, setTreinando]   = useState(false);
  const [error, setError]           = useState('');

  // Buscar info do modelo ativo
  const fetchModelo = async () => {
    try {
      const res = await api.get('/sniffer/ia/modelo');
      setModelo(res.data);
    } catch {
      setError('Erro ao carregar modelo');
    }
  };

  // Buscar estatísticas completas
  const fetchEstatisticas = async () => {
    try {
      setLoading(true);
      const res = await api.get('/sniffer/ia/estatisticas');
      setEstat(res.data);
    } catch {
      setError('Erro ao carregar estatísticas');
    } finally {
      setLoading(false);
    }
  };

  // Listar modelos disponíveis
  const fetchModelos = async () => {
    try {
      const res = await api.get('/sniffer/ia/modelos');
      setModelos(res.data.modelos || []);
    } catch {
      setError('Erro ao listar modelos');
    }
  };

  // Inspecionar modelo específico
  const inspecionarModelo = async (nome?: string) => {
    try {
      setLoading(true);
      const params = nome ? `?modelo=${nome}` : '';
      const res = await api.get(`/sniffer/ia/inspecionar${params}`);
      setInspecao(res.data);
    } catch {
      setError('Erro ao inspecionar modelo');
    } finally {
      setLoading(false);
    }
  };

  // Iniciar treino
  const iniciarTreino = async (config: TreinarConfig) => {
    try {
      setTreinando(true);
      setError('');
      await api.post('/sniffer/ia/treinar', config);
      // polling do estado
      const interval = setInterval(async () => {
        try {
          const res = await api.get('/sniffer/ia/treino/status');
          setTreino(res.data);
          if (!res.data.a_correr) {
            clearInterval(interval);
            setTreinando(false);
            fetchModelos();
            fetchModelo();
          }
        } catch {
          clearInterval(interval);
          setTreinando(false);
        }
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao iniciar treino');
      setTreinando(false);
    }
  };

  useEffect(() => {
    fetchModelo();
    fetchEstatisticas();
    fetchModelos();
  }, []);

  return {
    modelo, modelos, estatisticas, treino, inspecao,
    loading, treinando, error,
    fetchModelo, fetchEstatisticas, fetchModelos,
    inspecionarModelo, iniciarTreino,
  };
}