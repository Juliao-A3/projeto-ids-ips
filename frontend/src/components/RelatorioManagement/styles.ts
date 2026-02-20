import styled from 'styled-components';

export const Container = styled.div`
  flex: 1;
  padding: 24px;
  max-width: 1220px;
  width: 100%;
  overflow-y: auto;
  color: ${(props) => props.theme.colors.text.primary};
`;

export const Header = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

export const HeaderTitle = styled.h1`
  font-size: 18px;
  font-weight: 600;
  color: ${(props) => props.theme.colors.text.primary};
  margin: 0;
`;

export const GeneratePDFButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
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

export const Content = styled.main`
  display: grid;
  grid-template-columns: 1fr 0.5fr;
  gap: 24px;
`;

export const LeftColumn = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

export const RightColumn = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

export const Section = styled.section`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

export const SectionTitle = styled.h2`
  font-size: 12px;
  font-weight: 600;
  color: ${(props) => props.theme.colors.text.secondary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0;
  padding-bottom: 12px;
  border-bottom: 1px solid ${(props) => props.theme.colors.border};
`;

export const SectionContent = styled.div`
  background: ${(props) => props.theme.colors.surface};
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 8px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

export const FiltersGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
`;

export const ViewButtonsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 8px;
`;

export const DetailedButton = styled.button`
  background: ${(props) => props.theme.colors.primary};
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 10px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    opacity: 0.9;
  }
`;

export const SummaryButton = styled.button`
  background: transparent;
  color: ${(props) => props.theme.colors.text.secondary};
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 6px;
  padding: 10px;
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

export const IncidentsTable = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

export const TableHeader = styled.thead`
  border-bottom: 1px solid ${(props) => props.theme.colors.border};
`;

export const TableHeaderCell = styled.th`
  padding: 12px 16px;
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  color: ${(props) => props.theme.colors.text.secondary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

export const TableBody = styled.tbody``;

export const TableRow = styled.tr`
  border-bottom: 1px solid ${(props) => props.theme.colors.border};
  transition: background 0.2s;

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background: rgba(255, 255, 255, 0.02);
  }
`;

export const TableCell = styled.td`
  padding: 16px;
  font-size: 13px;
  color: ${(props) => props.theme.colors.text.primary};
`;

interface StatusBadgeProps {
  status: string;
}

export const StatusBadge = styled.span<StatusBadgeProps>`
  display: inline-flex;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  background: ${({ status }) => {
    if (status === 'BLOQUEADO') return 'rgba(239, 68, 68, 0.1)';
    if (status === 'ALERTA') return 'rgba(234, 179, 8, 0.1)';
    return 'rgba(59, 130, 246, 0.1)';
  }};
  color: ${({ status }) => {
    if (status === 'BLOQUEADO') return '#ef4444';
    if (status === 'ALERTA') return '#eab308';
    return '#3b82f6';
  }};
  border: 1px solid ${({ status }) => {
    if (status === 'BLOQUEADO') return 'rgba(239, 68, 68, 0.3)';
    if (status === 'ALERTA') return 'rgba(234, 179, 8, 0.3)';
    return 'rgba(59, 130, 246, 0.3)';
  }};
`;

export const MetricsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

export const MetricItem = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

export const MetricHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

export const MetricLabel = styled.span`
  font-size: 11px;
  font-weight: 600;
  color: ${(props) => props.theme.colors.text.secondary};
  text-transform: uppercase;
  letter-spacing: 0.3px;
`;

export const MetricValue = styled.span`
  font-size: 16px;
  font-weight: 700;
  color: ${(props) => props.theme.colors.text.primary};
`;

export const MetricBar = styled.div`
  width: 100%;
  height: 8px;
  background: #2a2a2a;
  border-radius: 4px;
  overflow: hidden;
`;

interface MetricBarFillProps {
  percentage: number;
  color: string;
}

export const MetricBarFill = styled.div<MetricBarFillProps>`
  height: 100%;
  width: ${({ percentage }) => percentage}%;
  background: ${({ color }) => color};
  border-radius: 4px;
  transition: width 0.3s ease;
`;