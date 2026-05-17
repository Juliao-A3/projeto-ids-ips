import { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
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
<<<<<<< HEAD
=======
  const wsRetryTimeoutRef       = useRef<number | null>(null);
  const wsRefreshAttemptedRef   = useRef(false);
  const statusRequestInFlightRef = useRef(false);
  const runningRef              = useRef(false);
  const lastAnomaliasRef        = useRef(0);

  useEffect(() => {
    runningRef.current = status.running;
  }, [status.running]);
>>>>>>> 85b6a24ae68ef8aae4e61f071fe9a0a7eb0089e7

  const normalizarPacote = useCallback((raw: any) => {
    const pkt = { ...(raw || {}) };
    const tipoRaw = String(pkt?.tipo || '').toLowerCase();
    const labelRaw = String(pkt?.label || '').toLowerCase().trim();
    const ataquePorTipo = tipoRaw === 'ataque' || tipoRaw === 'alerta' || tipoRaw === 'anomalia';
    const ataquePorFlag = Boolean(pkt?.is_attack);
    const ataquePorLabel = labelRaw !== '' && labelRaw !== 'benign' && labelRaw !== 'normal';
    const isAtaque = ataquePorTipo || ataquePorFlag || ataquePorLabel;

    pkt.tipo = isAtaque ? 'alerta' : 'normal';
    if (!pkt.timestamp) {
      pkt.timestamp = new Date().toISOString();
    }
    return pkt;
  }, []);

  const mergePacotes = useCallback((atuais: any[], novos: any[]) => {
    const all = [...(atuais || []), ...(novos || [])];
    const seen = new Set<string>();
    const dedup: any[] = [];

    for (const p of all) {
      const key = [
        p?.id ?? '',
        p?.timestamp ?? '',
        p?.src_ip ?? '',
        p?.src_port ?? '',
        p?.dst_ip ?? p?.dest_ip ?? '',
        p?.dst_port ?? '',
        p?.label ?? '',
        p?.tipo ?? '',
      ].join('|');

      if (!seen.has(key)) {
        seen.add(key);
        dedup.push(p);
      }
    }

    dedup.sort((a, b) => {
      const aAlerta = String(a?.tipo || '').toLowerCase() === 'alerta' ? 1 : 0;
      const bAlerta = String(b?.tipo || '').toLowerCase() === 'alerta' ? 1 : 0;
      if (aAlerta !== bAlerta) {
        return bAlerta - aAlerta;
      }
      const ta = new Date(a?.timestamp || 0).getTime();
      const tb = new Date(b?.timestamp || 0).getTime();
      return tb - ta;
    });

    return dedup.slice(0, 120);
  }, []);

  // Busca status via HTTP
  const fetchStatus = useCallback(async () => {
    if (statusRequestInFlightRef.current) {
      return;
    }

    statusRequestInFlightRef.current = true;
    try {
      const res = await api.get('/sniffer/status');
      setStatus(res.data);
      const anomaliasAtuais = Number(res.data?.anomalias || 0);

      // Fallback: mantém os logs sincronizados com o backend caso o WS atrase/perca eventos.
      if (Array.isArray(res.data?.ultimos_pacotes)) {
        const pacotesStatus = res.data.ultimos_pacotes.map(normalizarPacote);
        setPacotes((prev) => {
          const merged = mergePacotes(prev, pacotesStatus);

          // Failsafe: se contador de anomalias subir e não houver detalhe em tempo real,
          // cria entrada sintética com os dados do alerta mais recente conhecido.
          if (anomaliasAtuais > lastAnomaliasRef.current) {
            const diff = Math.min(anomaliasAtuais - lastAnomaliasRef.current, 5);
            const alertaBase =
              merged.find((p) => String(p?.tipo || '').toLowerCase() === 'alerta') ||
              pacotesStatus.find((p: { tipo: any; }) => String(p?.tipo || '').toLowerCase() === 'alerta') ||
              merged[0] ||
              pacotesStatus[0] ||
              {};

            const agora = new Date().toISOString();
            const sint = Array.from({ length: diff }).map((_, idx) => ({
              id: `fallback-alert-${agora}-${idx}`,
              timestamp: agora,
              src_ip: alertaBase.src_ip || '-',
              dst_ip: alertaBase.dst_ip || alertaBase.dest_ip || '-',
              src_port: alertaBase.src_port || 0,
              dst_port: alertaBase.dst_port || 0,
              protocolo: alertaBase.protocolo || 'OUTRO',
              label: alertaBase.label || 'ALERTA DETECTADO',
              is_attack: true,
              tipo: 'alerta',
            }));

            return mergePacotes(sint, merged);
          }

          return merged;
        });
      }
      lastAnomaliasRef.current = anomaliasAtuais;
    } catch {
      setError('Erro ao obter status do sniffer');
    } finally {
      statusRequestInFlightRef.current = false;
    }
  }, [mergePacotes, normalizarPacote]);

<<<<<<< HEAD
  // Polling a cada 5 segundos
  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
=======
  // Polling de apoio quando não há eventos WS
  useEffect(() => {
    void fetchStatus();
    const interval = setInterval(() => {
      void fetchStatus();
    }, 5000);
>>>>>>> 85b6a24ae68ef8aae4e61f071fe9a0a7eb0089e7
    return () => clearInterval(interval);
  }, [fetchStatus]);

  const refreshAccessToken = useCallback(async (): Promise<string | null> => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      return null;
    }

    const apiBase = String(api.defaults.baseURL || '').trim();
    const apiUrl = apiBase ? new URL(apiBase, window.location.origin) : new URL(window.location.origin);

    try {
      const response = await axios.post(`${apiUrl.origin}/auth/refresh`, {
        refresh_token: refreshToken,
      });
      const newToken = String(response?.data?.access_token || '').trim();
      if (!newToken) {
        return null;
      }

      localStorage.setItem('access_token', newToken);
      return newToken;
    } catch {
      return null;
    }
  }, []);

  const getTokenExpiryMs = useCallback((token: string): number | null => {
    try {
      const payloadB64 = token.split('.')[1];
      if (!payloadB64) {
        return null;
      }

      const normalized = payloadB64.replace(/-/g, '+').replace(/_/g, '/');
      const padded = normalized + '='.repeat((4 - (normalized.length % 4)) % 4);
      const payload = JSON.parse(window.atob(padded));
      const expSec = Number(payload?.exp || 0);
      if (!Number.isFinite(expSec) || expSec <= 0) {
        return null;
      }

      return expSec * 1000;
    } catch {
      return null;
    }
  }, []);

  const ensureValidAccessToken = useCallback(async (): Promise<string | null> => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return await refreshAccessToken();
    }

    const expiryMs = getTokenExpiryMs(token);
    if (expiryMs && expiryMs - Date.now() < 60_000) {
      return await refreshAccessToken();
    }

    return token;
  }, [getTokenExpiryMs, refreshAccessToken]);

  // WebSocket — pacotes em tempo real
