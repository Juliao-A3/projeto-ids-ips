import { NavLink } from 'react-router-dom';
import styled from 'styled-components';


export const SidebarContainer = styled.aside`
  position: fixed;
  top: 60px;
  left: 0;

  width: 240px;
  height: calc(100vh - 60px);
  background-color: ${(props) => props.theme.colors.surface}; 
  border-right: 1px solid ${(props) => props.theme.colors.border};
  height: calc(100vh - 60px); 
  display: flex;
  z-index: 90;
  flex-direction: column;
  padding-top: 16px;
`;

export const NavItem = styled(NavLink)`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
  color: ${(props) => props.theme.colors.text.secondary};
  border-left: 4px solid transparent;
  transition: all 0.2s ease;

  &.active {
    color: ${(props) => props.theme.colors.primary};
    background-color: rgba(0, 153, 255, 0.1);
    border-left: 4px solid #0099ff;
  }

  &:hover:not(.active) {
    background-color: ${(props) => props.theme.colors.border};
  }
`;

export const StatusFooter = styled.div`
  margin-top: auto;
  padding: 20px;
  border-top: 1px solid ${(props) => props.theme.colors.border};
  font-size: 10px;
  color: ${(props) => props.theme.colors.text.secondary};

  .label {
    margin-bottom: 8px;
    display: block;
  }

  .progress-bar {
    height: 4px;
    background: #21262d;
    border-radius: 2px;
    overflow: hidden;
    margin-bottom: 5px;
    
    .fill {
      height: 100%;
      width: 85%; 
      background: #00a3ff;
    }
  }
`;