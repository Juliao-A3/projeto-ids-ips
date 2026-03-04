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



import { useEffect, useState } from 'react';
import { api } from '../../services/api';

export function LogCard() {
    const [logs, setLogs] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const resp = await api.get('/monitor/logs?limit=10');
                setLogs(resp.data);
            } catch (err) {
                console.error('Erro ao buscar logs:', err);
            } finally {
                setLoading(false);
            }
        };
        fetchLogs();
        const interval = setInterval(fetchLogs, 15000);
        return () => clearInterval(interval);
    }, []);

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
                {loading ? (
                    <div>Carregando logs...</div>
                ) : logs.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '2rem' }}>
                        Nenhum tráfego registrado ainda
                    </div>
                ) : (
                    logs.map(l => (
                        <LogInfo key={l.id} data={l} />
                    ))
                )}
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
