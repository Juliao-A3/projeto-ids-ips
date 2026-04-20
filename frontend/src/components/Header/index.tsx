import { Settings, FileText } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useEffect, useRef, useState } from 'react';
import { api } from '../../services/api';

import {
  HeaderContainer,
  HeaderContent,
  HeaderLeft,
  HeaderCenter,
  Metric,
  SubtitleContainer,
  StatusText,
  StatusInfo,
  CpuPorcent,
  Loadcpu,
  SpeedStatus,
  AlertConfig,
  ConfigButton,
  RelatorioButton,
} from './styles';

export function Header() {
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState<{cpu_load:number;memory:number;network_gbps:number} | null>(null);
  const requestInFlightRef = useRef(false);
  const lastTimeoutLogAtRef = useRef(0);

  const systemStatus = !metrics
    ? { label: 'A VERIFICAR...', tone: 'muted' as const }
    : metrics.cpu_load >= 85 || metrics.memory >= 90
      ? { label: 'Sistema Operacional Crítico', tone: 'danger' as const }
      : metrics.cpu_load >= 65 || metrics.memory >= 75
        ? { label: 'Sistema Operacional em Atenção', tone: 'warning' as const }
        : { label: 'Sistema Operacional Estável', tone: 'success' as const };

  const formatNetworkSpeed = (gbps: number) => {
    if (!Number.isFinite(gbps) || gbps < 0) return '--';
    if (gbps >= 1) return `${gbps.toFixed(2)} Gbps`;
    const mbps = gbps * 1000;
    if (mbps >= 1) return `${mbps.toFixed(1)} Mbps`;
    const kbps = mbps * 1000;
    return `${kbps.toFixed(0)} Kbps`;
  };

  useEffect(() => {
    const fetchMetrics = async () => {
      if (requestInFlightRef.current) {
        return;
      }

      requestInFlightRef.current = true;
      try {
        const resp = await api.get('/service/system/metrics');
        setMetrics(resp.data);
      } catch (e: unknown) {
        const isTimeout = (e as any)?.code === 'ECONNABORTED' || String((e as any)?.message || '').includes('timeout');
        if (!isTimeout) {
          console.error('Erro ao buscar métricas', e);
        } else {
          const now = Date.now();
          if (now - lastTimeoutLogAtRef.current > 60000) {
            console.warn('Timeout ao buscar métricas. Tentando novamente no próximo ciclo.');
            lastTimeoutLogAtRef.current = now;
          }
        }
      } finally {
        requestInFlightRef.current = false;
      }
    };

    void fetchMetrics();
    const iv = setInterval(fetchMetrics, 5000);
    return () => clearInterval(iv);
  }, []);

  return (
    <HeaderContainer>
      <HeaderContent>
        <HeaderLeft>
          <div>
            <h1>AEGIS IDS</h1>
            <span>v4.0.2</span>
          </div>
          <SubtitleContainer>
            <span>·</span>
            <StatusText $tone={systemStatus.tone}>{systemStatus.label}</StatusText>
          </SubtitleContainer>
        </HeaderLeft>

        <HeaderCenter>
          <Metric>
            <StatusInfo>
              <Loadcpu>CPU LOAD</Loadcpu>
              <CpuPorcent>{metrics ? `${metrics.cpu_load}%` : '--'}</CpuPorcent>
            </StatusInfo>
            <StatusInfo>
              <Loadcpu>MEMORY</Loadcpu>
              <CpuPorcent>{metrics ? `${metrics.memory}%` : '--'}</CpuPorcent>
            </StatusInfo>
            <StatusInfo>
              <Loadcpu>NETWORK</Loadcpu>
              <SpeedStatus>{metrics ? formatNetworkSpeed(metrics.network_gbps) : '--'}</SpeedStatus>
            </StatusInfo>
          </Metric>
        </HeaderCenter>

        <AlertConfig>
          <ConfigButton onClick={() => navigate('/settings/network')}>
            <Settings size={14} />
            CONFIG
          </ConfigButton>
          <RelatorioButton onClick={() => navigate('/settings/relatorio')}>
            <FileText size={14} />
            GERAR RELATORIO
          </RelatorioButton>
        </AlertConfig>
      </HeaderContent>
    </HeaderContainer>
  );
}