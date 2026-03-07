import styled, { keyframes } from "styled-components";

const fadeIn = keyframes`
  from { opacity: 0; }
  to   { opacity: 1; }
`;

const slideUp = keyframes`
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
`;

export const Overlay = styled.div`
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  animation: ${fadeIn} 0.2s ease;
`;

export const Modal = styled.div`
  position: relative;
  width: 440px;
  background: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 6px;
  padding: 32px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
  animation: ${slideUp} 0.25s ease;

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
    border-radius: 6px 6px 0 0;
  }
`;

export const ModalHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
`;

export const ModalTitle = styled.h2`
  font-family: 'Orbitron', monospace;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.2em;
  color: ${({ theme }) => theme.colors.text.primary};
`;

export const CloseBtn = styled.button`
  background: none;
  border: none;
  color: ${({ theme }) => theme.colors.text.muted};
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  transition: color 0.2s;
  &:hover { color: ${({ theme }) => theme.colors.danger}; }
`;

export const Divider = styled.div`
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

export const ApiError = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: ${({ theme }) => theme.colors.danger}12;
  border: 1px solid ${({ theme }) => theme.colors.danger}44;
  border-radius: 4px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  color: ${({ theme }) => theme.colors.danger};
  letter-spacing: 0.05em;
`;

export const FooterButtons = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 6px;
`;

export const CancelBtn = styled.button`
  flex: 1;
  padding: 11px;
  background: none;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 4px;
  color: ${({ theme }) => theme.colors.text.secondary};
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.15em;
  cursor: pointer;
  transition: all 0.2s;
  &:hover {
    border-color: ${({ theme }) => theme.colors.text.muted};
    color: ${({ theme }) => theme.colors.text.primary};
  }
`;

export const ConfirmBtn = styled.button<{ $loading?: boolean }>`
  flex: 2;
  padding: 11px;
  background: ${({ theme, $loading }) =>
    $loading ? `${theme.colors.primary}22` : theme.colors.primary};
  border: 1px solid ${({ theme }) => theme.colors.primary};
  border-radius: 4px;
  color: ${({ theme }) => theme.colors.text.primary};
  font-family: 'Orbitron', monospace;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.2em;
  cursor: ${({ $loading }) => ($loading ? "wait" : "pointer")};
  transition: all 0.2s;
  &:hover:not(:disabled) {
    box-shadow: 0 0 16px ${({ theme }) => theme.colors.primary}66;
    transform: translateY(-1px);
  }
  &:disabled { opacity: 0.7; cursor: wait; }
`;