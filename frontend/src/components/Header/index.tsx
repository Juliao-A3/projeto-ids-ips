import { Settings, FileText } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

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
              <CpuPorcent>12%</CpuPorcent>
            </StatusInfo>
            <StatusInfo>
              <Loadcpu>MEMORY</Loadcpu>
              <CpuPorcent>34%</CpuPorcent>
            </StatusInfo>
            <StatusInfo>
              <Loadcpu>NETWORK</Loadcpu>
              <SpeedStatus>1.2 Gbps</SpeedStatus>
            </StatusInfo>
          </Metric>
        </HeaderCenter>

        <AlertConfig>
          <UserContainer>
              <UserContent>
                  <NameUser>Julio Domingos</NameUser>
                  <DescriptionUser>ANALISTA DE SEGURANÇA</DescriptionUser>
              </UserContent>
              <UserAvatar>JD</UserAvatar>
          </UserContainer>
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