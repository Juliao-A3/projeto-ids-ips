import { useState } from 'react';
import { Activity, GitBranch, Shield, Zap } from 'lucide-react';
import { NetworkInterfacesTable } from '../NetworkInterfacesTable';
import { ToggleSwitch } from '../ToggleSwitch';
import { Dropdown } from '../Dropdown';
import { TextArea } from '../TextArea';
import {
  Container,
  Content,
  Section,
  SectionHeader,
  SectionTitle,
  SectionContent,
  BridgeConfig,
  BridgeDescription,
  BridgeSettings,
  BridgeToggles,
  DropdownsGrid,
  TwoColumnsWrapper,
  PerformanceItem,
  PerformanceLabel,
  PerformanceValue,
  PerformanceGrid,
  Footer,
  FooterButtons,
  RestoreButton,
  SaveButton
} from './styles';

export function NetworkManagement() {
  const [bridgeEnabled, setBridgeEnabled] = useState(true);
  const [internalInterface, setInternalInterface] = useState('eth1');
  const [externalInterface, setExternalInterface] = useState('eth0');
  
  // Whitelist
  const [whitelist, setWhitelist] = useState('192.168.1.0/24, 10.0.0.0/8, 127.0.0.1');
  
  // Performance
  const [promiscuousMode, setPromiscuousMode] = useState(true);

  const interfaceOptions = [
    { value: 'eth0', label: 'eth0' },
    { value: 'eth1', label: 'eth1' },
    { value: 'wlan0', label: 'wlan0' }
  ];

  return (
    <Container>
      <Content>
        <Section>
          <SectionHeader>
            <Activity size={16} />
            <SectionTitle>INTERFACES DE MONITORAMENTO</SectionTitle>
          </SectionHeader>
          <SectionContent>
            <NetworkInterfacesTable />
          </SectionContent>
        </Section>

        <Section>
          <SectionHeader>
            <GitBranch size={16} />
            <SectionTitle>CONFIGURAÇÃO DE BRIDGE</SectionTitle>
          </SectionHeader>
          <SectionContent>
            <BridgeConfig>
              <BridgeSettings>
                <div>
                  <h3 style={{ 
                    margin: '0 0 8px 0', 
                    fontSize: '14px', 
                    fontWeight: 600 
                  }}>
                    MODO INLINE (IPS BRIDGE)
                  </h3>
                  <BridgeDescription>
                    Interliga o Motor Suricata entre duas interfaces de rede para 
                    inspeção em linha (bloqueio físico).
                  </BridgeDescription>
                </div>
                <BridgeToggles>
                  <ToggleSwitch
                    checked={bridgeEnabled}
                    onChange={setBridgeEnabled}
                  />
                </BridgeToggles>
              </BridgeSettings>

              <DropdownsGrid>
                <Dropdown
                  label="INTERFACE INTERNA (LAN)"
                  value={internalInterface}
                  onChange={setInternalInterface}
                  options={interfaceOptions}
                  disabled={!bridgeEnabled}
                />
                <Dropdown
                  label="INTERFACE EXTERNA (WAN)"
                  value={externalInterface}
                  onChange={setExternalInterface}
                  options={interfaceOptions}
                  disabled={!bridgeEnabled}
                />
              </DropdownsGrid>
            </BridgeConfig>
          </SectionContent>
        </Section>

        <TwoColumnsWrapper>
          <Section>
            <SectionHeader>
              <Shield size={16} />
              <SectionTitle>LISTA BRANCA (WHITELIST)</SectionTitle>
            </SectionHeader>
            <SectionContent>
              <TextArea
                label="IPS CONFIÁVEIS / REDES LOCAIS"
                value={whitelist}
                onChange={setWhitelist}
                placeholder="Ex: 192.168.1.0/24, 10.0.0.0/8, 127.0.0.1"
                description="Separe cada endereço ou subrede por ponto-vírgula. Esses recursos não passarão pelo Motor."
                rows={10}
              />
            </SectionContent>
          </Section>

          <Section>
            <SectionHeader>
              <Zap size={16} />
              <SectionTitle>PERFORMANCE E OTIMIZAÇÃO</SectionTitle>
            </SectionHeader>
            <SectionContent>
              <BridgeConfig>
                <BridgeSettings>
                  <div>
                    <h3 style={{ 
                      margin: '0 0 8px 0', 
                      fontSize: '14px', 
                      fontWeight: 600 
                    }}>
                      MODO PROMÍSCUO
                    </h3>
                    <BridgeDescription>
                      Captura todos os pacotes que passam pela interface física.
                    </BridgeDescription>
                  </div>
                  <BridgeToggles>
                    <ToggleSwitch
                      checked={promiscuousMode}
                      onChange={setPromiscuousMode}
                    />
                  </BridgeToggles>
                </BridgeSettings>

                <PerformanceGrid>
                  <PerformanceItem>
                    <PerformanceLabel>OTIMIZAÇÃO DE MTU</PerformanceLabel>
                    <PerformanceValue>1500 bytes</PerformanceValue>
                  </PerformanceItem>
                  <PerformanceItem>
                    <PerformanceLabel>PADRÃO (DMA)</PerformanceLabel>
                    <PerformanceValue>JUMBO FRAMES (9000)</PerformanceValue>
                  </PerformanceItem>
                </PerformanceGrid>
              </BridgeConfig>
            </SectionContent>
          </Section>
        </TwoColumnsWrapper>
      </Content>

      <Footer>
        <FooterButtons>
          <RestoreButton>RESTAURAR PADRÕES</RestoreButton>
          <SaveButton>SALVAR ALTERAÇÕES</SaveButton>
        </FooterButtons>
      </Footer>
    </Container>
  );
}