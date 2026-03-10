import { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
    ConfigContainer, LogoSection, SystemStatus,
    NavigationCenter, ConsoleContainer, HeaderContainer,
    UserAvatar, DescriptionUser, NameUser, UserContent,
    UserContainer, RoleBadge, DropdownMenu, DropdownHeader,
    DropdownAvatar, DropdownUserInfo, DropdownName,
    DropdownSeparator, DropdownItem
} from './styles';

import { ChangePasswordModal } from "../ChangePasswordModal/index";

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
    const { user, logout } = useAuth();
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    const currentName = routeNames[location.pathname] || '';
    const [passwordModalOpen, setPasswordModalOpen] = useState(false);

    // fecha dropdown ao clicar fora
    useEffect(() => {
        function handleClickOutside(e: MouseEvent) {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
                setDropdownOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

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
                            <button onClick={() => navigate('/settings/user')}>
                                CONFIGURAÇÕES
                            </button>
                            <span className="separator"> &gt; </span>
                            <button className="current">{currentName}</button>
                        </>
                    )}
                </NavigationCenter>

                <ConsoleContainer>
                    {/* UserContainer com dropdown */}
                    <UserContainer
                        ref={dropdownRef}
                        onClick={() => setDropdownOpen(v => !v)}
                    >
                        <UserContent>
                            <NameUser>{user?.name}</NameUser>
                            <DescriptionUser>{user?.role}</DescriptionUser>
                        </UserContent>
                        <UserAvatar>{user?.initials}</UserAvatar>

                        {/* Dropdown */}
                        <DropdownMenu $open={dropdownOpen}>

                            {/* Cabeçalho com info do utilizador */}
                            <DropdownHeader>
                                <DropdownAvatar>{user?.initials}</DropdownAvatar>
                                <DropdownUserInfo>
                                    <DropdownName>{user?.name}</DropdownName>
                                    <RoleBadge>NÍVEL: {user?.role}</RoleBadge>
                                </DropdownUserInfo>
                            </DropdownHeader>

                            <DropdownSeparator />

                            {/* Ver Perfil */}
                            <DropdownItem onClick={(e) => {
                                e.stopPropagation();
                                navigate('/settings/profile');
                                setDropdownOpen(false);
                            }}>
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                                    <circle cx="12" cy="8" r="4" />
                                    <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" />
                                </svg>
                                VER PERFIL
                            </DropdownItem>

                            {/* Alterar Senha */}
                            <DropdownItem onClick={(e) => {
                                e.stopPropagation();
                                setPasswordModalOpen(true);
                                setDropdownOpen(false);
                                }}>
                                ALTERAR SENHA
                                </DropdownItem>


                            <DropdownSeparator />

                            {/* Logout */}
                            <DropdownItem $danger onClick={(e) => {
                                e.stopPropagation();
                                logout();
                                navigate('/login', { replace: true });
                            }}>
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                                    <polyline points="16 17 21 12 16 7" />
                                    <line x1="21" y1="12" x2="9" y2="12" />
                                </svg>
                                TERMINAR SESSÃO
                            </DropdownItem>

                        </DropdownMenu>
                    </UserContainer>
                            {passwordModalOpen && (
                                <ChangePasswordModal onClose={() => setPasswordModalOpen(false)} />
                            )}
                </ConsoleContainer>
            </HeaderContainer>
        </ConfigContainer>
    );
}