import styled from 'styled-components';

export const Container = styled.div`
  border-radius: 8px;
  width: 100%;
`;

export const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
`;

export const Title = styled.h3`
  color: ${(props) => props.theme.colors.text.secondary};
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0;
`;

interface StatusBadgeProps {
  percentage: number;
}

export const StatusBadge = styled.div<StatusBadgeProps>`
  display: flex;
  align-items: center;
  gap: 6px;
  background: ${({ percentage }) => 
    percentage >= 80 ? 'rgba(34, 197, 94, 0.1)' : 
    percentage >= 50 ? 'rgba(234, 179, 8, 0.1)' : 
    'rgba(239, 68, 68, 0.1)'
  };
  border: 1px solid ${({ percentage }) => 
    percentage >= 80 ? 'rgba(34, 197, 94, 0.3)' : 
    percentage >= 50 ? 'rgba(234, 179, 8, 0.3)' : 
    'rgba(239, 68, 68, 0.3)'
  };
  border-radius: 12px;
  padding: 4px 12px;
`;

interface StatusIconProps {
  percentage: number;
}

export const StatusIcon = styled.div<StatusIconProps>`
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${({ percentage }) => 
    percentage >= 80 ? '#22c55e' : 
    percentage >= 50 ? '#eab308' : 
    '#ef4444'
  };
`;

interface StatusTextProps {
  percentage: number;
}

export const StatusText = styled.span<StatusTextProps>`
  color: ${({ percentage }) => 
    percentage >= 80 ? '#22c55e' : 
    percentage >= 50 ? '#eab308' : 
    '#ef4444'
  };
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

export const ProgressSection = styled.div`
  margin-top: 12px;
`;

export const ProgressHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
`;

export const ProgressLabel = styled.span`
  color: ${(props) => props.theme.colors.text.secondary};
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
`;

interface ProgressValueProps {
  percentage: number;
}

export const ProgressValue = styled.span<ProgressValueProps>`
  color: ${({ percentage }) => 
    percentage >= 80 ? '#22c55e' : 
    percentage >= 50 ? '#eab308' : 
    '#ef4444'
  };
  font-size: 12px;
  font-weight: 600;
`;

export const ProgressBarContainer = styled.div`
  width: 100%;
  height: 8px;
  background: ${(props) => props.theme.colors.background};
  border-radius: 4px;
  overflow: hidden;
`;

interface ProgressBarFillProps {
  percentage: number;
}

export const ProgressBarFill = styled.div<ProgressBarFillProps>`
  height: 100%;
  background: ${({ percentage }) => 
    percentage >= 80 ? 'linear-gradient(90deg, #22c55e 0%, #16a34a 100%)' : 
    percentage >= 50 ? 'linear-gradient(90deg, #eab308 0%, #ca8a04 100%)' : 
    'linear-gradient(90deg, #ef4444 0%, #dc2626 100%)'
  };
  border-radius: 4px;
  width: ${({ percentage }) => percentage}%;
  transition: width 0.3s ease, background 0.3s ease;
`;