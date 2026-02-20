import styled from "styled-components";


const logColumns = `
  100px                     /* Timestamp */
  160px                     /* Origem */
  minmax(220px, 1fr)        /* Destino (flexível controlado) */
  130px                     /* Protocolo */
  120px                     /* Severidade */
  140px                     /* Ações */
`;

export const LogContainer = styled.div `

`

export const LogMain = styled.div `
    width: 100%;
    overflow-x: hidden;
`

export const LogContent = styled.div `
`

export const LogRow = styled.div`
  position: relative; /* necessário para o pseudo-elemento */
  display: grid;
  grid-template-columns: ${logColumns};
  padding: 0px 16px;

  font-size: 13px;
  color: #e5e7eb;

  span {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
`;


export const Severity = styled.span<{ level?: string }>`
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  width: fit-content;

  background: ${({ level }) =>
    level === "INFO" ? "#123c2a" :
    level === "BAIXA" ? "#2f2f2f" :
    "#402020"};

  color: ${({ level }) =>
    level === "INFO" ? "#22c55e" :
    level === "BAIXA" ? "#a3a3a3" :
    "#ef4444"};
`;

export const Actions = styled.div`
  display: flex;
  gap: 6px;

  button {
    background: #111827;
    border: 1px solid #1f2933;
    color: #cbd5e1;
    font-size: 11px;
    padding: 4px 8px;
    border-radius: 4px;
    cursor: pointer;

    &:hover {
      background: #1f2933;
    }
  }
`;

export const Divider = styled.div`
  width: calc(100% + 48px); // 100% + padding left + right
  height: 1px;
  background-color: ${(props) => props.theme.colors.border};
  margin: 16px -24px; // negativo para compensar o padding
`;