import { useState } from "react";
import { CheckboxGroup, CheckboxLabel, ControlsRow, FormGroup, Header, InputGrid, Label, LogIntegrationWrapper, StyledInput, TestButton } from "./styles";
interface LogConfig {
  syslog: string;
  siem: string;
  tls: boolean;
  json: boolean;
}

export function LogIntegration() {
        const [config, setConfig] = useState<LogConfig>({
          syslog: 'udp://10.0.1.200:514',
          siem: 'https://api.siem-service.com/v1/ingest',
          tls: true,
          json: false
        });
      
        const handleChange = (e: { target: { name: any; value: any; type: any; checked: any; }; }) => {
          const { name, value, type, checked } = e.target;
          setConfig(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
          }));
        };      
    return (
        <LogIntegrationWrapper>
          <Header>
            <span>🌐</span> INTEGRAÇÃO DE LOGS
          </Header>
    
          <InputGrid>
            <FormGroup>
              <Label>Remote Syslog Endpoint</Label>
              <StyledInput 
                name="syslog"
                value={config.syslog} 
                onChange={handleChange}
              />
            </FormGroup>
            <FormGroup>
              <Label>SIEM API Endpoint</Label>
              <StyledInput 
                name="siem"
                value={config.siem} 
                onChange={handleChange}
              />
            </FormGroup>
          </InputGrid>
    
          <ControlsRow>
            <CheckboxGroup>
              <CheckboxLabel>
                <input 
                  type="checkbox" 
                  name="tls"
                  checked={config.tls} 
                  onChange={handleChange}
                /> TLS Encryption
              </CheckboxLabel>
              <CheckboxLabel>
                <input 
                  type="checkbox" 
                  name="json"
                  checked={config.json} 
                  onChange={handleChange}
                /> JSON Format
              </CheckboxLabel>
            </CheckboxGroup>
    
            <TestButton onClick={() => alert('Testando conexão...')}>
              TESTAR CONEXÃO
            </TestButton>
          </ControlsRow>
        </LogIntegrationWrapper>
    );
}