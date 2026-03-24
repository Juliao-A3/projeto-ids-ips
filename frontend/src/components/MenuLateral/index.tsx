import React from 'react';
import { 
  MdPsychology, MdHub, 
  MdNotifications, MdAssessment, 
  MdPerson
} from 'react-icons/md';
import { NavItem, SidebarContainer, StatusFooter } from './styles';

const MENU_ITEMS = [
  //{ label: 'GERAL', path: '/settings/general', icon: <MdSettings size={18}/> },
  { label: 'USUÁRIO', path: '/settings/user', icon: <MdPerson size={18}/> },
  // { label: 'MOTOR SURICATA', path: '/settings/suricata', icon: <MdDns size={18}/> },
  { label: 'MODELO DE IA', path: '/settings/ai-model', icon: <MdPsychology size={18}/> },
  { label: 'REDE', path: '/settings/network', icon: <MdHub size={18}/> },
  { label: 'ANÁLISE ESTÁTICA', path: '/settings/analise', icon: <MdAssessment size={18}/> },
  { label: 'GESTÃO DE IA', path: '/settings/gestao-ia', icon: <MdPsychology size={18}/> },
  { label: 'NOTIFICAÇÕES', path: '/settings/notifications', icon: <MdNotifications size={18}/> },
  { label: 'RELATORIO', path: '/settings/relatorio', icon: <MdAssessment size={18}/>}
];

export const MenuLateral: React.FC = () => {
  return (
    <SidebarContainer>
      {MENU_ITEMS.map((item) => (
        <NavItem key={item.path} to={item.path}>
          {item.icon}
          {item.label}
        </NavItem>
      ))}

      <StatusFooter>
        <span className="label">STATUS DA CONFIGURAÇÃO</span>
        <div className="progress-bar">
          <div className="fill" style={{ width: '85%' }}></div>
        </div>
        <span style={{ fontSize: '9px' }}>85% das otimizações aplicadas</span>
      </StatusFooter>
    </SidebarContainer>
  );
};