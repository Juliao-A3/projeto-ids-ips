import { useEffect, useState } from "react";

type Status = {
  modelo_ativo: string;
  uptime: string;
  latencia_ms: number;
  acuracia: number;
};

type AnomalyPoint = {
  time: string;
  score: number;
  threshold: number;
};

type Metrics = {
  latencia_ms: number;
  throughput: number;
  cpu_percent: number;
  memory_mb: number;
};

type AIData = {
  status: Status;
  anomaly_history: AnomalyPoint[];
  metrics: Metrics;
};

export function useAIMetrics() {
  const [data, setData]       = useState<AIData | null>(null);
  const [connected, setConnected] = useState(false);
  const [error, setError]     = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const ws = new WebSocket(`ws://localhost:8000/ai/ws/metrics?token=${token}`);

    ws.onopen = () => {
      setConnected(true);
      setError(null);
      console.log("[AI WebSocket] Conectado");
    };

    ws.onmessage = (event) => {
      const payload: AIData = JSON.parse(event.data);
      setData(payload);
    };

    ws.onerror = () => {
      setError("Erro de ligação ao servidor");
      setConnected(false);
    };

    ws.onclose = () => {
      setConnected(false);
      console.log("[AI WebSocket] Desligado");
    };

    return () => ws.close();
  }, []);

  return { data, connected, error };
}