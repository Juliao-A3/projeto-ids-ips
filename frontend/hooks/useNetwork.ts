import { useState, useEffect, useCallback, useRef } from "react";
import { api } from "../src/services/api";

type Interface = {
  name: string;
  status: "UP" | "DOWN";
  speed: string;
  ip: string;
  mac: string;
  packets_sent: number;
  packets_recv: number;
  monitored: boolean;
};

type BlockedIP = {
  id: number;
  ip_bloqueado: string;
  motivo: string;
  bloqueado_em: string;
};

export type NetworkConfigSchema = {
  capture_interface: string;
  capture_interfaces?: string[];
  zone_map?: Record<string, string>;
  promiscuous_mode: boolean;
  bpf_filter: string;
  whitelist: string;
};

const extractConfiguredInterfaces = (
  config: Partial<NetworkConfigSchema> | null | undefined
) => {
  if (!config) return [];

  if (
    Array.isArray(config.capture_interfaces) &&
    config.capture_interfaces.length > 0
  ) {
    return config.capture_interfaces;
  }

  return String(config.capture_interface || "eth0")
    .split(",")
    .map((entry: string) => entry.trim())
    .filter(Boolean);
};

const mergeInterfaces = (
  allIfaces: Interface[],
  monitoredNames: string[]
): Interface[] =>
  allIfaces.map((iface) => ({
    ...iface,
    monitored: monitoredNames.includes(iface.name),
  }));

export function useNetwork() {
  const [interfaces, setInterfaces] = useState<Interface[]>([]);
  const [blockedIps, setBlockedIps] = useState<BlockedIP[]>([]);
  const [config, setConfig] = useState<NetworkConfigSchema>({
    capture_interface: "eth0",
    capture_interfaces: ["eth0"],
    zone_map: {},
    promiscuous_mode: true,
    bpf_filter: "",
    whitelist: "192.168.1.0/24, 10.0.0.0/8, 127.0.0.1",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const configRef = useRef(config);
  useEffect(() => {
    configRef.current = config;
  }, [config]);

  // Busca TODAS as interfaces do SO + quais estão a ser monitorizadas
  const fetchInterfaces = useCallback(() => {
    Promise.all([
      api.get("/network/interfaces"),
      api
        .get("/sniffer/interfaces")
        .catch(() => ({ data: { monitored_interfaces: [] } })),
    ])
      .then(([ifRes, sniffRes]) => {
        const monitored: string[] =
          sniffRes.data.monitored_interfaces || [];
        const all = mergeInterfaces(ifRes.data as Interface[], monitored);
        setInterfaces((prev) =>
          JSON.stringify(prev) === JSON.stringify(all) ? prev : all
        );
      })
      .catch(() => setError("Erro ao carregar interfaces"));
  }, []);

  const fetchBlockedIps = useCallback(() => {
    api
      .get("/network/blocked-ips")
      .then((r) =>
        setBlockedIps((prev) =>
          JSON.stringify(prev) === JSON.stringify(r.data) ? prev : r.data
        )
      )
      .catch(() => {});
  }, []);

  const fetchConfig = useCallback(() => {
    api
      .get("/network/config")
      .then((r) => {
        if (r.data) {
          const configuredInterfaces = extractConfiguredInterfaces(r.data);
          const next: NetworkConfigSchema = {
            ...r.data,
            capture_interface:
              r.data.capture_interface ||
              (Array.isArray(r.data.capture_interfaces)
                ? r.data.capture_interfaces.join(",")
                : "eth0"),
            capture_interfaces:
              Array.isArray(r.data.capture_interfaces) &&
              r.data.capture_interfaces.length > 0
                ? r.data.capture_interfaces
                : configuredInterfaces,
            zone_map: r.data.zone_map || {},
          };
          setConfig((prev) =>
            JSON.stringify(prev) === JSON.stringify(next) ? prev : next
          );
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);

    Promise.all([
      // Todas as interfaces + monitorizadas em paralelo
      Promise.all([
        api.get("/network/interfaces"),
        api
          .get("/sniffer/interfaces")
          .catch(() => ({ data: { monitored_interfaces: [] } })),
      ]).then(([ifRes, sniffRes]) => {
        const monitored: string[] =
          sniffRes.data.monitored_interfaces || [];
        return {
          data: mergeInterfaces(ifRes.data as Interface[], monitored),
        } as any;
      }),
      api.get("/network/blocked-ips").catch(() => ({ data: [] })),
      api.get("/network/config").catch(() => ({ data: null })),
    ])
      .then(([ifRes, ipRes, cfgRes]) => {
        setInterfaces(ifRes.data);
        setBlockedIps(ipRes.data);
        if (cfgRes.data) {
          const configuredInterfaces = extractConfiguredInterfaces(cfgRes.data);
          const next: NetworkConfigSchema = {
            ...cfgRes.data,
            capture_interface:
              cfgRes.data.capture_interface ||
              (Array.isArray(cfgRes.data.capture_interfaces)
                ? cfgRes.data.capture_interfaces.join(",")
                : "eth0"),
            capture_interfaces:
              Array.isArray(cfgRes.data.capture_interfaces) &&
              cfgRes.data.capture_interfaces.length > 0
                ? cfgRes.data.capture_interfaces
                : configuredInterfaces,
            zone_map: cfgRes.data.zone_map || {},
          };
          setConfig(next);
        }
      })
      .catch(() => setError("Erro ao carregar rede"))
      .finally(() => setLoading(false));

    const interfaceInterval  = setInterval(fetchInterfaces, 5000);
    const configInterval     = setInterval(fetchConfig, 10000);
    const blockedIpsInterval = setInterval(fetchBlockedIps, 5000);

    return () => {
      clearInterval(interfaceInterval);
      clearInterval(configInterval);
      clearInterval(blockedIpsInterval);
    };
  }, []);

  const unblockIp = async (id: number) => {
    try {
      await api.delete(`/network/blocked-ips/${id}`);
      setSuccessMsg("IP desbloqueado com sucesso!");
      fetchBlockedIps();
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch {
      setError("Erro ao desbloquear IP");
      setTimeout(() => setError(null), 3000);
    }
  };

  const saveConfig = async (data: NetworkConfigSchema) => {
    try {
      setSaving(true);
      await api.put("/network/config", data);
      setConfig(data);
      setSuccessMsg("Configuração salva com sucesso!");
      setTimeout(() => setSuccessMsg(null), 3000);
      return true;
    } catch {
      setError("Erro ao salvar configuração");
      setTimeout(() => setError(null), 3000);
      return false;
    } finally {
      setSaving(false);
    }
  };

  const restoreDefaults = async () => {
    const defaults: NetworkConfigSchema = {
      capture_interface: "eth0",
      capture_interfaces: ["eth0"],
      zone_map: {},
      promiscuous_mode: true,
      bpf_filter: "",
      whitelist: "192.168.1.0/24, 10.0.0.0/8, 127.0.0.1",
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