import { useState, useEffect, useRef, useCallback } from 'react';
import { api } from '../src/services/api';

export interface SnifferStatus {
  running:            boolean;
  contador:           number;
  anomalias:          number;
  bloqueios:          number;
  taxa_anomalia:      number;
  ips_bloqueados:     string[];
  whitelist:          string[];
  stats:              Record<string, number>;
  interface_ativas:   string[];
  interface_inativas: string[];
  portas_tcp:         Record<string, number>;
  portas_udp:         Record<string, number>;
  ultimos_pacotes:    any[];
  contagem_ips:       Record<string, number>;  // ← ADICIONA
}

const STATUS_VAZIO: SnifferStatus = {
  running: false, contador: 0, anomalias: 0, bloqueios: 0,
  taxa_anomalia: 0, ips_bloqueados: [], whitelist: [], stats: {},
  interface_ativas: [], interface_inativas: [],
  portas_tcp: {}, portas_udp: {}, ultimos_pacotes: [],
  contagem_ips: {},  // ← ADICIONA
};

export function useSniffer() {
  const [status, setStatus]     = useState<SnifferStatus>(STATUS_VAZIO);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState('');
  const [pacotes, setPacotes]   = useState<any[]>([]);
  const wsRef                   = useRef<WebSocket | null>(null);

  // Busca status via HTTP
  const fetchStatus = useCallback(async () => {
    try {
      const res = await api.get('/sniffer/status');
      setStatus(res.data);
    } catch {
      setError('Erro ao obter status do sniffer');
    }
  }, []);

  // Polling a cada 5 segundos
  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  // WebSocket — pacotes em tempo real
  const conectarWS = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    const token = localStorage.getItem('access_token');
    const ws = new WebSocket(`ws://localhost:8000/sniffer/ws?token=${token}`);

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.tipo === 'anomalia' || data.tipo === 'normal') {
        setPacotes(prev => [data, ...prev].slice(0, 50));
      }
      if (data.tipo === 'status') {
        setStatus(prev => ({ ...prev, ...data }));
      }
    };

    ws.onerror = () => setError('Erro na ligação WebSocket');
    ws.onclose = () => {
      // reconecta após 3 segundos se o sniffer estiver ativo
      setTimeout(() => {
        if (status.running) conectarWS();
      }, 3000);
    };

    wsRef.current = ws;
  }, [status.running]);

  // Iniciar sniffer
  const iniciar = async (interface_?: string, filtro?: string, bloquear = true) => {
    try {
      setLoading(true);
      setError('');
      await api.post('/sniffer/start', {
        interface: interface_ || null,
        filtro:    filtro    || null,
        bloquear,
      });
      await fetchStatus();
      conectarWS();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao iniciar sniffer');
    } finally {
      setLoading(false);
    }
  };

  // Pausar sniffer
  const pausar = async () => {
    try {
      setLoading(true);
      setError('');
      await api.post('/sniffer/stop');
      await fetchStatus();
      wsRef.current?.close();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao pausar sniffer');
    } finally {
      setLoading(false);
    }
  };

  // Reboot sniffer
  const reboot = async (interface_?: string, filtro?: string) => {
    try {
      setLoading(true);
      setError('');
      await api.post('/sniffer/reboot', {
        interface: interface_ || null,
        filtro:    filtro    || null,
        bloquear:  true,
      });
      await fetchStatus();
      conectarWS();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao reiniciar sniffer');
    } finally {
      setLoading(false);
    }
  };

  // Limpa WebSocket ao desmontar
  useEffect(() => {
    return () => wsRef.current?.close();
  }, []);

  return {
    status, loading, error, pacotes,
    iniciar, pausar, reboot, fetchStatus,
  };
}