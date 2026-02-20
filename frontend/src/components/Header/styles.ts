import styled from "styled-components";

export const SubtitleContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  color: ${(props) => props.theme.colors.success};

  > span:first-child {
    font-size: 20px;
    line-height: 1;
  }
`;

export const StatusText = styled.span`
  font-size: 14px;
  color: ${(props) => props.theme.colors.success};
  font-weight: bold;
`;

export const HeaderContainer = styled.header`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 64px;
  padding: 0 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  background-color: ${({ theme }) => theme.colors.surface};
  color: ${({ theme }) => theme.colors.text.primary};
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
`;

export const HeaderContent = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  max-width: 1400px;
`;

export const HeaderLeft = styled.div`
  display: block;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;

  > div:first-child {
    display: flex;
    align-items: center;
    gap: 6px;

    h1 {
      color: ${(props) => props.theme.colors.text.primary};
      font-size: 20px;
      margin: 0;
      font-weight: 800;
      letter-spacing: 0.5px;
    }

    span {
      color: ${(props) => props.theme.colors.text.secondary};
      font-size: 15px;
      font-weight: 500;
    }
  }
`;

export const HeaderCenter = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  margin: 0 32px;
`;

export const Metric = styled.div`
  display: flex;
  align-items: center;
`;

export const StatusInfo = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  min-width: 80px;
`;

export const CpuPorcent = styled.span`
  color: ${(props) => props.theme.colors.success};
  font-size: 14px;
  font-weight: 600;
  line-height: 1;
`;

export const Loadcpu = styled.span`
  font-size: 10px;
  color: ${(props) => props.theme.colors.text.secondary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
`;

export const SpeedStatus = styled.div`
  font-size: 14px;
  color: ${(props) => props.theme.colors.text.primary};
  font-weight: 600;
  line-height: 1;
`;

export const AlertConfig = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
`;

export const ConfigButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 600;
  padding: 10px 16px;
  border-radius: 6px;
  border: 1px solid ${(props) => props.theme.colors.border};
  background-color: transparent;
  color: ${(props) => props.theme.colors.text.secondary};
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.5px;

  &:hover {
    background-color: ${(props) => props.theme.colors.surface};
    color: ${(props) => props.theme.colors.text.primary};
    border-color: ${(props) => props.theme.colors.primary};
  }
`;

export const RelatorioButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 600;
  padding: 10px 16px;
  border-radius: 6px;
  border: none;
  background-color: ${(props) => props.theme.colors.primary};
  color: ${(props) => props.theme.colors.text.primary};
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.5px;

  &:hover {
    opacity: 0.85;
    transform: translateY(-1px);
  }
`;

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
`