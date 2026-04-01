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

// ── Limites por tipo de relatório
const LIMITS = {
  detalhado: 500,
  resumido:  100,
};

export function ReportsManagement() {
  const [period, setPeriod]         = useState('24h');
  const [severity, setSeverity]     = useState('all');
  const [reportType, setReportType] = useState<'detalhado' | 'resumido'>('detalhado');
  const [pdfLoading, setPdfLoading] = useState(false);
  const [pdfError, setPdfError]     = useState('');

  const { summary, incidents, volume, loading, error } = useReports(period, severity);

  // ── total real de alertas vs limite aplicado
  const totalReal  = summary?.total_eventos ?? 0;
  const limiteAtual = LIMITS[reportType];
  const truncado   = totalReal > limiteAtual;

  const handleDownloadPDF = async () => {
    setPdfLoading(true);
    setPdfError('');
    try {
      const response = await api.get(
        `/reports/export/pdf?period=${period}&severity=${severity}&tipo=${reportType}&limite=${limiteAtual}`,
        { responseType: 'blob' }
      );

      const blob = new Blob([response.data], { type: 'application/pdf' });
      const link = document.createElement('a');
      link.href  = URL.createObjectURL(blob);
      link.download = `aegis-report-${reportType}-${period}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(link.href);
    } catch {
      setPdfError('Erro ao gerar PDF. Tenta novamente.');
    } finally {
      setPdfLoading(false);
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
        <GeneratePDFButton type='button' onClick={handleDownloadPDF} disabled={pdfLoading}>
          <Download size={16} />
          {pdfLoading ? 'A GERAR...' : `GERAR PDF ${reportType.toUpperCase()}`}
        </GeneratePDFButton>
      </Header>

      {/* erros */}
      {(error || pdfError) && (
        <div style={{
          padding: "10px 14px", margin: "0 0 12px 0",
          background: "#ef444412", border: "1px solid #ef444444",
          borderLeft: "3px solid #ef4444", borderRadius: "4px",
          fontFamily: "'Share Tech Mono', monospace", fontSize: "11px", color: "#ef4444"
        }}>
          ⚠ {error || pdfError}
        </div>
      )}

      {/* aviso de truncagem */}
      {truncado && (
        <div style={{
          padding: "10px 14px", margin: "0 0 12px 0",
          background: "#FFAB0012", border: "1px solid #FFAB0044",
          borderLeft: "3px solid #FFAB00", borderRadius: "4px",
          fontFamily: "'Share Tech Mono', monospace", fontSize: "11px", color: "#FFAB00"
        }}>
          ⚑ A mostrar os {limiteAtual} alertas mais recentes de {totalReal} no total.
          {reportType === 'resumido'
            ? ' Muda para DETALHADO para ver até 500.'
            : ' Exporta como CSV para ver todos.'
          }
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

              {/* ── Botões tipo relatório ── */}
              <div>
                <div style={{
                  fontFamily: "'Share Tech Mono', monospace",
                  fontSize: 10, color: '#64748B',
                  letterSpacing: 1, marginBottom: 8,
                }}>
                  TIPO DE RELATÓRIO
                </div>
                <ViewButtonsGrid>
                  <DetailedButton
                    $active={reportType === 'detalhado'}
                    onClick={() => setReportType('detalhado')}
                  >
                    DETALHADO
                    <span style={{
                      display: 'block', fontSize: 9, opacity: 0.7,
                      fontFamily: "'Share Tech Mono', monospace",
                      fontWeight: 400, letterSpacing: 0,
                    }}>
                      até {LIMITS.detalhado} alertas
                    </span>
                  </DetailedButton>

                  <SummaryButton
                    $active={reportType === 'resumido'}
                    onClick={() => setReportType('resumido')}
                  >
                    RESUMIDO
                    <span style={{
                      display: 'block', fontSize: 9, opacity: 0.7,
                      fontFamily: "'Share Tech Mono', monospace",
                      fontWeight: 400, letterSpacing: 0,
                    }}>
                      até {LIMITS.resumido} alertas
                    </span>
                  </SummaryButton>
                </ViewButtonsGrid>
              </div>
            </SectionContent>
          </Section>

          {/* INCIDENTES */}
          <Section>
            <SectionTitle>
              PREVIEW DE INCIDENTES RECENTES
              <span style={{ fontSize: '10px', color: '#666', marginLeft: '8px', fontWeight: 400 }}>
                {incidents.length} INCIDENTES
                {truncado && ` (de ${totalReal})`}
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
              {/* badge tipo ativo */}
              <div style={{ display: 'flex', gap: 8, marginBottom: 4 }}>
                <span style={{
                  padding: '2px 10px', borderRadius: 4,
                  fontFamily: "'Share Tech Mono', monospace", fontSize: 9,
                  background: reportType === 'detalhado' ? 'rgba(0,163,255,0.15)' : 'rgba(0,200,83,0.15)',
                  border: `1px solid ${reportType === 'detalhado' ? 'rgba(0,163,255,0.4)' : 'rgba(0,200,83,0.4)'}`,
                  color: reportType === 'detalhado' ? '#00A3FF' : '#00C853',
                }}>
                  {reportType.toUpperCase()} — LIMITE {limiteAtual}
                </span>
                {truncado && (
                  <span style={{
                    padding: '2px 10px', borderRadius: 4,
                    fontFamily: "'Share Tech Mono', monospace", fontSize: 9,
                    background: 'rgba(255,171,0,0.12)',
                    border: '1px solid rgba(255,171,0,0.4)',
                    color: '#FFAB00',
                  }}>
                    TRUNCADO
                  </span>
                )}
              </div>

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