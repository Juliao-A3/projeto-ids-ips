import styled, { keyframes } from "styled-components";

const fadeUp = keyframes`
  from { opacity: 0; transform: translateY(18px); }
  to   { opacity: 1; transform: translateY(0); }
`;

export const Panel = styled.div`
  position: relative;
  width: 370px;
  background: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 4px;
  padding: 40px 36px 28px;
  box-shadow:
    0 0 60px ${({ theme }) => theme.colors.primary}18,
    0 30px 80px rgba(0,0,0,0.6);
  animation: ${fadeUp} 0.7s ease both;

  &::before {
    content: '';
    position: absolute;
    top: -1px; left: -1px; right: -1px;
    height: 2px;
    background: linear-gradient(
      90deg,
      transparent,
      ${({ theme }) => theme.colors.primary},
      transparent
    );
    border-radius: 4px 4px 0 0;
  }
`;

export const Header = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 28px;
`;

export const StepBadge = styled.div`
  font-family: 'Share Tech Mono', monospace;
  font-size: 9px;
  letter-spacing: 0.25em;
  color: ${({ theme }) => theme.colors.primary};
  background: ${({ theme }) => theme.colors.primary}18;
  border: 1px solid ${({ theme }) => theme.colors.primary}44;
  border-radius: 20px;
  padding: 4px 12px;
  margin-bottom: 14px;
  text-transform: uppercase;
`;

export const Title = styled.h1`
  font-family: 'Orbitron', monospace;
  font-size: 20px;
  font-weight: 900;
  letter-spacing: 0.2em;
  color: ${({ theme }) => theme.colors.text.primary};
  text-align: center;
  margin-bottom: 6px;
`;

export const Description = styled.p`
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  color: ${({ theme }) => theme.colors.text.muted};
  text-align: center;
  letter-spacing: 0.08em;
  line-height: 1.6;
`;

export const Divider = styled.div`
  width: 100%;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    ${({ theme }) => theme.colors.border} 30%,
    ${({ theme }) => theme.colors.border} 70%,
    transparent
  );
  margin-bottom: 22px;
`;

export const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 14px;
`;

export const Field = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
`;

export const Label = styled.label`
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  letter-spacing: 0.2em;
  color: ${({ theme }) => theme.colors.text.secondary};
  text-transform: uppercase;
`;

export const InputRow = styled.div`
  position: relative;
  display: flex;
  align-items: center;
`;

export const InputIcon = styled.span`
  position: absolute;
  left: 12px;
  color: ${({ theme }) => theme.colors.text.muted};
  display: flex;
  align-items: center;
  pointer-events: none;
`;

export const EyeBtn = styled.button`
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  color: ${({ theme }) => theme.colors.text.muted};
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  transition: color 0.2s;
  &:hover { color: ${({ theme }) => theme.colors.primary}; }
`;

export const StyledInput = styled.input<{ $error?: boolean }>`
  width: 100%;
  background: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme, $error }) => $error ? theme.colors.danger : theme.colors.border};
  border-radius: 4px;
  color: ${({ theme }) => theme.colors.text.primary};
  font-family: 'Share Tech Mono', monospace;
  font-size: 13px;
  padding: 10px 40px 10px 36px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;

  &::placeholder {
    color: ${({ theme }) => theme.colors.text.muted};
    font-size: 11px;
  }

  &:focus {
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 2px ${({ theme }) => theme.colors.primary}22;
  }
`;

export const ErrorMsg = styled.span`
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  color: ${({ theme }) => theme.colors.danger};
  letter-spacing: 0.05em;
`;

export const SubmitBtn = styled.button<{ $loading?: boolean }>`
  width: 100%;
  padding: 13px;
  background: ${({ theme, $loading }) =>
    $loading ? `${theme.colors.primary}22` : theme.colors.primary};
  border: 1px solid ${({ theme }) => theme.colors.primary};
  border-radius: 4px;
  color: ${({ theme }) => theme.colors.text.primary};
  font-family: 'Orbitron', monospace;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  cursor: ${({ $loading }) => ($loading ? "wait" : "pointer")};
  transition: all 0.25s;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
    transform: translateX(-100%);
    transition: transform 0.5s;
  }
  &:hover:not(:disabled)::before { transform: translateX(100%); }
  &:hover:not(:disabled) {
    box-shadow: 0 0 20px ${({ theme }) => theme.colors.primary}66;
    transform: translateY(-1px);
  }
  &:disabled { cursor: wait; opacity: 0.7; }
`;

export const LoginRow = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 16px;
`;

export const LoginText = styled.span`
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  color: ${({ theme }) => theme.colors.text.muted};
  letter-spacing: 0.08em;
`;

export const LoginLink = styled.a`
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  color: ${({ theme }) => theme.colors.primary};
  text-decoration: none;
  letter-spacing: 0.08em;
  cursor: pointer;
  transition: opacity 0.2s;
  &:hover { opacity: 0.7; text-decoration: underline; }
`;