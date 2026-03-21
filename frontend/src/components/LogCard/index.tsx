import { LogInfo } from '../LogInfo';
import TrafficIntegrityStatus from '../TrafficIntegrityStatus';
import { useSniffer } from '../../../hooks/useSniffer';
import { api } from '../../../src/services/api';
import {
  LogContainer, LogSection, LogHeader, HeaderTitle,
  ListIcon, LogTitle, ButtonContainer, LogsButton,
  Divider, ListaMenu, SidebarWrapper, SidebarContainer,
  CoreContainer, CoreTitle, CoreMain, CoreMode,
  CoreSubTitle, CoreStatus, CoreSection,
  IniciaButton, PausarButton, ReporButton,
  LogsList,
} from './styles';

export function LogCard() {
  const { status, loading, error, pacotes, iniciar, pausar, reboot } = useSniffer();

  const handleWhitelist = (ip: string) => {
    api.post('/sniffer/whitelist/add', { ip });
  };

  return (
    <LogContainer>
      <LogSection>
        <LogHeader>
          <HeaderTitle>
            <ListIcon />
            <LogTitle>LOGS EM TEMPO REAL</LogTitle>
          </HeaderTitle>
          <ButtonContainer>
            <LogsButton>FILTROS</LogsButton>
            <LogsButton>EXPORTAR CSV</LogsButton>
          </ButtonContainer>
        </LogHeader>

        <Divider />

        <ListaMenu>
          <span>Timestamp</span>
          <span>Origem</span>
          <span>Destino</span>
          <span>Protocolo</span>
          <span>Tipo</span>
          <span>Ações</span>
        </ListaMenu>

        <Divider />
        <LogsList>
          {pacotes.length === 0 ? (
            <div style={{
              textAlign: 'center', padding: '2rem',
              fontFamily: "'Share Tech Mono', monospace",
              fontSize: 11, color: '#64748B'
            }}>
              {status.running
                ? 'A aguardar pacotes...'
                : 'Sniffer inativo — clica em Iniciar para começar'
              }
            </div>
          ) : (
            pacotes.map((p, i) => <LogInfo key={i} data={p} />)
          )}
        </LogsList>
      </LogSection>

      <SidebarWrapper>
        <SidebarContainer>
          <TrafficIntegrityStatus />
        </SidebarContainer>

        <CoreContainer>
          <CoreTitle>Controles Core</CoreTitle>

          {error && (
            <div style={{
              padding: '8px 12px', marginBottom: 8,
              background: 'rgba(239,68,68,0.1)',
              border: '1px solid rgba(239,68,68,0.3)',
              borderRadius: 6,
              fontFamily: "'Share Tech Mono', monospace",
              fontSize: 10, color: '#EF4444'
            }}>
              ⚠ {error}
            </div>
          )}

          <CoreMain>
            <CoreMode>
              <CoreSubTitle>MODO IDS/IPS</CoreSubTitle>
              <CoreStatus style={{ color: status.running ? '#00C853' : '#EF4444' }}>
                {status.running ? '● ATIVO' : '○ INATIVO'}
              </CoreStatus>
            </CoreMode>

            {status.running && (
              <div style={{
                display: 'grid', gridTemplateColumns: '1fr 1fr',
                gap: 8, marginBottom: 12
              }}>
                {[
                  { label: 'PACOTES',   value: status.contador,          color: '#00A3FF' },
                  { label: 'ANOMALIAS', value: status.anomalias,         color: '#EF4444' },
                  { label: 'BLOQUEIOS', value: status.bloqueios,         color: '#FFAB00' },
                  { label: 'TAXA',      value: `${status.taxa_anomalia}%`, color: '#A855F7' },
                ].map(({ label, value, color }) => (
                  <div key={label} style={{
                    background: 'rgba(0,0,0,0.2)',
                    border: `1px solid ${color}33`,
                    borderRadius: 6, padding: '6px 10px', textAlign: 'center'
                  }}>
                    <div style={{ fontFamily: "'Orbitron', monospace", fontSize: 14, fontWeight: 700, color }}>
                      {value}
                    </div>
                    <div style={{ fontFamily: "'Share Tech Mono', monospace", fontSize: 8, color: '#64748B', letterSpacing: 1 }}>
                      {label}
                    </div>
                  </div>
                ))}
              </div>
            )}

            <CoreSection>
              <IniciaButton
                onClick={() => iniciar()}
                disabled={loading || status.running}
                style={{ opacity: status.running ? 0.4 : 1 }}
              >
                {loading && !status.running ? 'A INICIAR...' : 'Iniciar'}
              </IniciaButton>

              <PausarButton
                onClick={pausar}
                disabled={loading || !status.running}
                style={{ opacity: !status.running ? 0.4 : 1 }}
              >
                {loading && status.running ? 'A PAUSAR...' : 'Pausar'}
              </PausarButton>

              <ReporButton onClick={() => reboot()} disabled={loading}>
                Reboot
              </ReporButton>
            </CoreSection>
          </CoreMain>
        </CoreContainer>

        {/* IPs Suspeitos */}
        {status.running && Object.keys(status.contagem_ips || {}).length > 0 && (
          <div style={{
              background: '#151921',
              border: '1px solid #262C36',
              borderRadius: 10,
              padding: 16,
              marginTop: 12,
              maxHeight: '280px',       // ← altura proporcional aos logs
              overflowY: 'auto',        // ← scroll interno
              scrollbarWidth: 'thin',   // ← scrollbar fina (Firefox)
            }}>
            <div style={{
              fontFamily: "'Orbitron', monospace",
              fontSize: 10, fontWeight: 700,
              color: '#FFAB00', letterSpacing: 2,
              marginBottom: 12,
              position: 'sticky',     // ← título fica fixo ao fazer scroll
              top: 0,
              background: '#151921',
              paddingBottom: 8,
            }}>
              ⚠ IPs SUSPEITOS ({Object.keys(status.contagem_ips).length})
            </div>

            {Object.entries(status.contagem_ips)
              .sort((a, b) => b[1] - a[1])
              .slice(0, 5)
              .map(([ip, count]) => {
                const bloqueado    = status.ips_bloqueados.includes(ip);
                const naWhitelist  = (status.whitelist || []).includes(ip);
                const pct          = Math.min((count / 5) * 100, 100);
                const cor          = bloqueado ? '#EF4444' : count >= 4 ? '#FFAB00' : '#00A3FF';

                return (
                  <div key={ip} style={{ marginBottom: 10 }}>
                    <div style={{
                      display: 'flex', justifyContent: 'space-between',
                      alignItems: 'center', marginBottom: 4,
                    }}>
                      <span style={{ fontFamily: "'Share Tech Mono', monospace", fontSize: 10, color: cor }}>
                        {bloqueado ? '🔒 ' : naWhitelist ? '✅ ' : '⚠ '}{ip}
                      </span>
                      <span style={{ fontFamily: "'Share Tech Mono', monospace", fontSize: 9, color: '#64748B' }}>
                        {count}/5
                      </span>
                    </div>

                    <div style={{ width: '100%', height: 4, background: '#262C36', borderRadius: 2, overflow: 'hidden' }}>
                      <div style={{
                        height: '100%', width: `${pct}%`,
                        background: cor, borderRadius: 2, transition: 'width 0.5s ease',
                      }} />
                    </div>

                    {!bloqueado && !naWhitelist && (
                      <button
                        onClick={() => handleWhitelist(ip)}
                        style={{
                          marginTop: 4, padding: '2px 8px',
                          background: 'rgba(0,200,83,0.1)',
                          border: '1px solid rgba(0,200,83,0.3)',
                          borderRadius: 4, cursor: 'pointer',
                          fontFamily: "'Share Tech Mono', monospace",
                          fontSize: 9, color: '#00C853',
                        }}
                      >
                        + WHITELIST
                      </button>
                    )}
                  </div>
                );
              })
            }
          </div>
        )}

      </SidebarWrapper>
    </LogContainer>
  );
}