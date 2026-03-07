import { useState, useEffect, type SetStateAction } from "react";
import { api } from "../src/services/api";

type NotificationConfig = {
  email_provider: string;
  smtp_server: string;
  smtp_port: number;
  smtp_ssl: boolean;
  smtp_username: string;
  smtp_password: string;
  smtp_enabled: boolean;
  telegram_token: string;
  telegram_chat_id: string;
  telegram_enabled: boolean;
  teams_webhook: string;
  teams_enabled: boolean;
  trigger_critical: boolean;
  trigger_high: boolean;
  trigger_medium: boolean;
};

const defaultConfig: NotificationConfig = {
  email_provider: "gmail",
  smtp_server:        "",
  smtp_port:          587,
  smtp_ssl:           true,
  smtp_username:      "",
  smtp_password:      "",
  smtp_enabled:       false,
  telegram_token:     "",
  telegram_chat_id:   "",
  telegram_enabled:   false,
  teams_webhook:      "",
  teams_enabled:      false,
  trigger_critical:   true,
  trigger_high:       true,
  trigger_medium:     false,
};

export function useNotifications() {
  const [config, setConfig]   = useState<NotificationConfig>(defaultConfig);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving]   = useState(false);
  const [testing, setTesting] = useState<string | null>(null);
  const [error, setError]     = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // carrega configurações ao iniciar
  useEffect(() => {
    api.get("/notifications/config")
      .then((res: { data: SetStateAction<NotificationConfig>; }) => setConfig(res.data))
      .catch(() => setError("Erro ao carregar configurações"))
      .finally(() => setLoading(false));
  }, []);

  const saveConfig = async () => {
    setSaving(true);
    setError(null);
    setSuccessMsg(null);
    try {
      await api.put("/notifications/config", config);
      setSuccessMsg("Configurações salvas com sucesso!");
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch {
      setError("Erro ao salvar configurações");
    } finally {
      setSaving(false);
    }
  };

  const testChannel = async (channel: "email" | "telegram" | "teams") => {
    setTesting(channel);
    setError(null);
    setSuccessMsg(null);
    try {
      await api.post(`/notifications/test/${channel}`);
      setSuccessMsg(`Teste de ${channel} enviado com sucesso!`);
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || `Erro ao testar ${channel}`);
    } finally {
      setTesting(null);
    }
  };

  const restoreDefaults = () => {
    setConfig(defaultConfig);
  };

  return {
    config, setConfig,
    loading, saving, testing,
    error, successMsg,
    saveConfig, testChannel, restoreDefaults,
  };
}