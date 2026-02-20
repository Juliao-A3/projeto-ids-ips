//import { Sidebar } from 'lucide-react';
import { LogInfo } from '../LogInfo';
import TrafficIntegrityStatus from '../TrafficIntegrityStatus';
import {
    LogContainer,
    LogHeader,
    LogsButton,
    HeaderTitle,
    LogTitle,
    ButtonContainer,
    LogSection,
    SidebarContainer,
    ListIcon,
    Divider,
    ListaMenu,
    SidebarTitle,
    SidebarProcess,
    SidebarWrapper,
    ProcessFooter,
    ProcessBar,
    ProcessStatus,
    ProcessTitle,
    CoreTitle,
    CoreMain,
    CoreSection,
    IniciaButton,
    PausarButton,
    ReporButton,
    CoreSubTitle,
    CoreStatus,
    CoreContainer,
    CoreMode,
} from './styles'



export function LogCard() {
    return (
        <LogContainer>

            <LogSection>

                <LogHeader>
                    <HeaderTitle>
                        <ListIcon/>
                        <LogTitle>
                            LOGS EM TEMPO REAL
                        </LogTitle>
                    </HeaderTitle>
                    <ButtonContainer>
                        <LogsButton>FILTROS</LogsButton>
                        <LogsButton>EXPORTAR CSV</LogsButton>
                    </ButtonContainer>
                </LogHeader>

                <Divider/>

                <ListaMenu>
                    <span>Timestamp</span>
                    <span>Origem</span>
                    <span>Destino</span>
                    <span>Protocolo</span>
                    <span>Severidade</span>
                    <span>Ações</span>
                </ListaMenu>

                <Divider/>
                <LogInfo/>
                <LogInfo/>
            </LogSection>

            <SidebarWrapper>
                <SidebarContainer>
                    <TrafficIntegrityStatus />
                </SidebarContainer>

                <CoreContainer>
                    <CoreTitle>Controles Core</CoreTitle>
                    <CoreMain>
                        <CoreMode>
                            <CoreSubTitle>MODO IDS/IPS</CoreSubTitle>
                            <CoreStatus>ESTAVEL</CoreStatus>
                        </CoreMode>
                        <CoreSection>
                            <IniciaButton>Iniciar</IniciaButton>
                            <PausarButton>Pausar</PausarButton>
                            <ReporButton>Reboot</ReporButton>
                        </CoreSection>
                    </CoreMain>
                </CoreContainer>
                
            </SidebarWrapper>
        </LogContainer>
    );
}
