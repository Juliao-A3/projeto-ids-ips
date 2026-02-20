import { AlertTriangle, Check, XCircle } from "lucide-react";
import { Container ,Header, Title, StatusBadge, StatusIcon, StatusText, ProgressSection, ProgressHeader, ProgressLabel, ProgressValue, ProgressBarContainer, ProgressBarFill } from "./styles";

interface TrafficIntegrityStatusProps {
    percentage?: number;
}

const TrafficIntegrityStatus = ({ percentage = 15 }: TrafficIntegrityStatusProps) => {

    const getStatus = () => {
        if (percentage >= 80) return { text: 'Estável', icon: Check };
        if (percentage >= 50) return { text: 'Atenção', icon: AlertTriangle };
        return { text: 'Crítico', icon: XCircle };
      };
  
    const status = getStatus();
    const StatusIconComponent = status.icon;
    return (
        <Container>
        <Header>
          <Title>Integridade do Tráfego</Title>
          <StatusBadge percentage={percentage}>
            <StatusIcon percentage={percentage}>
              <StatusIconComponent size={14} strokeWidth={3} />
            </StatusIcon>
            <StatusText percentage={percentage}>{status.text}</StatusText>
          </StatusBadge>
        </Header>
        
        <ProgressSection>
          <ProgressHeader>
            <ProgressLabel>Anomalias de Tráfego</ProgressLabel>
            <ProgressValue percentage={percentage}>{percentage}%</ProgressValue>
          </ProgressHeader>
          <ProgressBarContainer>
            <ProgressBarFill percentage={percentage} />
          </ProgressBarContainer>
        </ProgressSection>
      </Container>
    );
  };
  
  export default TrafficIntegrityStatus;