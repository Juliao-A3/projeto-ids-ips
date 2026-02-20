import styled from 'styled-components';

export const LogIntegrationWrapper = styled.section`
  max-width: 1220px;
  width: 100%;
  margin: auto 0;
  padding: 24px;
  margin-top: -1.5rem;
  color: ${(props) => props.theme.colors.text.primary};
  font-family: 'Inter', sans-serif;
`;

export const Header = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  color: ${(props) => props.theme.colors.primary}; 
  border-bottom: 1px solid ${(props) => props.theme.colors.border};
  font-size: 14px;
  padding-bottom: 1.5rem;
  font-weight: bold;
  text-transform: uppercase;
`;

export const InputGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
  padding: 24px;
  border-radius: 6px;
  background-color: ${(props) => props.theme.colors.surface};
`;

export const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

export const Label = styled.label`
  font-size: 0.75rem;
  color: ${(props) => props.theme.colors.text.secondary};
  text-transform: uppercase;
`;

export const StyledInput = styled.input`
  background-color: ${(props) => props.theme.colors.background};
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 4px;
  padding: 12px;
  color: ${(props) => props.theme.colors.text.primary};
  font-size: 0.85rem;

  &:focus {
    outline: none;
    border-color: ${(props) => props.theme.colors.success};
  }
`;

export const ControlsRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

export const CheckboxGroup = styled.div`
  display: flex;
  gap: 20px;
`;

export const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  color: ${(props) => props.theme.colors.text.secondary};
  cursor: pointer;

  input {
    accent-color: ${(props) => props.theme.colors.primary};
  }
`;

export const TestButton = styled.button`
  background-color: transparent;
  border: 1px solid ${(props) => props.theme.colors.primary};
  color: ${(props) => props.theme.colors.primary};
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: bold;
  transition: all 0.2s;

  &:hover {
    background-color: rgba(77, 166, 255, 0.1);
  }
`;