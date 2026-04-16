import { AlertTriangle, Check, XCircle } from "lucide-react";
import { Container ,Header, Title, StatusBadge, StatusIcon, StatusText, ProgressSection, ProgressHeader, ProgressLabel, ProgressValue, ProgressBarContainer, ProgressBarFill } from "./styles";

interface TrafficIntegrityStatusProps {
  anomalyRate?: number;
  running?: boolean;
  hasAttack?: boolean;
}

const TrafficIntegrityStatus = ({ anomalyRate = 0, running = false, hasAttack = false }: TrafficIntegrityStatusProps) => {

  const normalizedAnomalyRate = Math.max(0, Math.min(100, Number(anomalyRate) || 0));
  const integrityPercentage = running ? Math.max(0, 100 - normalizedAnomalyRate) : 0;

    const getStatus = () => {
    if (!running) return { text: 'Inativo', icon: XCircle };
    if (hasAttack || normalizedAnomalyRate >= 20) return { text: 'Crítico', icon: XCircle };
    if (normalizedAnomalyRate >= 5) return { text: 'Atenção', icon: AlertTriangle };
    return { text: 'Estável', icon: Check };
      };
  
    const status = getStatus();
    const StatusIconComponent = status.icon;
    return (
        <Container>
        <Header>
          <Title>Integridade do Tráfego</Title>
          <StatusBadge $percentage={integrityPercentage}>
            <StatusIcon $percentage={integrityPercentage}>
              <StatusIconComponent size={14} strokeWidth={3} />
            </StatusIcon>
            <StatusText $percentage={integrityPercentage}>{status.text}</StatusText>
          </StatusBadge>
        </Header>
        
        <ProgressSection>
          <ProgressHeader>
            <ProgressLabel>Integridade Atual</ProgressLabel>
            <ProgressValue $percentage={integrityPercentage}>{integrityPercentage.toFixed(1)}%</ProgressValue>
          </ProgressHeader>
          <ProgressBarContainer>
            <ProgressBarFill $percentage={integrityPercentage} />
          </ProgressBarContainer>
        </ProgressSection>
      </Container>
    );
  };
  
  export default TrafficIntegrityStatus;