import styled from 'styled-components';

export const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  height: 100%;
`;

export const Label = styled.label`
  font-size: 12px;
  font-weight: 600;
  color: ${(props) => props.theme.colors.text.secondary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

export const StyledTextArea = styled.textarea`
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 6px;
  padding: 12px 16px;
  font-size: 13px;
  font-family: 'Consolas', 'Monaco', monospace;
  color: ${(props) => props.theme.colors.text.primary};
  resize: vertical;
  transition: all 0.2s;

  &:focus {
    outline: none;
    border-color: ${(props) => props.theme.colors.primary};
    background: rgba(255, 255, 255, 0.08);
  }

  &::placeholder {
    color: ${(props) => props.theme.colors.text.secondary};
    opacity: 0.5;
  }
`;

export const Description = styled.p`
  font-size: 11px;
  color: ${(props) => props.theme.colors.text.secondary};
  margin: 0;
  line-height: 1.4;
`;