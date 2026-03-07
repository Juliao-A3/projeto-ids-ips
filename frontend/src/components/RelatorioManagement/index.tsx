import { useState } from 'react';
import { Download } from 'lucide-react';
import { Dropdown } from '../Dropdown';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { useReports } from '../../../hooks/useReports';
import {
  Container, Header, HeaderTitle, GeneratePDFButton, Content,
  LeftColumn, RightColumn, Section, SectionTitle, SectionContent,
  FiltersGrid, ViewButtonsGrid, DetailedButton, SummaryButton,
  IncidentsTable, TableHeader, TableHeaderCell, TableBody,
  TableRow, TableCell, StatusBadge, MetricsContainer, MetricItem,
  MetricHeader, MetricLabel, MetricValue, MetricBar, MetricBarFill,
} from './styles';
import { api } from '../../services/api';

export function ReportsManagement() {
  const [period, setPeriod]     = useState('24h');
  const [severity, setSeverity] = useState('all');

  const { summary, incidents, volume, loading, error } = useReports(period, severity);

  const handleDownloadPDF = async () => {
  try {
      const response = await api.get(
        `/reports/export/pdf?period=${period}&severity=${severity}`,
        { responseType: 'blob' }
      );
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const link = document.createElement('a');
      link.href  = URL.createObjectURL(blob);
      link.download = `aegis-report-${period}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(link.href);
    } catch {
      console.error("Erro ao gerar PDF");
    }
  };

  const periodOptions = [
    { value: '24h', label: 'Últimas 24 Horas' },
    { value: '7d',  label: 'Últimos 7 Dias'   },
    { value: '30d', label: 'Últimos 30 Dias'  },
  ];

  const severityOptions = [
    { value: 'all',    label: 'Todas as Severidades' },
    { value: 'critica', label: 'Crítica'             },
    { value: 'alta',    label: 'Alta'                },
    { value: 'media',   label: 'Média'               },
    { value: 'baixa',   label: 'Baixa'               },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'mitigado': return 'BLOQUEADO';
      case 'pendente': return 'ALERTA';
      case 'ignorado': return 'AVISO';
      default: return status.toUpperCase();
    }
  };

  if (loading) return (
    <Container>
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "center",
        height: "200px", color: "#64748B",
        fontFamily: "'Share Tech Mono', monospace", fontSize: "12px"
      }}>
        A CARREGAR RELATÓRIO...
      </div>
    </Container>
  );

  return (
    <Container>
      <Header>
        <HeaderTitle>Relatórios Técnicos</HeaderTitle>
        <GeneratePDFButton type='button' onClick={handleDownloadPDF}>
          <Download size={16} />
          GERAR RELATÓRIO PDF
        </GeneratePDFButton>
      </Header>

      {error && (
        <div style={{
          padding: "10px 14px", margin: "0 0 12px 0",
          background: "#ef444412", border: "1px solid #ef444444",
          borderLeft: "3px solid #ef4444", borderRadius: "4px",
          fontFamily: "'Share Tech Mono', monospace", fontSize: "11px", color: "#ef4444"
        }}>
          ⚠ {error}
        </div>
      )}

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

          {/* INCIDENTES */}
          <Section>
            <SectionTitle>
              PREVIEW DE INCIDENTES RECENTES
              <span style={{ fontSize: '10px', color: '#666', marginLeft: '8px', fontWeight: 400 }}>
                {incidents.length} INCIDENTES
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
                  {incidents.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={4} style={{ textAlign: 'center', color: '#64748B' }}>
                        Sem incidentes no período selecionado
                      </TableCell>
                    </TableRow>
                  ) : (
                    incidents.map((incident) => (
                      <TableRow key={incident.id}>
                        <TableCell>{incident.timestamp?.slice(0, 19).replace('T', ' ')}</TableCell>
                        <TableCell>{incident.evento}</TableCell>
                        <TableCell>{incident.origem}</TableCell>
                        <TableCell>
                          <StatusBadge status={getStatusColor(incident.status)}>
                            {getStatusColor(incident.status)}
                          </StatusBadge>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </IncidentsTable>
            </SectionContent>
          </Section>
        </LeftColumn>

        <RightColumn>
          {/* GRÁFICO */}
          <Section>
            <SectionTitle>VOLUME DE ATAQUES</SectionTitle>
            <SectionContent>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={volume} barSize={20}>
                  <XAxis
                    dataKey="time"
                    tick={{ fill: '#888', fontSize: 10 }}
                    axisLine={false} tickLine={false}
                  />
                  <YAxis
                    tick={{ fill: '#888', fontSize: 10 }}
                    axisLine={false} tickLine={false}
                  />
                  <Tooltip contentStyle={{
                    background: '#1a1a1a', border: '1px solid #333',
                    borderRadius: '6px', color: '#fff', fontSize: '12px'
                  }} />
                  <Bar dataKey="attacks" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </SectionContent>
          </Section>

          {/* MÉTRICAS */}
          <Section>
            <SectionTitle>MÉTRICAS DO RELATÓRIO</SectionTitle>
            <SectionContent>
              <MetricsContainer>
                <MetricItem>
                  <MetricHeader>
                    <MetricLabel>Total de Eventos</MetricLabel>
                    <MetricValue>{summary?.total_eventos ?? 0}</MetricValue>
                  </MetricHeader>
                  <MetricBar>
                    <MetricBarFill percentage={100} color="#0ea5e9" />
                  </MetricBar>
                </MetricItem>

                <MetricItem>
                  <MetricHeader>
                    <MetricLabel>Severidade Crítica</MetricLabel>
                    <MetricValue>{summary?.criticos ?? 0}</MetricValue>
                  </MetricHeader>
                  <MetricBar>
                    <MetricBarFill
                      percentage={summary?.total_eventos ? Math.round((summary.criticos / summary.total_eventos) * 100) : 0}
                      color="#ef4444"
                    />
                  </MetricBar>
                </MetricItem>

                <MetricItem>
                  <MetricHeader>
                    <MetricLabel>IPs Bloqueados</MetricLabel>
                    <MetricValue>{summary?.total_ips_bloqueados ?? 0}</MetricValue>
                  </MetricHeader>
                  <MetricBar>
                    <MetricBarFill
                      percentage={summary?.total_eventos ? Math.min(Math.round((summary.total_ips_bloqueados / summary.total_eventos) * 100), 100) : 0}
                      color="#00C853"
                    />
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