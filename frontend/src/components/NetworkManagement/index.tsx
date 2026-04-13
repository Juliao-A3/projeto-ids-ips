import { useState, useEffect } from 'react';
import { Activity, Shield, Zap, Lock, Unlock, Radio } from 'lucide-react';
import { ToggleSwitch } from '../ToggleSwitch';
import { Dropdown } from '../Dropdown';
import { TextArea } from '../TextArea';
import { useNetwork } from '../../../hooks/useNetwork';
import type { NetworkConfigSchema } from '../../../hooks/useNetwork';
import { useAuth } from '../../contexts/AuthContext';
import {
  Container, Content, Section, SectionHeader, SectionTitle,
  SectionContent, BridgeConfig, BridgeDescription, BridgeSettings,
  BridgeToggles, TwoColumnsWrapper, Footer, FooterButtons,
  RestoreButton, SaveButton, WhitelistEditor, WhitelistInputRow,
  WhitelistInput, WhitelistAddButton, WhitelistList, WhitelistChip,
  WhitelistChipButton, WhitelistHint, WhitelistError, Label,
} from './styles';

export function NetworkManagement() {
  const { user }    = useAuth();
  const {
    interfaces, blockedIps, config,
    loading, saving, error, successMsg,
    unblockIp, saveConfig, restoreDefaults
  } = useNetwork();

  const [captureInterface, setCaptureInterface] = useState('eth0');
  const [promiscuousMode, setPromiscuousMode]   = useState(true);
  const [bpfFilter, setBpfFilter]               = useState('');
  const [whitelistEntries, setWhitelistEntries]  = useState<string[]>([]);
  const [whitelistInput, setWhitelistInput]      = useState('');
  const [whitelistError, setWhitelistError]      = useState('');
  const [whitelistDirty, setWhitelistDirty]      = useState(false);

  const parseWhitelist = (value: string) =>
    Array.from(
      new Set(
        value
          .split(/[\n,]/)
          .map(entry => entry.trim())
          .filter(Boolean)
      )
    );

  const isValidIPv4 = (value: string) => {
    const ipv4Pattern = /^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$/;
    return ipv4Pattern.test(value.trim());
  };

  const persistWhitelistEntries = (entries: string[]) => {
    setWhitelistEntries(entries);
    setWhitelistDirty(true);
  };

  // sincroniza com dados do backend
  useEffect(() => {
    if (config && !whitelistDirty) {
      setCaptureInterface(config.capture_interface);
      setPromiscuousMode(config.promiscuous_mode);
      setBpfFilter(config.bpf_filter);
      setWhitelistEntries(parseWhitelist(config.whitelist));
    }
  }, [config, whitelistDirty]);

  const interfaceOptions = interfaces.map(i => ({
    value: i.name,
    label: `${i.name} — ${i.ip} (${i.status})`
  }));

  const handleSave = async () => {
    const saved = await saveConfig({
      capture_interface: captureInterface,
      promiscuous_mode:  promiscuousMode,
      bpf_filter:        bpfFilter,
      whitelist: whitelistEntries.join(', '),
    });
    if (saved) {
      setWhitelistDirty(false);
    }
  };

  const handleAddWhitelistIp = () => {
    const candidate = whitelistInput.trim();
    if (!candidate) {
      setWhitelistError('Informe um IP válido.');
      return;
    }

    if (!isValidIPv4(candidate)) {
      setWhitelistError('IP inválido. Use IPv4 no formato 192.168.1.10.');
      return;
    }

    if (whitelistEntries.includes(candidate)) {
      setWhitelistError('Esse IP já está na lista branca.');
      return;
    }

    persistWhitelistEntries([...whitelistEntries, candidate]);
    setWhitelistInput('');
    setWhitelistError('');
  };

  const handleRemoveWhitelistIp = (ip: string) => {
    persistWhitelistEntries(whitelistEntries.filter(entry => entry !== ip));
    setWhitelistError('');
  };

  return (
    <Container>
      <Content>

        {/* INTERFACES DE MONITORAMENTO */}
        <Section>
          <SectionHeader>
            <Activity size={16} />
            <SectionTitle>INTERFACES DE MONITORAMENTO</SectionTitle>
          </SectionHeader>
          <SectionContent>
            {loading ? (
              <div style={{ color: '#64748B', fontSize: '12px', fontFamily: "'Share Tech Mono', monospace" }}>
                A CARREGAR INTERFACES...
              </div>
            ) : (
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #262C36' }}>
                    {['INTERFACE', 'STATUS', 'IP', 'MAC', 'VELOCIDADE', 'PKT ENVIADOS', 'PKT RECEBIDOS'].map(h => (
                      <th key={h} style={{
                        padding: '8px 12px', textAlign: 'left',
                        color: '#64748B', fontFamily: "'Share Tech Mono', monospace",
                        fontWeight: 600, fontSize: '10px'
                      }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {interfaces.map((iface, i) => (
                    <tr key={iface.name} style={{
                      borderBottom: '1px solid #1a2030',
                      background: i % 2 === 0 ? 'transparent' : '#0d1117'
                    }}>
                      <td style={{ padding: '8px 12px', color: '#fff', fontFamily: "'Share Tech Mono', monospace" }}>
                        {iface.name}
                      </td>
                      <td style={{ padding: '8px 12px' }}>
                        <span style={{
                          display: 'inline-flex', alignItems: 'center', gap: '6px',
                          padding: '2px 8px', borderRadius: '4px', fontSize: '10px',
                          fontWeight: 700, fontFamily: "'Share Tech Mono', monospace",
                          background: iface.status === 'UP' ? '#00C85320' : '#ef444420',
                          color: iface.status === 'UP' ? '#00C853' : '#ef4444',
                          border: `1px solid ${iface.status === 'UP' ? '#00C85340' : '#ef444440'}`,
                        }}>
                          <span style={{
                            width: '6px', height: '6px', borderRadius: '50%',
                            background: iface.status === 'UP' ? '#00C853' : '#ef4444',
                          }} />
                          {iface.status}
                        </span>
                      </td>
                      <td style={{ padding: '8px 12px', color: '#94A3B8', fontFamily: "'Share Tech Mono', monospace", fontSize: '11px' }}>
                        {iface.ip}
                      </td>
                      <td style={{ padding: '8px 12px', color: '#94A3B8', fontFamily: "'Share Tech Mono', monospace", fontSize: '11px' }}>
                        {iface.mac}
                      </td>
                      <td style={{ padding: '8px 12px', color: '#94A3B8', fontFamily: "'Share Tech Mono', monospace", fontSize: '11px' }}>
                        {iface.speed}
                      </td>
                      <td style={{ padding: '8px 12px', color: '#94A3B8', fontFamily: "'Share Tech Mono', monospace", fontSize: '11px' }}>
                        {iface.packets_sent.toLocaleString()}
                      </td>
                      <td style={{ padding: '8px 12px', color: '#94A3B8', fontFamily: "'Share Tech Mono', monospace", fontSize: '11px' }}>
                        {iface.packets_recv.toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </SectionContent>
        </Section>

        {/* CAPTURA SCAPY */}
        <Section>
          <SectionHeader>
            <Radio size={16} />
            <SectionTitle>CONFIGURAÇÃO DE CAPTURA (SCAPY)</SectionTitle>
          </SectionHeader>
          <SectionContent>
            <BridgeConfig>
              <BridgeSettings>
                <div>
                  <h3 style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: 600 }}>
                    MODO PROMÍSCUO
                  </h3>
                  <BridgeDescription>
                    Captura todos os pacotes que passam pela interface — não apenas os destinados a esta máquina.
                  </BridgeDescription>
                </div>
                <BridgeToggles>
                  <ToggleSwitch checked={promiscuousMode} onChange={setPromiscuousMode} />
                </BridgeToggles>
              </BridgeSettings>

              <div style={{ marginTop: '16px' }}>
                <Dropdown
                  label="INTERFACE DE CAPTURA"
                  value={captureInterface}
                  onChange={setCaptureInterface}
                  options={interfaceOptions.length > 0 ? interfaceOptions : [
                    { value: 'eth0', label: 'eth0' },
                    { value: 'eth1', label: 'eth1' },
                    { value: 'wlan0', label: 'wlan0' },
                  ]}
                />
              </div>

              <div style={{ marginTop: '16px' }}>
                <TextArea
                  label="FILTRO BPF (BERKELEY PACKET FILTER)"
                  value={bpfFilter}
                  onChange={setBpfFilter}
                  placeholder="Ex: tcp port 80, udp, icmp, not port 22"
                  description="Filtro nativo do Scapy para limitar o tráfego capturado. Deixe vazio para capturar tudo."
                  rows={3}
                />
              </div>
            </BridgeConfig>
          </SectionContent>
        </Section>

        <TwoColumnsWrapper>
          {/* WHITELIST */}
          <Section>
            <SectionHeader>
              <Shield size={16} />
              <SectionTitle>LISTA BRANCA (WHITELIST)</SectionTitle>
            </SectionHeader>
            <SectionContent>
                <WhitelistEditor>
                  <div>
                    <Label>ADICIONAR IP À LISTA BRANCA</Label>
                    <WhitelistInputRow>
                      <WhitelistInput
                        value={whitelistInput}
                        onChange={(e) => {
                          setWhitelistInput(e.target.value);
                          if (whitelistError) setWhitelistError('');
                        }}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            handleAddWhitelistIp();
                          }
                        }}
                        placeholder="Ex: 192.168.1.10"
                      />
                      <WhitelistAddButton
                        type="button"
                        onClick={handleAddWhitelistIp}
                        disabled={!whitelistInput.trim()}
                      >
                        ADICIONAR
                      </WhitelistAddButton>
                    </WhitelistInputRow>
                    <WhitelistHint>
                      Apenas IPs IPv4 válidos podem ser adicionados aqui. Entradas já existentes, como redes CIDR, continuam preservadas na lista.
                    </WhitelistHint>
                    {whitelistError && <WhitelistError>{whitelistError}</WhitelistError>}
                  </div>

                  <div>
                    <Label>IPS E REDES NA LISTA</Label>
                    <WhitelistList>
                      {whitelistEntries.length === 0 ? (
                        <WhitelistHint>Nenhum IP configurado na whitelist.</WhitelistHint>
                      ) : (
                        whitelistEntries.map((ip) => (
                          <WhitelistChip key={ip}>
                            {ip}
                            <WhitelistChipButton
                              type="button"
                              onClick={() => handleRemoveWhitelistIp(ip)}
                              aria-label={`Remover ${ip}`}
                              title="Remover"
                            >
                              ×
                            </WhitelistChipButton>
                          </WhitelistChip>
                        ))
                      )}
                    </WhitelistList>
                  </div>
                </WhitelistEditor>
            </SectionContent>
          </Section>

          {/* IPS BLOQUEADOS */}
          {user?.role === 'admin' && (
            <Section>
              <SectionHeader>
                <Lock size={16} />
                <SectionTitle>IPs BLOQUEADOS</SectionTitle>
              </SectionHeader>
              <SectionContent>
                {blockedIps.length === 0 ? (
                  <div style={{ color: '#64748B', fontSize: '12px', fontFamily: "'Share Tech Mono', monospace", padding: '12px 0' }}>
                    Nenhum IP bloqueado no momento.
                  </div>
                ) : (
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid #262C36' }}>
                        {['IP BLOQUEADO', 'MOTIVO', 'BLOQUEADO EM', 'AÇÃO'].map(h => (
                          <th key={h} style={{
                            padding: '8px 12px', textAlign: 'left',
                            color: '#64748B', fontFamily: "'Share Tech Mono', monospace",
                            fontWeight: 600, fontSize: '10px'
                          }}>{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {blockedIps.map((ip, i) => (
                        <tr key={ip.id} style={{
                          borderBottom: '1px solid #1a2030',
                          background: i % 2 === 0 ? 'transparent' : '#0d1117'
                        }}>
                          <td style={{ padding: '8px 12px', color: '#ef4444', fontFamily: "'Share Tech Mono', monospace" }}>
                            {ip.ip_bloqueado}
                          </td>
                          <td style={{ padding: '8px 12px', color: '#94A3B8', fontFamily: "'Share Tech Mono', monospace", fontSize: '11px' }}>
                            {ip.motivo || '-'}
                          </td>
                          <td style={{ padding: '8px 12px', color: '#94A3B8', fontFamily: "'Share Tech Mono', monospace", fontSize: '11px' }}>
                            {ip.bloqueado_em?.slice(0, 19).replace('T', ' ')}
                          </td>
                          <td style={{ padding: '8px 12px' }}>
                            <button
                              onClick={() => unblockIp(ip.id)}
                              style={{
                                display: 'inline-flex', alignItems: 'center', gap: '5px',
                                padding: '4px 10px', borderRadius: '4px', cursor: 'pointer',
                                background: '#00C85320', color: '#00C853',
                                border: '1px solid #00C85340', fontSize: '10px',
                                fontFamily: "'Share Tech Mono', monospace", fontWeight: 700,
                              }}
                            >
                              <Unlock size={11} />
                              DESBLOQUEAR
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </SectionContent>
            </Section>
          )}
        </TwoColumnsWrapper>

        {/* mensagens */}
        {successMsg && (
          <div style={{
            padding: '10px 14px', background: '#00C85312',
            border: '1px solid #00C85344', borderLeft: '3px solid #00C853',
            borderRadius: '4px', fontFamily: "'Share Tech Mono', monospace",
            fontSize: '11px', color: '#00C853'
          }}>
            ✓ {successMsg}
          </div>
        )}
        {error && (
          <div style={{
            padding: '10px 14px', background: '#ef444412',
            border: '1px solid #ef444444', borderLeft: '3px solid #ef4444',
            borderRadius: '4px', fontFamily: "'Share Tech Mono', monospace",
            fontSize: '11px', color: '#ef4444'
          }}>
            ⚠ {error}
          </div>
        )}

      </Content>

      <Footer>
        <FooterButtons>
          <RestoreButton type="button" onClick={restoreDefaults}>
            RESTAURAR PADRÕES
          </RestoreButton>
          <SaveButton type="button" onClick={handleSave} disabled={saving}>
            {saving ? 'A SALVAR...' : 'SALVAR ALTERAÇÕES'}
          </SaveButton>
        </FooterButtons>
      </Footer>
    </Container>
  );
}