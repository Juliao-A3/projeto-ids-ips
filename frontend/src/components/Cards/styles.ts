import styled from "styled-components"

export const CardContainer = styled.div`
    display: grid; 

    color: ${(props) => props.theme.colors.text.primary};
    
    background-color: ${(props) => props.theme.colors.background};
    width: 100%;

    margin-top: 1rem;

    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
`;


export const CardContent = styled.div`
  border: 1px solid ${(props) => props.theme.colors.border};
  
  background-color: ${(props) => props.theme.colors.surface};

  border-radius: 14px;
  padding: 1.25rem;

  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1.5rem;

  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  }
`;

export const CardTitle = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;

  font-size: 0.85rem;
  font-weight: 500;

  color: ${(props) => props.theme.colors.text.secondary};
`;

export const CardInfo = styled.div`
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
`;

export const CardNum = styled.span<{ $isActive?: boolean }>`
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1;

  color: ${(props) => {
    if (props.$isActive === true) return '#00ff00';
    if (props.$isActive === false) return '#ff0000';
    return props.theme.colors.text.primary;
  }};
  
  text-shadow: ${(props) => {
    if (props.$isActive === true) return '0 0 8px rgba(0, 255, 0, 0.5)';
    if (props.$isActive === false) return '0 0 8px rgba(255, 0, 0, 0.5)';
    return 'none';
  }};
  
  transition: all 0.3s ease;
`;


export const CardSubtitle = styled.div`
  font-size: 0.8rem;
  font-weight: 400;

  color: ${(props) => props.theme.colors.text.muted};
`;
