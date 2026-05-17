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
  height: 100%;
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
  position: relative;
  z-index: 1;
  flex: 1;
  display: flex;
  flex-direction: column;
`;

export const WhitelistEditor = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

export const WhitelistInputRow = styled.div`
  display: flex;
  gap: 10px;
  align-items: flex-start;
`;

export const WhitelistInput = styled.input`
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 6px;
  padding: 12px 16px;
  font-size: 13px;
  font-family: 'Consolas', 'Monaco', monospace;
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

export const WhitelistAddButton = styled.button`
  background: ${(props) => props.theme.colors.primary};
  color: ${(props) => props.theme.colors.text.primary};
  border: none;
  border-radius: 6px;
  padding: 12px 18px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  cursor: pointer;
  transition: opacity 0.2s;
  white-space: nowrap;

  &:hover:not(:disabled) {
    opacity: 0.9;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

export const WhitelistList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

export const WhitelistChip = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid ${(props) => props.theme.colors.border};
  background: rgba(255, 255, 255, 0.03);
  font-size: 12px;
  font-family: 'Consolas', 'Monaco', monospace;
  color: ${(props) => props.theme.colors.text.primary};
`;

export const WhitelistChipButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: none;
  border-radius: 50%;
  background: ${(props) => props.theme.colors.danger}22;
  color: ${(props) => props.theme.colors.danger};
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  padding: 0;

  &:hover {
    background: ${(props) => props.theme.colors.danger}33;
  }
`;

export const WhitelistHint = styled.p`
  font-size: 11px;
  color: ${(props) => props.theme.colors.text.secondary};
  margin: 0;
  line-height: 1.4;
`;

export const Label = styled.div`
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  color: ${(props) => props.theme.colors.text.muted};
  letter-spacing: 1px;
  margin-bottom: 6px;
`;

export const WhitelistError = styled.p`
  font-size: 11px;
  color: ${(props) => props.theme.colors.danger};
  margin: 0;
  line-height: 1.4;
`;

export const BridgeConfig = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: 100%;
`;

export const BridgeSettings = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
`;

export const BridgeDescription = styled.p`
  font-size: 13px;
  color: ${(props) => props.theme.colors.text.secondary};
  margin: 0;
  line-height: 1.5;
`;

export const BridgeToggles = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

export const DropdownsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
`;

export const TwoColumnsWrapper = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: stretch;
`;

export const PerformanceGrid = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 16px;
  flex: 1;
  justify-content: center;
`;

export const PerformanceItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 6px;
`;

export const PerformanceLabel = styled.span`
  font-size: 12px;
  font-weight: 600;
  color: ${(props) => props.theme.colors.text.secondary};
  text-transform: uppercase;
  letter-spacing: 0.3px;
`;

export const PerformanceValue = styled.span`
  font-size: 13px;
  font-weight: 600;
  color: ${(props) => props.theme.colors.primary};
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
  color: ${(props) => props.theme.colors.text.primary};
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