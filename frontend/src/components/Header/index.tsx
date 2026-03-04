import { Settings, FileText } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
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
  UserAvatar,
  UserContainer,
  NameUser,
  UserContent,
  DescriptionUser,
} from './styles';

export function Header() {
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState<{cpu_load:number;memory:number;network_gbps:number} | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const resp = await api.get('/service/system/metrics');
        setMetrics(resp.data);
      } catch (e) {
        console.error('Erro ao buscar métricas', e);
      }
    };
    fetchMetrics();
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
            <StatusText>Sistema Operacional Estável</StatusText>
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
              <SpeedStatus>{metrics ? `${metrics.network_gbps} Gbps` : '--'}</SpeedStatus>
            </StatusInfo>
          </Metric>
        </HeaderCenter>

        <AlertConfig>
          <ConfigButton onClick={() => navigate('/settings/ai-model')}>
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