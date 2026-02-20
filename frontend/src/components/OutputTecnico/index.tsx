import { 
    OutputContainer,
    OutputHeader,
    OutputTitle,
    OutputBody,
    LogLine,
    LogTime,
    LogLevel,
    LogMessage,
    Main,
  } from "./styles";
  
export function OutputTecnico() {
    return (
        <Main>  
        <OutputContainer>
            <OutputHeader>
            <OutputTitle>OUTPUT TÉCNICO DE KERNEL</OutputTitle>
            </OutputHeader>
    
            <OutputBody>
            <LogLine>
                <LogTime>[15:30:44]</LogTime>
                <LogLevel type="system">[SYSTEM]</LogLevel>
                <LogMessage>
                Suricata 7.0.2 iniciado com sucesso. Todos os módulos operantes.
                </LogMessage>
            </LogLine>
    
            <LogLine>
                <LogTime>[15:30:45]</LogTime>
                <LogLevel type="info">[INFO]</LogLevel>
                <LogMessage>
                Carregando base de assinaturas (Total: 24.110 regras).
                </LogMessage>
            </LogLine>
    
            <LogLine>
                <LogTime>[15:30:46]</LogTime>
                <LogLevel type="warn">[WARN]</LogLevel>
                <LogMessage>
                Aceleração via hardware eBPF habilitada para interface eth0.
                </LogMessage>
            </LogLine>
            </OutputBody>
        </OutputContainer>
        </Main>
    );
}
  