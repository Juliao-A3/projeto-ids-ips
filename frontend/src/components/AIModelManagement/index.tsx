import { useState } from 'react';
import { Cpu, RefreshCw, Trash2, Activity, Table } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer
} from 'recharts';
import {
  Container,
  Content,
  Section,
  SectionHeader,
  SectionTitle,
  SectionContent,
  SectionActions,
  ReloadButton,
  ClearCacheButton,
  StatusGrid,
  StatusCard,
  StatusLabel,
  StatusValue,
  StatusSubValue,
  MonitoringGrid,
  ChartContainer,
  ChartHeader,
  ChartLegend,
  ChartLegendItem,
  ChartLegendDot,
  ChartFooter,
  MetricsContainer,
  MetricItem,
  MetricHeader,
  MetricLabel,
  MetricValue,
  MetricBar,
  MetricBarFill,
  MetricInfo,
  MetricSubLabel,
  FeaturesCell,
  FeaturesHeaderCell,
  FeaturesHeaderRow,
  FeaturesRow,
  FeaturesTable,
  ImportanceBadge,
  Footer,
  FooterLeft,
  FooterButtons,
  FooterStatus,
  RestoreButton,
  SaveButton,
} from './styles';
import { ToggleSwitch } from '../ToggleSwitch';

// Dados mockados do gráfico - virão do backend
const anomalyData = [
  { time: '-15 min', score: 0.2, threshold: 0.7 },
  { time: '', score: 0.3, threshold: 0.7 },
  { time: '', score: 0.25, threshold: 0.7 },
  { time: '', score: 0.4, threshold: 0.7 },
  { time: '', score: 0.35, threshold: 0.7 },
  { time: '', score: 0.5, threshold: 0.7 },
  { time: '', score: 0.45, threshold: 0.7 },
  { time: '', score: 0.6, threshold: 0.7 },
  { time: '', score: 0.55, threshold: 0.7 },
  { time: '', score: 0.8, threshold: 0.7 },
  { time: '', score: 0.75, threshold: 0.7 },
  { time: '', score: 0.5, threshold: 0.7 },
  { time: '', score: 0.4, threshold: 0.7 },
  { time: '', score: 0.3, threshold: 0.7 },
  { time: 'Agora', score: 0.25, threshold: 0.7 },
];

const featuresData = [
    {
      id: 1,
      attribute: 'IP Origem / Destino',
      value: '192.168.1.42',
      importance: 'Alta',
      enabled: true
    },
    {
      id: 2,
      attribute: 'Porta (TCP/UDP)',
      value: '443',
      importance: 'Alta',
      enabled: true
    },
    {
      id: 3,
      attribute: 'Tamanho do Pacote (Payload)',
      value: '1,460 bytes',
      importance: 'Média',
      enabled: true
    }
  ];

