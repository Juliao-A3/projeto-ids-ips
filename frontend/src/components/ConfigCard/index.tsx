import {
    Container,
    Grid,
    Section,
    SectionTitle,
} from './styles';

import { MdSettingsInputComponent } from 'react-icons/md';
import { SettingSwitch } from '../PainelConfiguracoes';


export function ConfigGeral() {
  return (
    <Container>
      <Section>
        <SectionTitle>
          <MdSettingsInputComponent />
          CONFIGURAÇÕES DO SISTEMA
        </SectionTitle>

        <Grid>
          <SettingSwitch 
            title="Modo de Prevenção (IPS)"
            description="Bloqueio ativo de ameaças detectadas em tempo real."
            onSave={(val) => console.log("IPS alterado para:", val)}
          />

          <SettingSwitch 
            title="Auto-bloqueio de IPs"
            description="Banimento automático de fontes com alto score de risco."
            onSave={(val) => console.log("Auto-block alterado para:", val)}
          />

          <SettingSwitch 
            title="Análise Profunda (DPI)"
            description="Inspeção detalhada do payload de pacotes (SSL/TLS)."
          />
        </Grid>
      </Section>

    </Container>
  );
}