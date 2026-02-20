import styled from 'styled-components';

export const TableContainer = styled.div`
  width: 100%;
  overflow-x: auto;
`;

export const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

export const TableHeader = styled.thead`
  background: rgba(255, 255, 255, 0.02);
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
  color: ${(props) => props.theme.colors.text.primary};
  font-size: 14px;
`;

export const ToggleCell = styled(TableCell)`
  padding: 12px 16px;
`;

interface StatusBadgeProps {
  status: string;
}

export const StatusBadge = styled.span<StatusBadgeProps>`
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  background: ${({ status }) => {
    if (status === 'CONECTADO') return 'rgba(34, 197, 94, 0.1)';
    if (status === 'STANDBY') return 'rgba(234, 179, 8, 0.1)';
    return 'rgba(100, 100, 100, 0.1)';
  }};
  color: ${({ status }) => {
    if (status === 'CONECTADO') return '#22c55e';
    if (status === 'STANDBY') return '#eab308';
    return '#888';
  }};
  border: 1px solid ${({ status }) => {
    if (status === 'CONECTADO') return 'rgba(34, 197, 94, 0.3)';
    if (status === 'STANDBY') return 'rgba(234, 179, 8, 0.3)';
    return 'rgba(100, 100, 100, 0.3)';
  }};
`;