export function AIModelManagement() {
  const [bridgeEnabled, setBridgeEnabled] = useState(true);  
  return (
    <Container>
      <Content>

        {/* STATUS OPERACIONAL */}
        <Section>
          <SectionHeader>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Cpu size={16} color="#0ea5e9" />
              <SectionTitle>STATUS OPERACIONAL</SectionTitle>
            </div>
            <SectionActions>
              <ReloadButton>
                <RefreshCw size={14} />
                RECARREGAR MODELO (.PKL)
              </ReloadButton>
              <ClearCacheButton>
                <Trash2 size={14} />
                LIMPAR CACHE
              </ClearCacheButton>
            </SectionActions>
          </SectionHeader>
          <SectionContent>
            <StatusGrid>
              <StatusCard>
                <StatusLabel>MODELO ATIVO</StatusLabel>
                <StatusValue>XGB_PROD_v2</StatusValue>
              </StatusCard>
              <StatusCard>
                <StatusLabel>TEMPO DE UPTIME</StatusLabel>
                <StatusValue>14d 02h 45m</StatusValue>
              </StatusCard>
              <StatusCard>
                <StatusLabel>LATÊNCIA MÉDIA</StatusLabel>
                <StatusValue highlight>
                  12.4 <StatusSubValue>ms</StatusSubValue>
                </StatusValue>
                <StatusSubValue>P95: 15ms</StatusSubValue>
              </StatusCard>
              <StatusCard>
                <StatusLabel>ACURÁCIA REAL-TIME</StatusLabel>
                <StatusValue highlight>98.4%</StatusValue>
              </StatusCard>
            </StatusGrid>
          </SectionContent>
        </Section>

        {/* MONITORAMENTO DA IA EM TEMPO REAL */}
        <Section>
          <SectionHeader>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Activity size={16} color="#0ea5e9" />
              <SectionTitle>MONITORAMENTO DA IA EM TEMPO REAL</SectionTitle>
            </div>
          </SectionHeader>
          <SectionContent>
            <MonitoringGrid>

              <ChartContainer>
                <ChartHeader>
                  <span>SCORE DE ANORMALIDADE (HISTÓRICO)</span>
                  <ChartLegend>
                    <ChartLegendItem>
                      <ChartLegendDot color="#0ea5e9" />
                      Score
                    </ChartLegendItem>
                    <ChartLegendItem>
                      <ChartLegendDot color="#ef4444" />
                      Threshold
                    </ChartLegendItem>
                  </ChartLegend>
                </ChartHeader>

                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={anomalyData} barSize={12}>
                    <XAxis 
                      dataKey="time" 
                      tick={{ fill: '#888', fontSize: 10 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis 
                      domain={[0, 1]}
                      tick={{ fill: '#888', fontSize: 10 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <Tooltip
                      contentStyle={{
                        background: '#1a1a1a',
                        border: '1px solid #333',
                        borderRadius: '6px',
                        color: '#fff',
                        fontSize: '12px'
                      }}
                    />
                    <ReferenceLine 
                      y={0.7} 
                      stroke="#ef4444" 
                      strokeDasharray="4 4"
                      strokeWidth={1.5}
                    />
                    <Bar 
                      dataKey="score" 
                      fill="#0ea5e9"
                      radius={[3, 3, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>

                <ChartFooter>
                  <span>-15 min</span>
                  <span>Agora</span>
                </ChartFooter>
              </ChartContainer>

              {/* Métricas de Inferência */}
              <MetricsContainer>
                <span style={{ 
                  fontSize: '11px', 
                  fontWeight: 600, 
                  color: '#888',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  marginBottom: '8px',
                  display: 'block'
                }}>
                  MÉTRICAS DE INFERÊNCIA
                </span>

                <MetricItem>
                  <MetricHeader>
                    <MetricLabel>LATÊNCIA (MS)</MetricLabel>
                    <MetricValue>12.4</MetricValue>
                  </MetricHeader>
                  <MetricBar>
                    <MetricBarFill percentage={62} color="#0ea5e9" />
                  </MetricBar>
                </MetricItem>

                <MetricItem>
                  <MetricHeader>
                    <MetricLabel>THROUGHPUT (REQ/S)</MetricLabel>
                    <MetricValue>1,248</MetricValue>
                  </MetricHeader>
                  <MetricBar>
                    <MetricBarFill percentage={85} color="#0ea5e9" />
                  </MetricBar>
                </MetricItem>

                <MetricItem>
                  <MetricHeader>
                    <MetricLabel>USO DE CPU (%)</MetricLabel>
                    <MetricValue>14.2%</MetricValue>
                  </MetricHeader>
                  <MetricInfo>
                    <MetricSubLabel>MEMÓRIA (MODEL)</MetricSubLabel>
                    <MetricSubLabel>842MB</MetricSubLabel>
                  </MetricInfo>
                </MetricItem>
              </MetricsContainer>

            </MonitoringGrid>
          </SectionContent>
        </Section>

        <Section>
            <SectionHeader>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Table size={16} color="#0ea5e9" />
                <SectionTitle>CAMPOS DE ANÁLISE (FEATURES)</SectionTitle>
                </div>
            </SectionHeader>
            <SectionContent>
                <FeaturesTable>
                <thead>
                    <FeaturesHeaderRow>
                    <FeaturesHeaderCell>ATRIBUTO DE REDE</FeaturesHeaderCell>
                    <FeaturesHeaderCell>VALOR ATUAL (LIVE)</FeaturesHeaderCell>
                    <FeaturesHeaderCell>IMPORTÂNCIA</FeaturesHeaderCell>
                    <FeaturesHeaderCell>STATUS</FeaturesHeaderCell>
                    </FeaturesHeaderRow>
                </thead>
                <tbody>
                    {featuresData.map((feature) => (
                    <FeaturesRow key={feature.id}>
                        <FeaturesCell>{feature.attribute}</FeaturesCell>
                        <FeaturesCell highlight>{feature.value}</FeaturesCell>
                        <FeaturesCell>
                        <ImportanceBadge importance={feature.importance}>
                            {feature.importance}
                        </ImportanceBadge>
                        </FeaturesCell>
                        <FeaturesCell>
                        <ToggleSwitch
                            checked={bridgeEnabled}
                            onChange={setBridgeEnabled}
                        />
                        </FeaturesCell>
                    </FeaturesRow>
                    ))}
                </tbody>
                </FeaturesTable>
            </SectionContent>
        </Section>  
        <Footer>
        <FooterLeft>
          <FooterStatus>
            <span style={{ color: '#888' }}>INTEGRIDADE DO MOTOR:</span>
            <span style={{ color: '#22c55e', fontWeight: 600 }}>OPERACIONAL NORMAL</span>
          </FooterStatus>
          <span style={{ color: '#666', fontSize: '12px' }}>
            SURICATA ENGINE: RUNNING • UPTIME: 142:07H:19M • IPS-INLINE MODE
          </span>
        </FooterLeft>
        <FooterButtons>
          <RestoreButton>RESTAURAR PADRÕES</RestoreButton>
          <SaveButton>SALVAR ALTERAÇÕES</SaveButton>
        </FooterButtons>
      </Footer>      
      </Content>
    </Container>
  );
}