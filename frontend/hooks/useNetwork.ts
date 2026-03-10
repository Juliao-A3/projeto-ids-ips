import { useState, useEffect, useCallback } from "react";
import { api } from "../src/services/api";

type Interface = {
  name:         string;
  status:       "UP" | "DOWN";
  speed:        string;
  ip:           string;
  mac:          string;
  packets_sent: number;
  packets_recv: number;
};

type BlockedIP = {
  id:           number;
  ip_bloqueado: string;
  motivo:       string;
  bloqueado_em: string;
};

export type NetworkConfigSchema = {
  capture_interface: string;
  promiscuous_mode:  boolean;
  bpf_filter:        string;
  whitelist:         string;
};

export function useNetwork() {
  const [interfaces, setInterfaces] = useState<Interface[]>([]);
  const [blockedIps, setBlockedIps] = useState<BlockedIP[]>([]);
  const [config, setConfig]         = useState<NetworkConfigSchema>({
    capture_interface: "eth0",
    promiscuous_mode:  true,
    bpf_filter: "",
    whitelist: "192.168.1.0/24, 10.0.0.0/8, 127.0.0.1",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const fetchInterfaces = useCallback(() => { 
    api.get('/network/interfaces')
      .then(r => setInterfaces(r.data))
      .catch(() => setError('Erro ao carregar interfaces'));
  }, []);

  const fetchBlockedIps = useCallback(() => {
    api.get('/network/blocked-ips')
      .then(r => setBlockedIps(r.data))
      .catch(() => {});
  }, []);

  const fetchConfig = useCallback(() => {
    api.get('/network/config')
      .then(r => { if (r.data) setConfig(r.data); })
      .catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.get('/network/interfaces'),
      api.get('/network/blocked-ips').catch(() => ({ data: [] })),
      api.get('/network/config').catch(() => ({ data: null })),
    ])
      .then(([ifRes, ipRes, cfgRes]) => {
        setInterfaces(ifRes.data);
        setBlockedIps(ipRes.data);
        if (cfgRes.data) setConfig(cfgRes.data);
      })
      .catch(() => setError('Erro ao carregar rede'))
      .finally(() => setLoading(false));

    // atualiza interfaces a cada 5 segundos
    const interval = setInterval(fetchInterfaces, 5000);
    return () => clearInterval(interval);
  }, [fetchInterfaces]);

  const unblockIp = async (id: number) => {
    try {
      await api.delete(`/network/blocked-ips/${id}`);
      setSuccessMsg('IP desbloqueado com sucesso!');
      fetchBlockedIps();
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch {
      setError('Erro ao desbloquear IP');
      setTimeout(() => setError(null), 3000);
    }
  };

  const saveConfig = async (data: NetworkConfigSchema) => {
    try {
      setSaving(true);
      await api.put('/network/config', data);
      setConfig(data);
      setSuccessMsg('Configuração salva com sucesso!');
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch {
      setError('Erro ao salvar configuração');
      setTimeout(() => setError(null), 3000);
    } finally {
      setSaving(false);
    }
  };

  const restoreDefaults = async () => {
    const defaults: NetworkConfigSchema = {
      capture_interface: "eth0",
      promiscuous_mode:  true,
      bpf_filter:        "",
      whitelist:         "192.168.1.0/24, 10.0.0.0/8, 127.0.0.1",
    };
    await saveConfig(defaults);
  };

  return {
    interfaces,
    blockedIps,
    config,
    loading,
    saving,
    error,
    successMsg,
    unblockIp,
    saveConfig,
    restoreDefaults,
    fetchBlockedIps,
    fetchConfig,
  };
}