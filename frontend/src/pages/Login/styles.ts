import styled, { keyframes } from "styled-components";

const gridMove = keyframes`
  from { transform: perspective(600px) rotateX(20deg) translateY(0); }
  to   { transform: perspective(600px) rotateX(20deg) translateY(80px); }
`;

export const Wrapper = styled.div`
  position: relative;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background:
    radial-gradient(ellipse 70% 50% at 50% 0%, #0d1f35 0%, transparent 70%),
    ${({ theme }) => theme.colors.background};
`;

export const GridBg = styled.div`
  position: absolute;
  inset: -10%;
  background-image:
    linear-gradient(${({ theme }) => theme.colors.border} 1px, transparent 1px),
    linear-gradient(90deg, ${({ theme }) => theme.colors.border} 1px, transparent 1px);
  background-size: 60px 60px;
  opacity: 0.3;
  animation: ${gridMove} 8s linear infinite;
  pointer-events: none;
`;

const fadeUp = keyframes`
  from { opacity: 0; transform: translateY(18px); }
  to   { opacity: 1; transform: translateY(0); }
`;

export const Panel = styled.div`
  position: relative;
  width: 350px;
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

const shieldPulse = keyframes`
  0%, 100% { filter: drop-shadow(0 0 8px ${({ theme }) => theme.colors.primary}); }
  50%       { filter: drop-shadow(0 0 4px ${({ theme }) => theme.colors.primary}); }
`;

const spinRing = keyframes`
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
`;

const spinRingRev = keyframes`
  from { transform: rotate(0deg); }
  to   { transform: rotate(-360deg); }
`;

const glitch = keyframes`
  0%   { clip-path: inset(0 0 98% 0); transform: translate(-2px, 0); }
  20%  { clip-path: inset(40% 0 50% 0); transform: translate(2px, 0); }
  60%  { clip-path: inset(15% 0 70% 0); transform: translate(1px, 0); }
  100% { clip-path: inset(0 0 98% 0); transform: translate(0, 0); }
`;

export const ShieldWrapper = styled.div`
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
`;

export const ShieldOuter = styled.div`
  position: relative;
  width: 72px; height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

export const Ring1 = styled.div`
  position: absolute;
  width: 68px; height: 68px;
  border-radius: 50%;
  border: 1px solid transparent;
  border-top-color: ${({ theme }) => theme.colors.primary};
  border-right-color: ${({ theme }) => theme.colors.primary}44;
  animation: ${spinRing} 4s linear infinite;
`;

export const Ring2 = styled.div`
  position: absolute;
  width: 52px; height: 52px;
  border-radius: 50%;
  border: 1px solid transparent;
  border-bottom-color: ${({ theme }) => theme.colors.primary}88;
  border-left-color: ${({ theme }) => theme.colors.primary}88;
  animation: ${spinRingRev} 3s linear infinite;
`;

export const ShieldSvg = styled.svg`
  width: 32px; height: 32px;
  z-index: 2;
  animation: ${shieldPulse} 2.5s ease-in-out infinite;
`;

export const Logo = styled.h1`
  font-family: 'Orbitron', monospace;
  font-size: 26px;
  font-weight: 900;
  letter-spacing: 0.4em;
  text-align: center;
  color: ${({ theme }) => theme.colors.text.primary};
  position: relative;
`;

export const Subtitle = styled.p`
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  letter-spacing: 0.28em;
  color: ${({ theme }) => theme.colors.primary};
  text-align: center;
  margin-top: 5px;
  margin-bottom: 24px;
  opacity: 0.9;
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

export const FieldHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

export const Anchor = styled.a`
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  color: ${({ theme }) => theme.colors.primary};
  text-decoration: none;
  letter-spacing: 0.08em;
  cursor: pointer;
  transition: opacity 0.2s;
  &:hover { opacity: 0.7; }
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

export const SubmitBtn = styled.button<{ $loading?: boolean; $success?: boolean }>`
  width: 100%;
  padding: 13px;
  background: ${({ theme, $loading, $success }) =>
    $success
      ? theme.colors.success
      : $loading
      ? `${theme.colors.primary}22`
      : theme.colors.primary};
  border: 1px solid ${({ theme, $success }) =>
    $success ? theme.colors.success : theme.colors.primary};
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

  &:active:not(:disabled) { transform: translateY(0); }
  &:disabled { cursor: wait; opacity: 0.7; }
`;

export const RegisterRow = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 16px;
`;

export const RegisterText = styled.span`
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  color: ${({ theme }) => theme.colors.text.muted};
  letter-spacing: 0.08em;
`;

export const RegisterLink = styled.a`
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  color: ${({ theme }) => theme.colors.primary};
  text-decoration: none;
  letter-spacing: 0.08em;
  cursor: pointer;
  transition: opacity 0.2s;
  &:hover { opacity: 0.7; text-decoration: underline; }
`;


export const RestrictedBadge = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 18px;
  padding: 8px;
  border: 1px solid ${({ theme }) => theme.colors.danger}33;
  border-radius: 4px;
  background: ${({ theme }) => theme.colors.danger}08;
`;

export const RestrictedText = styled.span`
  font-family: 'Share Tech Mono', monospace;
  font-size: 9px;
  color: ${({ theme }) => theme.colors.danger};
  letter-spacing: 0.22em;
  text-transform: uppercase;
`;

export const Copyright = styled.p`
  font-family: 'Share Tech Mono', monospace;
  font-size: 9px;
  color: ${({ theme }) => theme.colors.text.muted};
  text-align: center;
  margin-top: 8px;
  letter-spacing: 0.07em;
`;

export const StatusBar = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid ${({ theme }) => theme.colors.border};
`;

export const StatusItem = styled.div`
  display: flex;
  align-items: center;
  gap: 5px;
`;

const blinkAnim = keyframes`
  0%, 49% { opacity: 1; }
  50%, 100% { opacity: 0; }
`;

export const StatusDot = styled.div<{ $color?: string; $fast?: boolean }>`
  width: 6px; height: 6px;
  border-radius: 50%;
  background: ${({ theme, $color }) => $color || theme.colors.success};
  box-shadow: 0 0 5px ${({ theme, $color }) => $color || theme.colors.success};
  animation: ${blinkAnim} ${({ $fast }) => ($fast ? "0.9s" : "2.2s")} step-start infinite;
`;

export const StatusLabel = styled.span`
  font-family: 'Share Tech Mono', monospace;
  font-size: 9px;
  color: ${({ theme }) => theme.colors.text.muted};
  letter-spacing: 0.1em;
`;