<<<<<<< HEAD
  const conectarWS = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    const token = localStorage.getItem('access_token');
    const ws = new WebSocket(`ws://localhost:8000/sniffer/ws?token=${token}`);
=======
  const conectarWS = useCallback(async () => {
    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const token = await ensureValidAccessToken();
    if (!token) {
      setError('Sem token para ligação WebSocket');
      return;
    }

    const apiBase = String(api.defaults.baseURL || '').trim();
    const apiUrl = apiBase ? new URL(apiBase, window.location.origin) : new URL(window.location.origin);
    const wsProto = apiUrl.protocol === 'https:' ? 'wss' : 'ws';
    const wsUrl = `${wsProto}://${apiUrl.host}/sniffer/ws?token=${encodeURIComponent(token)}`;
    const ws = new WebSocket(wsUrl);
>>>>>>> 85b6a24ae68ef8aae4e61f071fe9a0a7eb0089e7

    ws.onopen = () => {
      wsRefreshAttemptedRef.current = false;
      setError('');
    };

  ws.onmessage = (e) => {
    const data = JSON.parse(e.data);
<<<<<<< HEAD
    if (data.tipo === 'ataque' || data.tipo === 'normal') {  // ← era 'anomalia'
      setPacotes(prev => [data, ...prev].slice(0, 50));
    }
    if (data.tipo === 'status') {
      setStatus(prev => ({ ...prev, ...data }));
=======

    if (data.tipo === 'status') {
      setStatus(prev => ({ ...prev, ...data }));
      return;
    }

    // Pacote em tempo real: normaliza antes de inserir para não perder alertas.
    if (data && (data.src_ip || data.dst_ip || data.dest_ip)) {
      const pkt = normalizarPacote(data);
      const isAtaque = pkt.tipo === 'alerta';

      setPacotes((prev) => mergePacotes([pkt], prev));
      setStatus(prev => {
        const novoContador = (prev.contador || 0) + 1;
        const novasAnomalias = (prev.anomalias || 0) + (isAtaque ? 1 : 0);
        const novaTaxa = novoContador > 0 ? Number(((novasAnomalias / novoContador) * 100).toFixed(2)) : 0;
        return {
          ...prev,
          contador: novoContador,
          anomalias: novasAnomalias,
          taxa_anomalia: novaTaxa,
        };
      });
      window.dispatchEvent(new CustomEvent('sniffer:update', { detail: pkt }));
>>>>>>> 85b6a24ae68ef8aae4e61f071fe9a0a7eb0089e7
    }
  };

    ws.onerror = () => setError('Erro na ligação WebSocket');
<<<<<<< HEAD
    ws.onclose = () => {
      // reconecta após 3 segundos se o sniffer estiver ativo
      setTimeout(() => {
        if (status.running) conectarWS();
      }, 3000);
    };

    wsRef.current = ws;
  }, [status.running]);
=======
    ws.onclose = (event) => {
      wsRef.current = null;

      // 1008 normalmente indica token inválido/autorização recusada.
      if (event.code === 1008) {
        if (!wsRefreshAttemptedRef.current) {
          wsRefreshAttemptedRef.current = true;
          void (async () => {
            const refreshed = await refreshAccessToken();
            if (refreshed && runningRef.current) {
              await conectarWS();
              return;
            }
            setError('WebSocket recusado (token inválido ou expirado)');
          })();
          return;
        }

        setError('WebSocket recusado (token inválido ou expirado)');
        return;
      }

      // Reconeção com pequeno atraso para evitar loop agressivo no Firefox.
      if (runningRef.current) {
        if (wsRetryTimeoutRef.current) {
          window.clearTimeout(wsRetryTimeoutRef.current);
        }
        wsRetryTimeoutRef.current = window.setTimeout(() => {
          void conectarWS();
        }, 1000);
      }
    };

    wsRef.current = ws;
  }, [ensureValidAccessToken, mergePacotes, normalizarPacote, refreshAccessToken]);

  // Cleanup global do WebSocket
  useEffect(() => {
    return () => {
      if (wsRetryTimeoutRef.current) {
        window.clearTimeout(wsRetryTimeoutRef.current);
        wsRetryTimeoutRef.current = null;
      }
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!status.running && wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (status.running) {
      void conectarWS();
    }
  }, [status.running, conectarWS]);
>>>>>>> 85b6a24ae68ef8aae4e61f071fe9a0a7eb0089e7

  // Iniciar sniffer
  const iniciar = async (interface_?: string, filtro?: string, bloquear = true) => {
    try {
      setLoading(true);
      setError('');
      // Abre WS já no arranque para reduzir latência dos primeiros logs.
      void conectarWS();
      await api.post('/sniffer/start', {
        interface: interface_ || null,
        filtro:    filtro    || null,
        bloquear,
      });
      await fetchStatus();
      void conectarWS();
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
      void conectarWS();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao reiniciar sniffer');
    } finally {
      setLoading(false);
    }
  };

  return {
    status, loading, error, pacotes,
    iniciar, pausar, reboot, fetchStatus,
  };
}