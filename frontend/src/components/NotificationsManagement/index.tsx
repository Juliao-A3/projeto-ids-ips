import { Mail, Send, Bell, AlertCircle, MessageCircle, Users } from 'lucide-react';
import { ToggleSwitch } from '../ToggleSwitch';
import { useNotifications } from '../../../hooks/useNotifications';
import {
  Container, Content, Section, SectionHeader, SectionTitle, SectionContent,
  EmailForm, FormRow, FormGroup, Label, Input, TestButton, IntegrationsGrid,
  IntegrationCard, IntegrationHeader, IntegrationIcon, IntegrationName,
  IntegrationInput, IntegrationDescription, TriggersGrid, TriggerCard,
  TriggerLabel, TriggerDescription, SystemAlert, Footer, FooterButtons,
  RestoreButton, SaveButton,
} from './styles';

export function NotificationsManagement() {
  const {
    config, setConfig,
    loading, saving, testing,
    error, successMsg,
    saveConfig, testChannel, restoreDefaults,
  } = useNotifications();

  if (loading) return (
    <Container>
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "center",
        height: "200px", color: "#64748B",
        fontFamily: "'Share Tech Mono', monospace", fontSize: "12px"
      }}>
        A CARREGAR CONFIGURAÇÕES...
      </div>
    </Container>
  );

  return (
    <Container>
      <Content>

        {/* Mensagens de feedback */}
        {error && (
          <div style={{
            padding: "10px 14px", marginBottom: "12px",
            background: "#ef444412", border: "1px solid #ef444444",
            borderLeft: "3px solid #ef4444", borderRadius: "4px",
            fontFamily: "'Share Tech Mono', monospace", fontSize: "11px", color: "#ef4444"
          }}>
            ⚠ {error}
          </div>
        )}
        {successMsg && (
          <div style={{
            padding: "10px 14px", marginBottom: "12px",
            background: "#00C85312", border: "1px solid #00C85344",
            borderLeft: "3px solid #00C853", borderRadius: "4px",
            fontFamily: "'Share Tech Mono', monospace", fontSize: "11px", color: "#00C853"
          }}>
            ✓ {successMsg}
          </div>
        )}

        {/* SMTP */}
        {/* SMTP */}
        <Section>
          <SectionHeader>
            <Mail size={16} />
            <SectionTitle>ALERTAS POR E-MAIL</SectionTitle>
            <ToggleSwitch
              checked={config.smtp_enabled}
              onChange={(v) => setConfig(prev => ({ ...prev, smtp_enabled: v }))}
            />
          </SectionHeader>
          <SectionContent>
            <EmailForm>

              {/* Selector de provider */}
              <FormRow style={{ gap: '10px', marginBottom: '4px' }}>
                {["gmail", "outlook"].map((provider) => (
                  <button
                    key={provider}
                    type="button"
                    onClick={() => setConfig(prev => ({ ...prev, email_provider: provider }))}
                    disabled={!config.smtp_enabled}
                    style={{
                      flex: 1,
                      padding: "10px",
                      background: config.email_provider === provider
                        ? "#00A3FF22"
                        : "transparent",
                      border: `1px solid ${config.email_provider === provider ? "#00A3FF" : "#262C36"}`,
                      borderRadius: "4px",
                      color: config.email_provider === provider ? "#00A3FF" : "#64748B",
                      fontFamily: "'Share Tech Mono', monospace",
                      fontSize: "12px",
                      letterSpacing: "0.1em",
                      cursor: config.smtp_enabled ? "pointer" : "not-allowed",
                      transition: "all 0.2s",
                      textTransform: "uppercase",
                    }}
                  >
                    {provider === "gmail" ? "📧 Gmail" : "📨 Outlook"}
                  </button>
                ))}
              </FormRow>

              {/* Instrução de senha de aplicação */}
              {config.smtp_enabled && (
                <div style={{
                  padding: "10px 12px",
                  background: "#00A3FF08",
                  border: "1px solid #00A3FF22",
                  borderLeft: "3px solid #00A3FF",
                  borderRadius: "4px",
                  marginBottom: "4px",
                }}>
                  <p style={{
                    fontFamily: "'Share Tech Mono', monospace",
                    fontSize: "10px",
                    color: "#94A3B8",
                    lineHeight: 1.6,
                    margin: 0,
                  }}>
                    {config.email_provider === "gmail" ? (
                      <>
                        <strong style={{ color: "#00A3FF" }}>Gmail:</strong> Usa uma{" "}
                        <strong>senha de aplicação</strong> — não a tua senha normal.{" "}
                        Vai a <strong>myaccount.google.com → Segurança → Senhas de app</strong>
                      </>
                    ) : (
                      <>
                        <strong style={{ color: "#00A3FF" }}>Outlook:</strong> Usa uma{" "}
                        <strong>senha de aplicação</strong> — não a tua senha normal.{" "}
                        Vai a <strong>account.microsoft.com → Segurança → Senhas de app</strong>
                      </>
                    )}
                  </p>
                </div>
              )}

              {/* Email e senha */}
              <FormRow>
                <FormGroup style={{ flex: 1 }}>
                  <Label>
                    {config.email_provider === "gmail" ? "CONTA GMAIL" : "CONTA OUTLOOK"}
                  </Label>
                  <Input
                    type="text"
                    value={config.smtp_username || ""}
                    onChange={(e) => setConfig(prev => ({ ...prev, smtp_username: e.target.value }))}
                    placeholder={config.email_provider === "gmail"
                      ? "exemplo@gmail.com"
                      : "exemplo@outlook.com"
                    }
                    disabled={!config.smtp_enabled}
                  />
                </FormGroup>
                <FormGroup style={{ flex: 1 }}>
                  <Label>SENHA DE APLICAÇÃO</Label>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <Input
                      type="password"
                      value={config.smtp_password || ""}
                      onChange={(e) => setConfig(prev => ({ ...prev, smtp_password: e.target.value }))}
                      placeholder="••••••••••••••••"
                      disabled={!config.smtp_enabled}
                    />
                    <TestButton
                      type="button"
                      onClick={() => testChannel("email")}
                      disabled={!config.smtp_enabled || testing === "email"}
                    >
                      {testing === "email" ? "A TESTAR..." : "TESTAR"}
                    </TestButton>
                  </div>
                </FormGroup>
              </FormRow>

            </EmailForm>
          </SectionContent>
        </Section>

        {/* INTEGRAÇÕES */}
        <Section>
          <SectionHeader>
            <Send size={16} />
            <SectionTitle>INTEGRAÇÕES EXTERNAS</SectionTitle>
          </SectionHeader>
          <SectionContent>
            <IntegrationsGrid>

              {/* Telegram */}
              <IntegrationCard>
                <IntegrationHeader>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <IntegrationIcon>✈️</IntegrationIcon>
                    <IntegrationName>TELEGRAM</IntegrationName>
                  </div>
                  <ToggleSwitch
                    checked={config.telegram_enabled}
                    onChange={(v) => setConfig(prev => ({ ...prev, telegram_enabled: v }))}
                  />
                </IntegrationHeader>
                <FormRow style={{ gap: '10px' }}>
                  <IntegrationInput
                    type="text"
                    value={config.telegram_token || ""}
                    onChange={(e) => setConfig(prev => ({ ...prev, telegram_token: e.target.value }))}
                    placeholder="BOT TOKEN"
                    disabled={!config.telegram_enabled}
                  />
                  <IntegrationInput
                    type="text"
                    value={config.telegram_chat_id || ""}
                    onChange={(e) => setConfig(prev => ({ ...prev, telegram_chat_id: e.target.value }))}
                    placeholder="CHAT ID"
                    disabled={!config.telegram_enabled}
                  />
                </FormRow>
                <TestButton
                  type="button"
                  onClick={() => testChannel("telegram")}
                  disabled={!config.telegram_enabled || testing === "telegram"}
                  style={{ marginTop: '8px' }}
                >
                  {testing === "telegram" ? "A TESTAR..." : "TESTAR TELEGRAM"}
                </TestButton>
                <IntegrationDescription>
                  Cria um bot no @BotFather e cola o token + chat ID para receber alertas.
                </IntegrationDescription>
              </IntegrationCard>

              {/* Microsoft Teams */}
              <IntegrationCard>
                <IntegrationHeader>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <IntegrationIcon>👥</IntegrationIcon>
                    <IntegrationName>MICROSOFT TEAMS</IntegrationName>
                  </div>
                  <ToggleSwitch
                    checked={config.teams_enabled}
                    onChange={(v) => setConfig(prev => ({ ...prev, teams_enabled: v }))}
                  />
                </IntegrationHeader>
                <IntegrationInput
                  type="text"
                  value={config.teams_webhook || ""}
                  onChange={(e) => setConfig(prev => ({ ...prev, teams_webhook: e.target.value }))}
                  placeholder="https://outlook.office.com/webhook/..."
                  disabled={!config.teams_enabled}
                />
                <TestButton
                  type="button"
                  onClick={() => testChannel("teams")}
                  disabled={!config.teams_enabled || testing === "teams"}
                  style={{ marginTop: '8px' }}
                >
                  {testing === "teams" ? "A TESTAR..." : "TESTAR TEAMS"}
                </TestButton>
                <IntegrationDescription>
                  Cole a URL do webhook para receber alertas no Microsoft Teams.
                </IntegrationDescription>
              </IntegrationCard>

            </IntegrationsGrid>
          </SectionContent>
        </Section>

        {/* GATILHOS */}
        <Section>
          <SectionHeader>
            <Bell size={16} />
            <SectionTitle>GATILHOS DE NOTIFICAÇÃO</SectionTitle>
          </SectionHeader>
          <SectionContent>
            <p style={{ fontSize: '12px', color: '#888', margin: '0 0 16px 0', lineHeight: 1.5 }}>
              Disparar alerta para os seguintes níveis de severidade:
            </p>
            <TriggersGrid>
              <TriggerCard severity="critical">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <TriggerLabel severity="critical">CRÍTICO</TriggerLabel>
                  <ToggleSwitch
                    checked={config.trigger_critical}
                    onChange={(v) => setConfig(prev => ({ ...prev, trigger_critical: v }))}
                  />
                </div>
                <TriggerDescription>Ataques coordenados ou falha total de um componente.</TriggerDescription>
              </TriggerCard>

              <TriggerCard severity="high">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <TriggerLabel severity="high">ALTO</TriggerLabel>
                  <ToggleSwitch
                    checked={config.trigger_high}
                    onChange={(v) => setConfig(prev => ({ ...prev, trigger_high: v }))}
                  />
                </div>
                <TriggerDescription>Tentativa de intrusão ou tráfego anômalo grave.</TriggerDescription>
              </TriggerCard>

              <TriggerCard severity="medium">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <TriggerLabel severity="medium">MÉDIO</TriggerLabel>
                  <ToggleSwitch
                    checked={config.trigger_medium}
                    onChange={(v) => setConfig(prev => ({ ...prev, trigger_medium: v }))}
                  />
                </div>
                <TriggerDescription>Requisições e comportamentos incomuns moderados.</TriggerDescription>
              </TriggerCard>
            </TriggersGrid>
          </SectionContent>
        </Section>

        {/* ALERTA DE SISTEMA */}
        <Section>
          <SectionHeader>
            <AlertCircle size={16} />
            <SectionTitle>ALERTAS DE SISTEMA</SectionTitle>
          </SectionHeader>
          <SectionContent>
            <SystemAlert>
              <AlertCircle size={18} />
              <span>
                As configurações são guardadas na base de dados. Certifique-se que a conectividade de rede está disponível antes de testar.
              </span>
            </SystemAlert>
          </SectionContent>
        </Section>

      </Content>

      {/* FOOTER */}
      <Footer>
        <FooterButtons>
          <RestoreButton type="button" onClick={restoreDefaults}>
            RESTAURAR PADRÕES
          </RestoreButton>
          <SaveButton type="button" onClick={saveConfig} disabled={saving}>
            {saving ? "A GUARDAR..." : "SALVAR ALTERAÇÕES"}
          </SaveButton>
        </FooterButtons>
      </Footer>
    </Container>
  );
}