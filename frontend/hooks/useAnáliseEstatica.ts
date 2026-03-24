import { useState } from 'react';
import { api } from '../src/services/api';

export interface ResultadoTeste {
  id:        string;
  ficheiro:  string;
  modelo:    string;
  resultado: {
    total_pacotes: number;
    anomalias:     number;
    normais:       number;
    taxa_anomalia: number;
    pacotes:       any[];
  };
  tamanho_kb: number;
}

export interface HistoricoItem {
  ficheiro:    string;
  data_teste:  string;
  modelo:      string;
  n_normais:   number;
  n_ataques:   number;
  total_pcaps: number;
}

export function useAnaliseEstatica() {
  const [loading, setLoading]         = useState(false);
  const [resultado, setResultado]     = useState<ResultadoTeste | null>(null);
  const [historico, setHistorico]     = useState<HistoricoItem[]>([]);
  const [testeAtual, setTesteAtual]   = useState<any>(null);
  const [error, setError]             = useState('');

  // Upload e testar PCAP
  const testarUpload = async (ficheiro: File, modelo?: string, limite?: number) => {
    try {
      setLoading(true);
      setError('');
      const form = new FormData();
      form.append('ficheiro', ficheiro);
      const params = new URLSearchParams();
      if (modelo) params.append('modelo', modelo);
      const res = await api.post(
        `/sniffer/testar/upload?${params.toString()}`,
        form,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      setResultado(res.data);
      return res.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao testar ficheiro');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Testar pasta
  const testarPasta = async (pasta: string, modelo?: string, maxPacotes = 5000) => {
    try {
      setLoading(true);
      setError('');
      await api.post('/sniffer/testar/pasta', { pasta, modelo, max_pacotes: maxPacotes });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao testar pasta');
    } finally {
      setLoading(false);
    }
  };

  // Buscar histórico
  const fetchHistorico = async () => {
    try {
      const res = await api.get('/sniffer/testar/historico');
      setHistorico(res.data.historico || []);
      setTesteAtual(res.data.teste_atual || null);
    } catch {
      setError('Erro ao carregar histórico');
    }
  };

  // Exportar CSV
  const exportarCSV = (dados: any[]) => {
    if (!dados.length) return;
    const headers = Object.keys(dados[0]).join(',');
    const rows    = dados.map(d => Object.values(d).join(',')).join('\n');
    const blob    = new Blob([headers + '\n' + rows], { type: 'text/csv' });
    const url     = URL.createObjectURL(blob);
    const a       = document.createElement('a');
    a.href        = url;
    a.download    = `aegis_resultado_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return {
    loading, resultado, historico, testeAtual, error,
    testarUpload, testarPasta, fetchHistorico, exportarCSV,
  };
}