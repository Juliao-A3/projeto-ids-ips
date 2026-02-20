import { useState } from 'react';
import { Download } from 'lucide-react';
import { Dropdown } from '../Dropdown';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import {
  Container,
  Header,
  HeaderTitle,
  GeneratePDFButton,
  Content,
  LeftColumn,
  RightColumn,
  Section,
  SectionTitle,
  SectionContent,
  FiltersGrid,
  ViewButtonsGrid,
  DetailedButton,
  SummaryButton,
  IncidentsTable,
  TableHeader,
  TableHeaderCell,
  TableBody,
  TableRow,
  TableCell,
  StatusBadge,
  MetricsContainer,
  MetricItem,
  MetricHeader,
  MetricLabel,
  MetricValue,
  MetricBar,
  MetricBarFill,
} from './styles';

// Dados do gráfico - virão do backend e muito salo aqui Ngola
const attackVolumeData = [
  { time: '00:00', attacks: 35 },
  { time: '03:00', attacks: 45 },
  { time: '06:00', attacks: 30 },
  { time: '09:00', attacks: 55 },
  { time: '12:00', attacks: 48 },
  { time: '15:00', attacks: 60 },
  { time: '18:00', attacks: 52 },
  { time: '21:00', attacks: 38 },
  { time: 'Agora', attacks: 42 },
];

// Dados de incidentes o teu trabalho Ngola
const incidentsData = [
  {
    id: 1,
    timestamp: '2023-10-27 14:03:01',
    event: 'SQL Injection Detected',
    origin: '192.168.1.150',
    status: 'BLOQUEADO'
  },
  {
    id: 2,
    timestamp: '2023-10-27 14:14:46',
    event: 'Multiple Failed Logins',
    origin: '40.23.123.0',
    status: 'ALERTA'
  },
  {
    id: 3,
    timestamp: '2023-10-27 14:50:12',
    event: 'Abnormal SSL Traffic',
    origin: '10.0.0.50',
    status: 'AVISO'
  }
];

export function ReportsManagement() {
  const [period, setPeriod] = useState('24h');
  const [attackType, setAttackType] = useState('all');
  const [severity, setSeverity] = useState('all');

  const periodOptions = [
    { value: '24h', label: 'Últimas 24 Horas' },
    { value: '7d', label: 'Últimos 7 Dias' },
    { value: '30d', label: 'Últimos 30 Dias' },
    { value: 'custom', label: 'Personalizado' }
  ];

  const attackTypeOptions = [
    { value: 'all', label: 'Todos os Tipos' },
    { value: 'sql-injection', label: 'SQL Injection' },
    { value: 'ddos', label: 'DDoS' },
    { value: 'malware', label: 'Malware' },
    { value: 'brute-force', label: 'Brute Force' }
  ];

  const severityOptions = [
    { value: 'all', label: 'Todas as Severidades' },
    { value: 'critical', label: 'Crítica' },
    { value: 'high', label: 'Alta' },
    { value: 'medium', label: 'Média' },
    { value: 'low', label: 'Baixa' }
  ];

  return (
    <Container>
      <Header>
        <HeaderTitle>Relatórios Técnicos</HeaderTitle>
        <GeneratePDFButton>
          <Download size={16} />
          GERAR RELATÓRIO PDF
        </GeneratePDFButton>
      </Header>

      <Content>
        <LeftColumn>
          <Section>
            <SectionTitle>FILTROS DE PARÂMETROS</SectionTitle>
            <SectionContent>
              <FiltersGrid>
                <Dropdown
                  label="PERÍODO"
                  value={period}
                  onChange={setPeriod}
                  options={periodOptions}
                />
                <Dropdown
                  label="TIPO DE ATAQUE"
                  value={attackType}
                  onChange={setAttackType}
                  options={attackTypeOptions}
                />
                <Dropdown
                  label="SEVERIDADE"
                  value={severity}
                  onChange={setSeverity}
                  options={severityOptions}
                />
              </FiltersGrid>
              <ViewButtonsGrid>
                <DetailedButton>DETALHADO</DetailedButton>
                <SummaryButton>RESUMIDO</SummaryButton>
              </ViewButtonsGrid>
            </SectionContent>
          </Section>

          {/* PREVIEW DE INCIDENTES RECENTES */}
          <Section>
            <SectionTitle>
              PREVIEW DE INCIDENTES RECENTES
              <span style={{ 
                fontSize: '10px', 
                color: '#666', 
                marginLeft: '8px',
                fontWeight: 400 
              }}>
                RECEBIDOS: 3 DE 126 INCIDENTES
              </span>
            </SectionTitle>
            <SectionContent>
              <IncidentsTable>
                <TableHeader>
                  <tr>
                    <TableHeaderCell>TIMESTAMP</TableHeaderCell>
                    <TableHeaderCell>EVENTO</TableHeaderCell>
                    <TableHeaderCell>ORIGEM</TableHeaderCell>
                    <TableHeaderCell>STATUS</TableHeaderCell>
                  </tr>
                </TableHeader>
                <TableBody>
                  {incidentsData.map((incident) => (
                    <TableRow key={incident.id}>
                      <TableCell>{incident.timestamp}</TableCell>
                      <TableCell>{incident.event}</TableCell>
                      <TableCell>{incident.origin}</TableCell>
                      <TableCell>
                        <StatusBadge status={incident.status}>
                          {incident.status}
                        </StatusBadge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </IncidentsTable>
            </SectionContent>
          </Section>
        </LeftColumn>

        <RightColumn>
          {/* VOLUME DE ATAQUES (24H) */}
          <Section>
            <SectionTitle>
              VOLUME DE ATAQUES (24H)
            </SectionTitle>
            <SectionContent>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={attackVolumeData} barSize={20}>
                  <XAxis 
                    dataKey="time" 
                    tick={{ fill: '#888', fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis 
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
                  <Bar 
                    dataKey="attacks" 
                    fill="#666"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </SectionContent>
          </Section>

          {/* MÉTRICAS DO RELATÓRIO */}
          <Section>
            <SectionTitle>MÉTRICAS DO RELATÓRIO</SectionTitle>
            <SectionContent>
              <MetricsContainer>
                <MetricItem>
                  <MetricHeader>
                    <MetricLabel>Total de Eventos</MetricLabel>
                    <MetricValue>12,842</MetricValue>
                  </MetricHeader>
                  <MetricBar>
                    <MetricBarFill percentage={85} color="#0ea5e9" />
                  </MetricBar>
                </MetricItem>

                <MetricItem>
                  <MetricHeader>
                    <MetricLabel>Falsos Positivos (%)</MetricLabel>
                    <MetricValue>2,340</MetricValue>
                  </MetricHeader>
                  <MetricBar>
                    <MetricBarFill percentage={18} color="#22c55e" />
                  </MetricBar>
                </MetricItem>

                <MetricItem>
                  <MetricHeader>
                    <MetricLabel>Severidade Crítica</MetricLabel>
                    <MetricValue>42</MetricValue>
                  </MetricHeader>
                  <MetricBar>
                    <MetricBarFill percentage={8} color="#ef4444" />
                  </MetricBar>
                </MetricItem>
              </MetricsContainer>
            </SectionContent>
          </Section>
        </RightColumn>
      </Content>
    </Container>
  );
}