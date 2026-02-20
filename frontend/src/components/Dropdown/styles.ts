import styled from 'styled-components';

export const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

export const Label = styled.label`
  font-size: 12px;
  font-weight: 600;
  color: ${(props) => props.theme.colors.text.secondary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

export const SelectWrapper = styled.div`
  position: relative;
  display: flex;
  align-items: center;

  svg {
    position: absolute;
    right: 16px;
    pointer-events: none;
    color: ${(props) => props.theme.colors.text.secondary};
  }
`;

export const Select = styled.select`
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 6px;
  padding: 12px 40px 12px 16px;
  font-size: 14px;
  font-weight: 500;
  color: ${(props) => props.theme.colors.text.primary};
  cursor: pointer;
  transition: all 0.2s;
  appearance: none;

  &:focus {
    outline: none;
    border-color: ${(props) => props.theme.colors.primary};
    background: rgba(255, 255, 255, 0.08);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  option {
    background: ${(props) => props.theme.colors.surface};
    color: ${(props) => props.theme.colors.text.primary};
    padding: 8px;
  }
`;

export const Description = styled.p`
  font-size: 11px;
  color: ${(props) => props.theme.colors.text.secondary};
  margin: 0;
  line-height: 1.4;
`;