import styled from "styled-components";

export const Main = styled.main `
    width: 100%;
`


export const OutputContainer = styled.section`
    margin-top: 1.5rem;
    background: linear-gradient(180deg, #0b1220, #070d18);
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.05);
`;

export const OutputHeader = styled.div`
  padding: 1rem 1.5rem;
  background-color: ${(props) => props.theme.colors.surface};
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
`;

export const OutputTitle = styled.h3`
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 1px;
  color: ${(props) => props.theme.colors.text.secondary};
`;

export const OutputBody = styled.div`
  max-height: 200px;
  padding: 0.75rem 1rem;

  overflow-y: auto;

  font-family: "JetBrains Mono", monospace;
  font-size: 0.75rem;
`;

export const LogLine = styled.div`
  display: flex;
  gap: 0.5rem;
  line-height: 1.6;
`;

export const LogTime = styled.span`
  color: #64748b;
`;

export const LogLevel = styled.span<{ type: "system" | "info" | "warn" }>`
  font-weight: 600;

  ${({ type }) =>
    type === "system" &&
    `
      color: #22c55e;
    `}

  ${({ type }) =>
    type === "info" &&
    `
      color: #38bdf8;
    `}

  ${({ type }) =>
    type === "warn" &&
    `
      color: #facc15;
    `}
`;

export const LogMessage = styled.span`
  color: ${(props) => props.theme.colors.text.primary};
`;
