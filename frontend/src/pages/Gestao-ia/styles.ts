import styled from 'styled-components';

// ── Styles ────────────────────────────────────────────────────────
export const Container = styled.div`
  display: flex;
  margin-left: 240px;
  padding-top: 60px;
  width: calc(100% - 240px);
  flex-direction: column;
  padding: 80px 32px 32px 32px;
`;

export const Title = styled.h1`
  font-family: 'Orbitron', monospace;
  font-size: 18px;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.text.primary};
  letter-spacing: 2px;
  margin-bottom: 24px;
`;

export const Grid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
`;

export const Card = styled.div`
  background: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 10px;
  padding: 24px;
`;

export const FullCard = styled(Card)`
  grid-column: 1 / 3;
`;

export const CardTitle = styled.div`
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  color: ${({ theme }) => theme.colors.primary};
  letter-spacing: 3px;
  margin-bottom: 16px;
`;

export const InfoRow = styled.div`
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border}55;
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
`;

export const InfoLabel = styled.span`
  color: ${({ theme }) => theme.colors.text.muted};
`;

export const InfoValue = styled.span`
  color: ${({ theme }) => theme.colors.text.primary};
  font-weight: 600;
`;

export const AccuracyBar = styled.div`
  width: 100%;
  height: 6px;
  background: ${({ theme }) => theme.colors.border};
  border-radius: 3px;
  margin: 12px 0;
  overflow: hidden;
`;

export const AccuracyFill = styled.div<{ $pct: number }>`
  height: 100%;
  width: ${({ $pct }) => $pct}%;
  background: linear-gradient(90deg, #00A3FF, #00C853);
  border-radius: 3px;
  transition: width 1s ease;
`;

export const FeatureList = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  max-height: 200px;
  overflow-y: auto;
`;

export const FeatureItem = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  color: ${({ theme }) => theme.colors.text.secondary};
  &::before {
    content: '';
    width: 4px; height: 4px;
    border-radius: 50%;
    background: ${({ theme }) => theme.colors.primary};
    flex-shrink: 0;
  }
`;

export const Select = styled.select`
  width: 100%;
  background: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 6px;
  padding: 8px 12px;
  color: ${({ theme }) => theme.colors.text.primary};
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  margin-bottom: 12px;
  outline: none;
`;

export const InputNum = styled.input`
  width: 100%;
  background: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 6px;
  padding: 8px 12px;
  color: ${({ theme }) => theme.colors.text.primary};
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  margin-bottom: 12px;
  outline: none;
`;

export const Label = styled.div`
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  color: ${({ theme }) => theme.colors.text.muted};
  letter-spacing: 1px;
  margin-bottom: 6px;
`;

export const Btn = styled.button<{ $variant?: string }>`
  padding: 10px 20px;
  border-radius: 6px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  transition: opacity 0.2s;
  background: ${({ theme, $variant }) =>
    $variant === 'success' ? theme.colors.success :
    $variant === 'outline' ? 'transparent' : theme.colors.primary};
  border: ${({ theme, $variant }) =>
    $variant === 'outline' ? `1px solid ${theme.colors.border}` : 'none'};
  color: ${({ theme, $variant }) => $variant === 'outline' ? theme.colors.text.secondary : '#fff'};
  display: flex;
  align-items: center;
  gap: 8px;
  &:disabled { opacity: 0.5; cursor: not-allowed; }
  &:hover:not(:disabled) { opacity: 0.85; }
`;

export const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: ${({ theme }) => theme.colors.border};
  border-radius: 4px;
  overflow: hidden;
  margin: 12px 0;
`;

export const ProgressFill = styled.div<{ $pct: number }>`
  height: 100%;
  width: ${({ $pct }) => $pct}%;
  background: linear-gradient(90deg, #00A3FF, #00C853);
  border-radius: 4px;
  transition: width 0.5s ease;
`;

export const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
`;

export const Th = styled.th`
  padding: 10px 12px;
  text-align: left;
  color: ${({ theme }) => theme.colors.primary};
  font-size: 9px;
  letter-spacing: 2px;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
`;

export const Td = styled.td`
  padding: 10px 12px;
  color: ${({ theme }) => theme.colors.text.secondary};
  border-bottom: 1px solid ${({ theme }) => theme.colors.border}55;
`;

export const Badge = styled.span<{ $color: string }>`
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 9px;
  font-weight: 700;
  background: ${({ $color }) => `${$color}18`};
  border: 1px solid ${({ $color }) => `${$color}44`};
  color: ${({ $color }) => $color};
`;

export const ErrorMsg = styled.div`
  padding: 10px 14px;
  background: ${({ theme }) => theme.colors.danger}12;
  border: 1px solid ${({ theme }) => theme.colors.danger}44;
  border-left: 3px solid ${({ theme }) => theme.colors.danger};
  border-radius: 4px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  color: ${({ theme }) => theme.colors.danger};
  margin-bottom: 16px;
`;