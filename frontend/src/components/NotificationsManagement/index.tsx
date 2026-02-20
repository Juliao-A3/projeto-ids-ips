import { useState } from 'react';
import { Mail, Plug, Bell, AlertCircle } from 'lucide-react';
import { ToggleSwitch } from '../ToggleSwitch';
import {
  Container,
  Content,
  Section,
  SectionHeader,
  SectionTitle,
  SectionContent,
  EmailForm,
  FormRow,
  FormGroup,
  Label,
  Input,
  TestButton,
  IntegrationsGrid,
  IntegrationCard,
  IntegrationHeader,
  IntegrationIcon,
  IntegrationName,
  IntegrationInput,
  IntegrationDescription,
  TriggersGrid,
  TriggerCard,
  TriggerLabel,
  TriggerDescription,
  SystemAlert,
  Footer,
  FooterButtons,
  RestoreButton,
  SaveButton,
} from './styles';

export function NotificationsManagement() {
  const [smtpServer, setSmtpServer] = useState('smtp.servidor.com');
  const [smtpPort, setSmtpPort] = useState('587');
  const [sslEnabled, setSslEnabled] = useState(true);
  const [username, setUsername] = useState('alertas@aegis.ai');
  const [password, setPassword] = useState('');

  const [discordEnabled, setDiscordEnabled] = useState(false);
  const [discordWebhook, setDiscordWebhook] = useState('https://hooks.slack.com/services/...');
  const [teamsEnabled, setTeamsEnabled] = useState(true);
  const [teamsWebhook, setTeamsWebhook] = useState('https://outlook.office.com/webhook/...');

  const [criticalEnabled, setCriticalEnabled] = useState(true);
  const [highEnabled, setHighEnabled] = useState(true);
  const [mediumEnabled, setMediumEnabled] = useState(false);

  return (
    <Container>
      <Content>
        {/* ALERTAS POR E-MAIL (SMTP) */}
        <Section>
          <SectionHeader>
            <Mail size={16} />
            <SectionTitle>ALERTAS POR E-MAIL (SMTP)</SectionTitle>
          </SectionHeader>
          <SectionContent>
            <EmailForm>
              <FormRow>
                <FormGroup style={{ flex: 2 }}>
                  <Label>SERVIDOR SMTP</Label>
                  <Input
                    type="text"
                    value={smtpServer}
                    onChange={(e) => setSmtpServer(e.target.value)}
                    placeholder="smtp.servidor.com"
                  />
                </FormGroup>

                <FormGroup style={{ flex: 1 }}>
                  <Label>PORTA</Label>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <Input
                      type="text"
                      value={smtpPort}
                      onChange={(e) => setSmtpPort(e.target.value)}
                      placeholder="587"
                    />
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <ToggleSwitch
                        checked={sslEnabled}
                        onChange={setSslEnabled}
                      />
                      <span style={{ 
                        fontSize: '11px', 
                        color: '#888',
                        textTransform: 'uppercase',
                        whiteSpace: 'nowrap'
                      }}>
                        SSL/TLS
                      </span>
                    </div>
                  </div>
                </FormGroup>
              </FormRow>

              <FormRow>
                <FormGroup style={{ flex: 1 }}>
                  <Label>USUÁRIO</Label>
                  <Input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="alertas@aegis.ai"
                  />
                </FormGroup>

                <FormGroup style={{ flex: 1 }}>
                  <Label>SENHA</Label>
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <Input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                    />
                    <TestButton>TESTAR E-MAIL</TestButton>
                  </div>
                </FormGroup>
              </FormRow>
            </EmailForm>
          </SectionContent>
        </Section>

        {/* INTEGRAÇÕES EXTERNAS */}
        <Section>
          <SectionHeader>
            <Plug size={16} />
            <SectionTitle>INTEGRAÇÕES EXTERNAS</SectionTitle>
          </SectionHeader>
          <SectionContent>
            <IntegrationsGrid>
              <IntegrationCard>
                <IntegrationHeader>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <IntegrationIcon>💬</IntegrationIcon>
                    <IntegrationName>DISCORD / SLACK WEBHOOK</IntegrationName>
                  </div>
                  <ToggleSwitch
                    checked={discordEnabled}
                    onChange={setDiscordEnabled}
                  />
                </IntegrationHeader>
                <IntegrationInput
                  type="text"
                  value={discordWebhook}
                  onChange={(e) => setDiscordWebhook(e.target.value)}
                  placeholder="https://hooks.slack.com/services/..."
                  disabled={!discordEnabled}
                />
                <IntegrationDescription>
                  Cole a URL do webhook para receber alertas diretamente no Discord ou Slack.
                </IntegrationDescription>
              </IntegrationCard>

              <IntegrationCard>
                <IntegrationHeader>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <IntegrationIcon>👥</IntegrationIcon>
                    <IntegrationName>MICROSOFT TEAMS</IntegrationName>
                  </div>
                  <ToggleSwitch
                    checked={teamsEnabled}
                    onChange={setTeamsEnabled}
                  />
                </IntegrationHeader>
                <IntegrationInput
                  type="text"
                  value={teamsWebhook}
                  onChange={(e) => setTeamsWebhook(e.target.value)}
                  placeholder="https://outlook.office.com/webhook/..."
                  disabled={!teamsEnabled}
                />
                <IntegrationDescription>
                  Cole a URL do webhook para receber alertas diretamente no Microsoft Teams.
                </IntegrationDescription>
              </IntegrationCard>
            </IntegrationsGrid>
          </SectionContent>
        </Section>

        {/* GATILHOS DE NOTIFICAÇÃO */}
        <Section>
          <SectionHeader>
            <Bell size={16} />
            <SectionTitle>GATILHOS DE NOTIFICAÇÃO</SectionTitle>
          </SectionHeader>
          <SectionContent>
            <p style={{ 
              fontSize: '12px', 
              color: '#888', 
              margin: '0 0 16px 0',
              lineHeight: 1.5
            }}>
              Disparar alerta para os seguintes níveis de severidade:
            </p>
            <TriggersGrid>
              <TriggerCard severity="critical">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <TriggerLabel severity="critical">CRÍTICO</TriggerLabel>
                  <ToggleSwitch
                    checked={criticalEnabled}
                    onChange={setCriticalEnabled}
                  />
                </div>
                <TriggerDescription>
                  Ataques coordenados ou falha total de um componente.
                </TriggerDescription>
              </TriggerCard>

              <TriggerCard severity="high">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <TriggerLabel severity="high">ALTO</TriggerLabel>
                  <ToggleSwitch
                    checked={highEnabled}
                    onChange={setHighEnabled}
                  />
                </div>
                <TriggerDescription>
                  Tentativa de intrusão ou tráfego anômalo grave.
                </TriggerDescription>
              </TriggerCard>

              <TriggerCard severity="medium">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <TriggerLabel severity="medium">MÉDIO</TriggerLabel>
                  <ToggleSwitch
                    checked={mediumEnabled}
                    onChange={setMediumEnabled}
                  />
                </div>
                <TriggerDescription>
                  Requisições e comportamentos incomuns moderados.
                </TriggerDescription>
              </TriggerCard>
            </TriggersGrid>
          </SectionContent>
        </Section>

        {/* ALERTAS DE SISTEMA */}
        <Section>
          <SectionHeader>
            <AlertCircle size={16} />
            <SectionTitle>ALERTAS DE SISTEMA</SectionTitle>
          </SectionHeader>
          <SectionContent>
            <SystemAlert>
              <AlertCircle size={18} />
              <span>
                As configurações de notificação são salvas locais. Certifique-se que a conectividade de rede está disponível.
              </span>
            </SystemAlert>
          </SectionContent>
        </Section>
      </Content>

      {/* FOOTER */}
      <Footer>
        <FooterButtons>
          <RestoreButton>RESTAURAR PADRÕES</RestoreButton>
          <SaveButton>SALVAR ALTERAÇÕES</SaveButton>
        </FooterButtons>
      </Footer>
    </Container>
  );
}