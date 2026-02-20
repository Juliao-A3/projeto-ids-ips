import { useState } from 'react';
import { 
  RotateCw, 
  FileSignature,
  Shield,
  Cpu,
  FileJson  
} from 'lucide-react';
import { RadioToggle } from '../RadioToggle';
import { ToggleSwitch } from '../ToggleSwitch';
import { RuleSetCard } from '../RuleSetCard';
import { NumberInput } from '../NumberInput';
import { LogToggle } from '../LogToggle';
import {
  Container,
  Header,
  HeaderTitle,
  ForceUpdateButton,
  Section,
  SectionHeader,
  SectionTitle,
  SectionContent,
  Content,
  Footer,
  FooterLeft,
  FooterStatus,
  FooterButtons,
  RestoreButton,
  SaveButton,
  AutoUpdateSection,
  AutoUpdateDescription,
  RuleSetsGrid,
  PerformanceGrid,
  LogsGrid,
} from './styles';

export function SuricataManagement() {
  const [autoDetectThreads, setAutoDetectThreads] = useState(16);
  const [autoUpdateEnabled, setAutoUpdateEnabled] = useState(true);
  const [updateFrequency, setUpdateFrequency] = useState('DIÁRIO');
  
  const [ruleSets, setRuleSets] = useState({
    emergingThreats: true,
    communityRules: true,
    customRules: false
  });

  const [workerThreads, setWorkerThreads] = useState(4);
  const [bufferSize, setBufferSize] = useState(1514);

  const [logs, setLogs] = useState({
    dns: true,
    http: true,
    tls: true,
    flow5: false
  });

  const toggleRuleSet = (ruleSetKey: keyof typeof ruleSets) => {
    setRuleSets(prev => ({
      ...prev,
      [ruleSetKey]: !prev[ruleSetKey]
    }));
  };

  const toggleLog = (logKey: keyof typeof logs) => {
    setLogs(prev => ({
      ...prev,
      [logKey]: !prev[logKey]
    }));
  };

  return (
    <Container>
      <Header>
        <HeaderTitle>MOTOR SURICATA</HeaderTitle>
        <ForceUpdateButton>
          <RotateCw size={16} />
          FORÇAR ATUALIZAÇÃO
        </ForceUpdateButton>
      </Header>

      <Content>

        {/* GERENCIAMENTO DE ASSINATURAS */}
        <Section>
          <SectionHeader>
            <FileSignature size={16} />
            <SectionTitle>GERENCIAMENTO DE ASSINATURAS</SectionTitle>
          </SectionHeader>
          <SectionContent>
            <AutoUpdateSection>
              <div>
                <SectionTitle>Atualização Automática de Regras</SectionTitle>
                <AutoUpdateDescription>
                  Manter a base de assinaturas sincronizada com os provedores.
                </AutoUpdateDescription>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <ToggleSwitch
                  checked={autoUpdateEnabled}
                  onChange={setAutoUpdateEnabled}
                />
                <RadioToggle
                  options={['DIÁRIO', 'SEMANAL']}
                  selected={updateFrequency}
                  onChange={setUpdateFrequency}
                />
              </div>
            </AutoUpdateSection>
          </SectionContent>
        </Section>

        {/* CONJUNTOS DE REGRAS */}
        <Section>
          <SectionHeader>
            <Shield size={16} />
            <SectionTitle>CONJUNTOS DE REGRAS</SectionTitle>
          </SectionHeader>
          <RuleSetsGrid>
            <RuleSetCard
              title="Emerging Threats"
              subtitle="ET OPEN RULESET"
              status="ATIVO"
              enabled={ruleSets.emergingThreats}
              onToggle={() => toggleRuleSet('emergingThreats')}
            />
            <RuleSetCard
              title="Community Rules"
              subtitle="OINKMASTER COMMUNITY"
              status="ATIVO"
              enabled={ruleSets.communityRules}
              onToggle={() => toggleRuleSet('communityRules')}
            />
            <RuleSetCard
              title="Custom Rules"
              subtitle="REGRAS PERSONALIZADAS"
              status="ATIVO"
              enabled={ruleSets.customRules}
              onToggle={() => toggleRuleSet('customRules')}
            />
          </RuleSetsGrid>
        </Section>

        {/* PERFORMANCE DO MOTOR */}
        <Section>
          <SectionHeader>
            <Cpu size={16} />
            <SectionTitle>PERFORMANCE DO MOTOR</SectionTitle>
          </SectionHeader>
          <SectionContent>
            <PerformanceGrid>
              <NumberInput
                label="NÚMERO DE THREADS DE WORKER"
                value={workerThreads}
                onChange={setWorkerThreads}
                autoDetectValue={autoDetectThreads}
                description="Recomendado: (nº de núcleos de CPU) menos 2."
                min={1}
                max={32}
              />
              <NumberInput
                label="TAMANHO DO BUFFER NTWRK"
                value={bufferSize}
                onChange={setBufferSize}
                description="Padrão Ethernet: 1514 bytes. Ajuste caso precise Frames de rede."
                min={512}
                max={9000}
              />
            </PerformanceGrid>
          </SectionContent>
        </Section>

        {/* LOGS EVE JSON */}
        <Section>
          <SectionHeader>
            <FileJson size={16} />
            <SectionTitle>LOGS EVE JSON</SectionTitle>
          </SectionHeader>
          <SectionContent>
            <LogsGrid>
              <LogToggle
                label="DNS LOGGING"
                checked={logs.dns}
                onChange={() => toggleLog('dns')}
              />
              <LogToggle
                label="HTTP LOGGING"
                checked={logs.http}
                onChange={() => toggleLog('http')}
              />
              <LogToggle
                label="TLS LOGGING"
                checked={logs.tls}
                onChange={() => toggleLog('tls')}
              />
              <LogToggle
                label="FLOW5 LOGGING"
                checked={logs.flow5}
                onChange={() => toggleLog('flow5')}
              />
            </LogsGrid>
          </SectionContent>
        </Section>

      </Content>

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
    </Container>
  );
}