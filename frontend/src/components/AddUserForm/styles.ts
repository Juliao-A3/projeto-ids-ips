import styled from 'styled-components';

export const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

export const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

export const Label = styled.label`
  font-size: 11px;
  font-weight: 600;
  color: ${(props) => props.theme.colors.text.secondary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

export const Input = styled.input`
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 6px;
  padding: 12px 16px;
  font-size: 14px;
  color: ${(props) => props.theme.colors.text.primary};
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

export const Select = styled.select`
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 6px;
  padding: 12px 16px;
  font-size: 14px;
  color: ${(props) => props.theme.colors.text.primary};
  cursor: pointer;
  transition: all 0.2s;

  &:focus {
    outline: none;
    border-color: ${(props) => props.theme.colors.primary};
    background: rgba(255, 255, 255, 0.08);
  }

  option {
    background: ${(props) => props.theme.colors.surface};
  }
`;

export const PasswordInputWrapper = styled.div`
  position: relative;
  display: flex;
  align-items: center;
`;

export const PasswordInput = styled.input`
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 6px;
  padding: 12px 16px;
  padding-right: 48px;
  font-size: 14px;
  color: ${(props) => props.theme.colors.text.primary};
  width: 100%;
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

export const PasswordToggle = styled.button`
  position: absolute;
  right: 12px;
  background: transparent;
  border: none;
  color: ${(props) => props.theme.colors.text.secondary};
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;

  &:hover {
    color: ${(props) => props.theme.colors.text.primary};
  }
`;

export const PasswordStrength = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 4px;
`;

export const StrengthBar = styled.div`
  width: 100%;
  height: 4px;
  background: #2a2a2a;
  border-radius: 2px;
  overflow: hidden;
`;

interface StrengthBarFillProps {
  strength: number;
}

export const StrengthBarFill = styled.div<StrengthBarFillProps>`
  height: 100%;
  width: ${({ strength }) => strength}%;
  background: ${({ strength }) =>
    strength > 60 ? '#22c55e' : strength > 40 ? '#eab308' : '#ef4444'
  };
  transition: width 0.3s ease, background 0.3s ease;
`;

export const CheckboxGroup = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;

  span {
    font-size: 13px;
    color: ${(props) => props.theme.colors.text.secondary};
  }
`;

export const ButtonGroup = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
`;

export const CancelButton = styled.button`
  background: transparent;
  color: ${(props) => props.theme.colors.text.secondary};
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 6px;
  padding: 10px 24px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: ${(props) => props.theme.colors.text.primary};
    color: ${(props) => props.theme.colors.text.primary};
  }
`;

export const SubmitButton = styled.button`
  background: ${(props) => props.theme.colors.primary};
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 10px 24px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    opacity: 0.9;
  }
`;