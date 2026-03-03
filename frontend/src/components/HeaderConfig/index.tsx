import { useNavigate, useLocation } from 'react-router-dom';
//import {LogOut } from 'lucide-react'
import {
    ConfigContainer,
    LogoSection,
    SystemStatus,
    NavigationCenter,
    //ConsoleButton,
    ConsoleContainer,
    HeaderContainer,
    //Square,
    UserAvatar,
    DescriptionUser,
    NameUser,
    UserContent,
    UserContainer
} from './styles';

const routeNames: Record<string, string> = {
    '/settings/general': 'GERAL',
    '/settings/user': 'USUÁRIO',
    '/settings/suricata': 'MOTOR SURICATA',
    '/settings/ai-model': 'MODELO DE IA',
    '/settings/network': 'NETWORK',
    '/settings/notifications': 'NOTIFICAÇÕES',
    '/settings/relatorio': 'RELATORIO'
};

export function HeaderConfig() {
    const navigate = useNavigate();
    const location = useLocation();

    const currentName = routeNames[location.pathname] || '';

    return (
        <ConfigContainer>
            <HeaderContainer>
                <LogoSection>
                    <h1>AEGIS IDS <span>v4.0.2</span></h1>
                    <SystemStatus>
                        <span className="dot">●</span> SISTEMA OPERACIONAL
                    </SystemStatus>
                </LogoSection>

                <NavigationCenter>
                    <button onClick={() => navigate('/')}>DASHBOARD</button>
                    
                    {currentName && (
                        <>
                            <span className="separator"> &gt; </span>
                            <button onClick={() => navigate('/settings/general')}>
                                CONFIGURAÇÕES
                            </button>
                            <span className="separator"> &gt; </span>
                            <button className="current">{currentName}</button>
                        </>
                    )}
                </NavigationCenter>

                <ConsoleContainer>
                    <UserContainer>
                        <UserContent>
                            <NameUser>Julio Domingos</NameUser>
                            <DescriptionUser>ANALISTA DE SEGURANÇA</DescriptionUser>
                        </UserContent>
                        <UserAvatar>JD</UserAvatar>
                       
                    </UserContainer>
                    {/* <ConsoleButton>
                        <Square /> 
                        CONSOLE
                    </ConsoleButton> */}
                </ConsoleContainer>
            </HeaderContainer>
        </ConfigContainer>
    );
} 