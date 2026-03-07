import { useState } from 'react';
import { Cpu, Trash2, Activity } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ReferenceLine, ResponsiveContainer
} from 'recharts';
import {
  Container, Content, Section, SectionHeader, SectionTitle, SectionContent,
  SectionActions, ClearCacheButton, StatusGrid, StatusCard, StatusLabel,
  StatusValue, StatusSubValue, MonitoringGrid, ChartContainer, ChartHeader,
  ChartLegend, ChartLegendItem, ChartLegendDot, ChartFooter, MetricsContainer,
  MetricItem, MetricHeader, MetricLabel, MetricValue, MetricBar, MetricBarFill,
  MetricInfo, MetricSubLabel,
} from './styles';
import { useAIMetrics } from '../../../hooks/useAIMetrics';

export function AIModelManagement() {
  const { data, connected, error } = useAIMetrics();

  if (!data) return (
    <Container>
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "center",
        height: "200px", color: "#64748B",
        fontFamily: "'Share Tech Mono', monospace",
        fontSize: "12px", letterSpacing: "0.1em"
      }}>
        {error ? `⚠ ${error}` : "A LIGAR AO SERVIDOR..."}
      </div>
    </Container>
  );

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
              {/* indicador LIVE */}
              <div style={{
                display: "flex", alignItems: "center", gap: "6px",
                fontSize: "10px", fontFamily: "'Share Tech Mono', monospace",
                color: connected ? "#00C853" : "#ef4444", marginRight: "12px"
              }}>
                <span style={{
                  width: 6, height: 6, borderRadius: "50%",
                  background: connected ? "#00C853" : "#ef4444",
                  display: "inline-block"
                }} />
                {connected ? "LIVE" : "DESLIGADO"}
              </div>
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
                <StatusValue>{data.status.modelo_ativo}</StatusValue>
              </StatusCard>
              <StatusCard>
                <StatusLabel>TEMPO DE UPTIME</StatusLabel>
                <StatusValue>{data.status.uptime}</StatusValue>
              </StatusCard>
              <StatusCard>
                <StatusLabel>LATÊNCIA MÉDIA</StatusLabel>
                <StatusValue highlight>
                  {data.status.latencia_ms} <StatusSubValue>ms</StatusSubValue>
                </StatusValue>
              </StatusCard>
              <StatusCard>
                <StatusLabel>ACURÁCIA REAL-TIME</StatusLabel>
                <StatusValue highlight>{data.status.acuracia}%</StatusValue>
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

              {/* Gráfico */}
              <ChartContainer>
                <ChartHeader>
                  <span>SCORE DE ANORMALIDADE (HISTÓRICO)</span>
                  <ChartLegend>
                    <ChartLegendItem>
                      <ChartLegendDot color="#0ea5e9" />Score
                    </ChartLegendItem>
                    <ChartLegendItem>
                      <ChartLegendDot color="#ef4444" />Threshold
                    </ChartLegendItem>
                  </ChartLegend>
                </ChartHeader>

                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={data.anomaly_history} barSize={12}>
                    <XAxis
                      dataKey="time"
                      tick={{ fill: '#888', fontSize: 10 }}
                      axisLine={false} tickLine={false}
                    />
                    <YAxis
                      domain={[0, 1]}
                      tick={{ fill: '#888', fontSize: 10 }}
                      axisLine={false} tickLine={false}
                    />
                    <Tooltip contentStyle={{
                      background: '#1a1a1a', border: '1px solid #333',
                      borderRadius: '6px', color: '#fff', fontSize: '12px'
                    }} />
                    <ReferenceLine y={0.7} stroke="#ef4444" strokeDasharray="4 4" strokeWidth={1.5} />
                    <Bar dataKey="score" fill="#0ea5e9" radius={[3, 3, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>

                <ChartFooter>
                  <span>{data.anomaly_history[0]?.time || ""}</span>
                  <span>{data.anomaly_history[data.anomaly_history.length - 1]?.time || "Agora"}</span>
                </ChartFooter>
              </ChartContainer>

              {/* Métricas */}
              <MetricsContainer>
                <span style={{
                  fontSize: '11px', fontWeight: 600, color: '#888',
                  textTransform: 'uppercase', letterSpacing: '0.5px',
                  marginBottom: '8px', display: 'block'
                }}>
                  MÉTRICAS DE INFERÊNCIA
                </span>

                <MetricItem>
                  <MetricHeader>
                    <MetricLabel>LATÊNCIA (MS)</MetricLabel>
                    <MetricValue>{data.metrics.latencia_ms}</MetricValue>
                  </MetricHeader>
                  <MetricBar>
                    <MetricBarFill percentage={Math.min(data.metrics.latencia_ms, 100)} color="#0ea5e9" />
                  </MetricBar>
                </MetricItem>

                <MetricItem>
                  <MetricHeader>
                    <MetricLabel>THROUGHPUT (REQ/S)</MetricLabel>
                    <MetricValue>{data.metrics.throughput}</MetricValue>
                  </MetricHeader>
                  <MetricBar>
                    <MetricBarFill percentage={Math.min(data.metrics.throughput, 100)} color="#0ea5e9" />
                  </MetricBar>
                </MetricItem>

                <MetricItem>
                  <MetricHeader>
                    <MetricLabel>USO DE CPU (%)</MetricLabel>
                    <MetricValue>{data.metrics.cpu_percent}%</MetricValue>
                  </MetricHeader>
                  <MetricInfo>
                    <MetricSubLabel>MEMÓRIA (MODEL)</MetricSubLabel>
                    <MetricSubLabel>{data.metrics.memory_mb}MB</MetricSubLabel>
                  </MetricInfo>
                </MetricItem>

              </MetricsContainer>
            </MonitoringGrid>
          </SectionContent>
        </Section>

      </Content>
    </Container>
  );
}