import styled from 'styled-components';

export const Card = styled.div`
  background: ${(props) => props.theme.colors.surface};
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 8px;
  padding: 20px;
  transition: all 0.2s;

  &:hover {
    border-color: ${(props) => props.theme.colors.primary};
    background: rgba(255, 255, 255, 0.03);
  }
`;

export const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
`;

export const CardTitle = styled.h3`
  font-size: 15px;
  font-weight: 600;
  color: ${(props) => props.theme.colors.text.primary};
  margin: 0 0 4px 0;
`;

export const CardSubtitle = styled.p`
  font-size: 12px;
  color: ${(props) => props.theme.colors.text.secondary};
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.3px;
`;

interface CardStatusProps {
  enabled: boolean;
}

export const CardStatus = styled.span<CardStatusProps>`
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  background: ${({ enabled }) => 
    enabled ? 'rgba(34, 197, 94, 0.1)' : 'rgba(100, 100, 100, 0.1)'
  };
  color: ${({ enabled }) => 
    enabled ? '#22c55e' : '#888'
  };
  border: 1px solid ${({ enabled }) => 
    enabled ? 'rgba(34, 197, 94, 0.3)' : 'rgba(100, 100, 100, 0.3)'
  };
`;