import styled from "styled-components"
import { ClipboardList} from 'lucide-react';


export const ListIcon = styled(ClipboardList) `
    align-items: center;
    color: ${(props) => props.theme.colors.primary};
    width: 20px;   // largura do ícone
    height: 20px;
    margin-right: 8px;
`

export const LogContainer = styled.div `
    display: grid;
    grid-template-columns: repeat(4, 1fr); 
    gap: 1.5rem;
    width: 100%;
    margin-top: 1.5rem;
`


export const LogHeader = styled.div `
    display: flex;
    justify-content: space-between;
`
export const ButtonContainer = styled.div`
    display: flex;
    gap: 8px;
`;

export const LogsButton = styled.button `
    background-color: transparent;
    color: ${(props) => props.theme.colors.text.primary};
    border: 1px solid ${(props) => props.theme.colors.border};
    font-size: 15px;
    border-radius: 6px;
    display: inline-block;
    gap: 8px;
    align-items: center;
    font-weight: bold;
    cursor: pointer;
    padding: 4px 12px;
    transition: 0.2s;
    &:hover {
        color: ${(props) => props.theme.colors.text.secondary};
    }
`

export const HeaderTitle = styled.div `
    display: flex;
    align-items: center;
    justify-content: center;  
`
export const LogTitle = styled.div `
    font-size: 1rem;
    font-weight: bold;
    align-items: center;
`

export const LogSection = styled.div `
    grid-column: 1 / 4; /* 🔥 do 1º ao 3º card */
    background-color: ${(props) => props.theme.colors.surface};
    border-radius: 8px;
    padding: 1.5rem;
    overflow-y: auto;
    overflow-x: hidden;
`


export const Divider = styled.div`
  width: calc(100% + 48px); // 100% + padding left + right
  height: 1px;
  background-color: ${(props) => props.theme.colors.border};
  margin: 16px -24px; // negativo para compensar o padding
`;

const logColumns = `
  100px                     /* Timestamp */
  160px                     /* Origem */
  minmax(220px, 1fr)        /* Destino (flexível controlado) */
  130px                     /* Protocolo */
  120px                     /* Severidade */
  140px                     /* Ações */
`;



export const ListaMenu = styled.div`
  display: grid;
  grid-template-columns: ${logColumns};
  padding: 0px 16px;

  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  color: #9aa4ad;

`;



export const SidebarContainer = styled.div `
    display: block;
    background-color: ${(props) => props.theme.colors.surface};
    border-radius: 8px;
    padding: 1.5rem;
  /* height: 195px;  Dica: evite height fixo se o conteúdo puder crescer */
`;

export const SidebarTitle = styled.span `
    font-size: 12px;
    font-weight: bold;
    color: ${(props) => props.theme.colors.text.primary};
`

export const SidebarWrapper = styled.div`
  grid-column: 4 / 5; 
  display: flex;
  flex-direction: column;
  gap: 1.5rem; /* Ajuste aqui o espaçamento entre os dois containers */
`;

export const SidebarProcess = styled.div `
    display: block;
    margin-top: 20.5px;
`
export const ProcessFooter = styled.div `
    display: flex;
    margin-top: 1rem;
    justify-content: space-between;
    align-items: center;
    font-size: 9px;
`

export const ProcessBar = styled.div `
    
`

export const ProcessStatus = styled.span`
    font-size: 10px;
    color: ${(props) => props.theme.colors.success};
`

export const ProcessTitle = styled.span `
    font-size: 10px;
    color: ${(props) => props.theme.colors.text.secondary};
`

export const CoreContainer = styled.div `
    display: block;
    background-color: ${(props) => props.theme.colors.surface};
    border-radius: 8px;
    padding: 1.5rem;
`

export const CoreTitle = styled.span`
  font-size: 12px;
  font-weight: bold;
  color: ${(props) => props.theme.colors.text.secondary};
`

export const CoreMain = styled.div`
  background-color: ${(props) => props.theme.colors.background};
  padding: 12px 12px;
  margin-top: 1rem;
  border-radius: 4px;
`

export const CoreSection = styled.section`
    margin-top: 1rem;
    margin-top: 1rem;
    display: flex;
    gap: 0.75rem;
`

export const IniciaButton = styled.button`
  padding: 0rem 0.5rem;
  border-radius: 8px;
  border: none;

  background-color: ${(props) => props.theme.colors.success};
  color: #ffffff;

  font-size: 0.9rem;
  font-weight: 600;

  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background-color: ${(props) => props.theme.colors.success};
  }

  &:active {
    transform: scale(0.97);
  }
`;

export const PausarButton = styled.button`
  padding: 0rem 0.5rem;
  border-radius: 8px;
  border: none;

  background-color: ${(props) => props.theme.colors.warning};
  color: #1f2937;

  font-size: 0.9rem;
  font-weight: 600;

  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background-color: ${(props) => props.theme.colors.warning};
  }

  &:active {
    transform: scale(0.97);
  }
`;

export const ReporButton = styled.button`
  padding: 0.5rem 0.5rem;
  border-radius: 8px;
  border: none;

  background-color: ${(props) => props.theme.colors.danger};
  color: ${(props) => props.theme.colors.text.primary};

  font-size: 0.9rem;
  font-weight: 600;

  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background-color: ${(props) => props.theme.colors.danger};
  }

  &:active {
    transform: scale(0.97);
  }
`;

export const CoreSubTitle = styled.span `
    font-size: 10px;
    color: ${(props) => props.theme.colors.text.primary};
`

export const CoreStatus = styled.span `
    color: ${(props) => props.theme.colors.success};
`

export const CoreMode = styled.div `
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 9px;
`