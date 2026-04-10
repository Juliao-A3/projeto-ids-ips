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
  const runningRef              = useRef(false);

  useEffect(() => {
    runningRef.current = status.running;
  }, [status.running]);

  // Busca status via HTTP
  const fetchStatus = useCallback(async () => {
    try {
      const res = await api.get('/sniffer/status');
      setStatus(res.data);
    } catch {
      setError('Erro ao obter status do sniffer');
    }
  }, []);

  // Polling mais curto para reduzir atraso visual quando não há eventos WS
  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 2000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  // WebSocket — pacotes em tempo real
  const conectarWS = useCallback(() => {
    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const token = localStorage.getItem('access_token');
    const isHttps = window.location.protocol === 'https:';
    const wsProto = isHttps ? 'wss' : 'ws';
    const wsHost = window.location.hostname;
    const wsUrl = `${wsProto}://${wsHost}:8000/sniffer/ws?token=${token ?? ''}`;
    const ws = new WebSocket(wsUrl);

  ws.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if (data.tipo === 'ataque' || data.tipo === 'normal') {  // ← era 'anomalia'
      setPacotes(prev => [data, ...prev].slice(0, 50));
      setStatus(prev => {
        const novoContador = (prev.contador || 0) + 1;
        const novasAnomalias = (prev.anomalias || 0) + (data.tipo === 'ataque' ? 1 : 0);
        const novaTaxa = novoContador > 0 ? Number(((novasAnomalias / novoContador) * 100).toFixed(2)) : 0;
        return {
          ...prev,
          contador: novoContador,
          anomalias: novasAnomalias,
          taxa_anomalia: novaTaxa,
        };
      });
      window.dispatchEvent(new CustomEvent('sniffer:update', { detail: data }));
    }
    if (data.tipo === 'status') {
      setStatus(prev => ({ ...prev, ...data }));
    }
  };

    ws.onerror = () => setError('Erro na ligação WebSocket');
    ws.onclose = () => {
      wsRef.current = null;
      // reconecta rápido se o sniffer estiver ativo
      setTimeout(() => {
        if (runningRef.current) conectarWS();
      }, 1000);
    };

    wsRef.current = ws;
  }, []);

  useEffect(() => {
    if (status.running) {
      conectarWS();
      return;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, [status.running, conectarWS]);

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