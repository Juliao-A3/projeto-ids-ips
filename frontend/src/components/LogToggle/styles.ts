import styled from 'styled-components';

export const Container = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: ${(props) => props.theme.colors.surface};
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 6px;
  transition: all 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.04);
    border-color: ${(props) => props.theme.colors.primary};
  }
`;

export const Label = styled.span`
  font-size: 13px;
  font-weight: 600;
  color: ${(props) => props.theme.colors.text.primary};
  text-transform: uppercase;
  letter-spacing: 0.3px;
`;