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
<<<<<<< HEAD
          <StatusBadge percentage={percentage}>
            <StatusIcon percentage={percentage}>
              <StatusIconComponent size={14} strokeWidth={3} />
            </StatusIcon>
            <StatusText percentage={percentage}>{status.text}</StatusText>
=======
          <StatusBadge $percentage={integrityPercentage}>
            <StatusIcon $percentage={integrityPercentage}>
              <StatusIconComponent size={14} strokeWidth={3} />
            </StatusIcon>
            <StatusText $percentage={integrityPercentage}>{status.text}</StatusText>
>>>>>>> 85b6a24ae68ef8aae4e61f071fe9a0a7eb0089e7
          </StatusBadge>
        </Header>
        
        <ProgressSection>
          <ProgressHeader>
<<<<<<< HEAD
            <ProgressLabel>Anomalias de Tráfego</ProgressLabel>
            <ProgressValue percentage={percentage}>{percentage}%</ProgressValue>
          </ProgressHeader>
          <ProgressBarContainer>
            <ProgressBarFill percentage={percentage} />
=======
            <ProgressLabel>Integridade Atual</ProgressLabel>
            <ProgressValue $percentage={integrityPercentage}>{integrityPercentage.toFixed(1)}%</ProgressValue>
          </ProgressHeader>
          <ProgressBarContainer>
            <ProgressBarFill $percentage={integrityPercentage} />
>>>>>>> 85b6a24ae68ef8aae4e61f071fe9a0a7eb0089e7
          </ProgressBarContainer>
        </ProgressSection>
      </Container>
    );
  };
  
  export default TrafficIntegrityStatus;