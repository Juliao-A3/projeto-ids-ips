import styled from "styled-components";

interface SwitchProps {
    $isActive: boolean;
}

export const Card = styled.div`
  background-color: ${(props) => props.theme.colors.surface};
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 6px; 
  padding: 24px;
  display: flex;
  flex-direction: column;
  height: 100%;
`;

export const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;

  strong {
    font-size: 13px;
    color: ${(props) => props.theme.colors.text.primary};
    text-transform: none; 
  }
`;

export const CardContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;

  span {
    font-size: 11px;
    color: ${(props) => props.theme.colors.text.secondary};
    line-height: 1.5;
  }  
`;

export const Switch = styled.div<SwitchProps>`
  width: 34px;
  height: 18px;
  border-radius: 10px;
  position: relative;
  cursor: pointer;
  transition: 0.3s;

  background-color: ${(props) => 
    props.$isActive ? '#00a2ff' : '#333'};

  &::after {
    content: '';
    position: absolute;
    width: 14px;
    height: 14px;
    background-color: white;
    border-radius: 50%;
    top: 2px;
    transition: 0.3s;
    
    left: ${(props) => (props.$isActive ? '18px' : '2px')};
  }
`;