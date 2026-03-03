import styled from "styled-components"
import { Terminal } from 'lucide-react';

export const HeaderContainer = styled.div`
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 60px;
    padding: 0 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: ${({ theme }) => theme.colors.surface}; 
    color: ${(props) => props.theme.colors.text.primary};
    border-bottom: 1px solid ${({ theme }) => theme.colors.border};
    z-index: 1000;
`;

export const ConfigContainer = styled.div `
  position: fixed;
  top: 60px;
  left: 0;
  z-index: 50;
  width: 240px;
  height: calc(100vh - 60px);

  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
`

export const LogoSection = styled.div `
    display: flex;
    flex-direction: column;
    h1 {
        font-size: 20px;
        margin: 0;
        letter-spacing: 0.5px;
        font-weight: 800;
        span {
            font-weight: 300;
            font-size: 15px;
        }
    }
`

export const SystemStatus = styled.span `
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 9px;
    
    font-weight: bold;
    margin-top: 2px;
    color: ${(props) => props.theme.colors.success};
    
    &::before {
    content: '';
    width: 6px;
    height: 6px;
    background-color: ${(props) => props.theme.colors.success};
    border-radius: 50%;
  }
`

export const NavigationCenter = styled.div`
    display: flex;
    align-items: center;
    gap: 8px;
    
    position: absolute;
    left: 50%;
    transform: translateX(-50%);

    span.separator {
        font-size: 12px;
        color: ${({ theme }) => theme.colors.text.primary};
        user-select: none;
    }

    button {
        background: none;
        border: none;
        padding: 0;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        color: ${({ theme }) => theme.colors.text.secondary};
         
        cursor: pointer;
        transition: color 0.2s;
        text-transform: uppercase;

        &:hover {
            color: ${({ theme }) => theme.colors.text.primary};
        }

        &.current {
            color: ${({ theme }) => theme.colors.primary};
            cursor: default;
        }
    }
`;
export const ConsoleButton = styled.div `
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid ${(props) => props.theme.colors.border};
    color: white;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.2s;

    &:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: ${(props) => props.theme.colors.border};
    }
`
export const ConsoleContainer = styled.div `
    display: flex;  
    align-items: center;
`

export const Square = styled(Terminal) `
    width: 15px;
`

export const UserAvatar = styled.div `
    width: 36px;
    height: 36px;
    border-radius: 15%;
    background: ${(props) => props.theme.colors.primary};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 600;
    margin-right: 0.5rem;
    color: ${(props) => props.theme.colors.text.primary};
`

export const DescriptionUser = styled.h3 `
    font-size: 8px;
    color: ${(props) => props.theme.colors.text.secondary};
`

export const NameUser = styled.h2 `
    font-size: 12px;
    align-items: center;
    color: ${(props) => props.theme.colors.text.primary};
`

export const UserContent = styled.div `
    display: block;
    margin-right: 8px;
`

export const UserContainer = styled.div `
    align-items: center;
    display: flex;
    padding: 24px;
    button {
        border: none;
        cursor: pointer;
        background-color: ${(props) => props.theme.colors.surface};
    }
`