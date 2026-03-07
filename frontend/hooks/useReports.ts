import { useState, useEffect } from "react";
import { api } from "../src/services/api";

type Incident = {
  id: number;
  timestamp: string;
  evento: string;
  origem: string;
  destino: string;
  protocolo: string;
  severidade: string;
  status: string;
};

type Summary = {
  total_eventos:       number;
  criticos:            number;
  altos:               number;
  medios:              number;
  bloqueados:          number;
  total_ips_bloqueados: number;
};

type AttackVolume = {
  time:    string;
  attacks: number;
};

export function useReports(period: string, severity: string) {
  const [summary, setSummary]       = useState<Summary | null>(null);
  const [incidents, setIncidents]   = useState<Incident[]>([]);
  const [volume, setVolume]         = useState<AttackVolume[]>([]);
  const [loading, setLoading]       = useState(true);
  const [error, setError]           = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    Promise.all([
      api.get(`/reports/summary?period=${period}&severity=${severity}`),
      api.get(`/reports/incidents?period=${period}&severity=${severity}&limit=10`),
      api.get(`/reports/attack-volume?period=${period}`),
    ])
      .then(([summaryRes, incidentsRes, volumeRes]) => {
        setSummary(summaryRes.data);
        setIncidents(incidentsRes.data);
        setVolume(volumeRes.data);
      })
      .catch(() => setError("Erro ao carregar relatório"))
      .finally(() => setLoading(false));
  }, [period, severity]);

  return { summary, incidents, volume, loading, error };
}