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
  justify-content: space-between;
  padding-bottom: 12px;
  border-bottom: 1px solid ${(props) => props.theme.colors.border};
`;

export const SectionTitle = styled.h2`
  font-size: 12px;
  font-weight: 600;
  color: ${(props) => props.theme.colors.text.secondary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0;
`;

export const SectionActions = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

export const SectionContent = styled.div`
  background: ${(props) => props.theme.colors.surface};
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 8px;
  padding: 24px;
  position: relative;
  z-index: 1;
`;

export const ReloadButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  color: ${(props) => props.theme.colors.primary};
  border: 1px solid ${(props) => props.theme.colors.primary};
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: ${(props) => props.theme.colors.primary};
    color: ${(props) => props.theme.colors.text.primary};
  }
`;

export const ClearCacheButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  color: #ef4444;
  border: 1px solid #ef4444;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(239, 68, 68, 0.1);
  }
`;

export const StatusGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
`;

export const StatusCard = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 8px;
`;

export const StatusLabel = styled.span`
  font-size: 11px;
  font-weight: 600;
  color: ${(props) => props.theme.colors.text.secondary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

interface StatusValueProps {
  highlight?: boolean;
}

export const StatusValue = styled.span<StatusValueProps>`
  font-size: 22px;
  font-weight: 700;
  color: ${({ highlight, theme }) =>
    highlight ? theme.colors.primary : theme.colors.text.primary
  };
`;

export const StatusSubValue = styled.span`
  font-size: 12px;
  font-weight: 400;
  color: ${(props) => props.theme.colors.text.secondary};
`;

export const MonitoringGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 0.6fr;
  gap: 24px;
`;

export const ChartContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

export const ChartHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;

  span {
    font-size: 11px;
    font-weight: 600;
    color: ${(props) => props.theme.colors.text.secondary};
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
`;

export const ChartLegend = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

export const ChartLegendItem = styled.span`
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: ${(props) => props.theme.colors.text.secondary};
`;

interface ChartLegendDotProps {
  color: string;
}

export const ChartLegendDot = styled.span<ChartLegendDotProps>`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${({ color }) => color};
`;

export const ChartFooter = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: ${(props) => props.theme.colors.text.secondary};
  padding: 0 4px;
`;

export const MetricsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
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
  font-size: 18px;
  font-weight: 700;
  color: ${(props) => props.theme.colors.text.primary};
`;

export const MetricBar = styled.div`
  width: 100%;
  height: 6px;
  background: #2a2a2a;
  border-radius: 3px;
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
  border-radius: 3px;
  transition: width 0.3s ease;
`;

export const MetricInfo = styled.div`
  display: flex;
  justify-content: space-between;
`;

export const MetricSubLabel = styled.span`
  font-size: 11px;
  color: ${(props) => props.theme.colors.text.secondary};
`;

export const FeaturesTable = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

export const FeaturesHeaderRow = styled.tr`
  border-bottom: 1px solid ${(props) => props.theme.colors.border};
`;

export const FeaturesHeaderCell = styled.th`
  padding: 12px 16px;
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  color: ${(props) => props.theme.colors.text.secondary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

export const FeaturesRow = styled.tr`
  border-bottom: 1px solid ${(props) => props.theme.colors.border};
  transition: background 0.2s;

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background: rgba(255, 255, 255, 0.02);
  }
`;

interface FeaturesCellProps {
  highlight?: boolean;
}

export const FeaturesCell = styled.td<FeaturesCellProps>`
  padding: 16px;
  font-size: 14px;
  color: ${({ highlight, theme }) =>
    highlight ? theme.colors.primary : theme.colors.text.primary
  };
`;

interface ImportanceBadgeProps {
  importance: string;
}

export const ImportanceBadge = styled.span<ImportanceBadgeProps>`
  display: inline-flex;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  background: ${({ importance }) =>
    importance === 'Alta' ? 'rgba(34, 197, 94, 0.1)' :
    importance === 'Média' ? 'rgba(234, 179, 8, 0.1)' :
    'rgba(100, 100, 100, 0.1)'
  };
  color: ${({ importance }) =>
    importance === 'Alta' ? '#22c55e' :
    importance === 'Média' ? '#eab308' :
    '#888'
  };
  border: 1px solid ${({ importance }) =>
    importance === 'Alta' ? 'rgba(34, 197, 94, 0.3)' :
    importance === 'Média' ? 'rgba(234, 179, 8, 0.3)' :
    'rgba(100, 100, 100, 0.3)'
  };
`;

export const Footer = styled.footer`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid ${(props) => props.theme.colors.border};
`;

export const FooterLeft = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

export const FooterStatus = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
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