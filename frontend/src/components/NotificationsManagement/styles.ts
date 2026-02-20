import styled from 'styled-components';

export const Container = styled.div`
  flex: 1;
  padding: 24px;
  max-width: 1220px;
  width: 100%;
  overflow-y: auto;
  color: ${(props) => props.theme.colors.text.primary};
`;

export const Content = styled.main`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

export const Section = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

export const SectionHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 12px;
  border-bottom: 1px solid ${(props) => props.theme.colors.border};

  svg {
    color: ${(props) => props.theme.colors.primary};
  }
`;

export const SectionTitle = styled.h2`
  font-size: 12px;
  font-weight: 600;
  color: ${(props) => props.theme.colors.text.secondary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0;
`;

export const SectionContent = styled.div`
  background: ${(props) => props.theme.colors.surface};
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 8px;
  padding: 24px;
`;

export const EmailForm = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

export const FormRow = styled.div`
  display: flex;
  gap: 20px;
  align-items: flex-end;
`;

export const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

export const Label = styled.label`
  font-size: 11px;
  font-weight: 600;
  color: ${(props) => props.theme.colors.text.secondary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

export const Input = styled.input`
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 6px;
  padding: 12px 16px;
  font-size: 14px;
  color: ${(props) => props.theme.colors.text.primary};
  transition: all 0.2s;

  &:focus {
    outline: none;
    border-color: ${(props) => props.theme.colors.primary};
    background: rgba(255, 255, 255, 0.08);
  }

  &::placeholder {
    color: ${(props) => props.theme.colors.text.secondary};
    opacity: 0.5;
  }
`;

export const TestButton = styled.button`
  background: transparent;
  color: ${(props) => props.theme.colors.text.secondary};
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 6px;
  padding: 12px 20px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;

  &:hover {
    border-color: ${(props) => props.theme.colors.primary};
    color: ${(props) => props.theme.colors.primary};
  }
`;

export const IntegrationsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
`;

export const IntegrationCard = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 8px;
`;

export const IntegrationHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

export const IntegrationIcon = styled.span`
  font-size: 24px;
`;

export const IntegrationName = styled.span`
  font-size: 12px;
  font-weight: 600;
  color: ${(props) => props.theme.colors.text.primary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

export const IntegrationInput = styled.input`
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 6px;
  padding: 10px 14px;
  font-size: 12px;
  color: ${(props) => props.theme.colors.text.primary};
  transition: all 0.2s;

  &:focus {
    outline: none;
    border-color: ${(props) => props.theme.colors.primary};
    background: rgba(255, 255, 255, 0.08);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &::placeholder {
    color: ${(props) => props.theme.colors.text.secondary};
    opacity: 0.5;
  }
`;

export const IntegrationDescription = styled.p`
  font-size: 11px;
  color: ${(props) => props.theme.colors.text.secondary};
  margin: 0;
  line-height: 1.4;
`;

export const TriggersGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
`;

interface TriggerCardProps {
  severity: 'critical' | 'high' | 'medium';
}

export const TriggerCard = styled.div<TriggerCardProps>`
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: ${({ severity }) => {
    if (severity === 'critical') return 'rgba(239, 68, 68, 0.05)';
    if (severity === 'high') return 'rgba(234, 179, 8, 0.05)';
    return 'rgba(59, 130, 246, 0.05)';
  }};
  border: 1px solid ${({ severity }) => {
    if (severity === 'critical') return 'rgba(239, 68, 68, 0.2)';
    if (severity === 'high') return 'rgba(234, 179, 8, 0.2)';
    return 'rgba(59, 130, 246, 0.2)';
  }};
  border-radius: 8px;
`;

interface TriggerLabelProps {
  severity: 'critical' | 'high' | 'medium';
}

export const TriggerLabel = styled.span<TriggerLabelProps>`
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: ${({ severity }) => {
    if (severity === 'critical') return '#ef4444';
    if (severity === 'high') return '#eab308';
    return '#3b82f6';
  }};
`;

export const TriggerDescription = styled.p`
  font-size: 11px;
  color: ${(props) => props.theme.colors.text.secondary};
  margin: 0;
  line-height: 1.4;
`;

export const SystemAlert = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(59, 130, 246, 0.05);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 8px;
  color: ${(props) => props.theme.colors.text.secondary};
  font-size: 12px;
  line-height: 1.5;

  svg {
    color: #3b82f6;
    flex-shrink: 0;
  }
`;

export const Footer = styled.footer`
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid ${(props) => props.theme.colors.border};
`;

export const FooterButtons = styled.div`
  display: flex;
  gap: 12px;
`;

export const RestoreButton = styled.button`
  background: transparent;
  color: ${(props) => props.theme.colors.text.secondary};
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 6px;
  padding: 10px 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: ${(props) => props.theme.colors.text.primary};
    color: ${(props) => props.theme.colors.text.primary};
  }
`;

export const SaveButton = styled.button`
  background: ${(props) => props.theme.colors.primary};
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 10px 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    opacity: 0.9;
  }
`;