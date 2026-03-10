import styled from 'styled-components';

export const Container = styled.div`
  display: flex;
`;

export const MainContent = styled.div`
  margin-left: 240px;
  margin-top: 32px;
  padding-top: 60px;
  width: calc(100% - 240px);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 32px 32px 32px;
`;

export const ProfileCard = styled.div`
  background: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 10px;
  padding: 32px;
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 20px;
  width: 100%;
  max-width: 600px;
`;

export const Avatar = styled.div`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: ${({ theme }) => theme.colors.primary}18;
  border: 2px solid ${({ theme }) => theme.colors.primary}44;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Orbitron', monospace;
  font-size: 24px;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.primary};
  flex-shrink: 0;
`;

export const ProfileInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
`;

export const ProfileName = styled.div`
  font-family: 'Rajdhani', sans-serif;
  font-size: 22px;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.text.primary};
`;

export const RoleBadge = styled.span<{ $color: string }>`
  display: inline-block;
  padding: 3px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-family: 'Share Tech Mono', monospace;
  font-weight: 700;
  letter-spacing: 1px;
  background: ${({ $color }) => `${$color}18`};
  border: 1px solid ${({ $color }) => `${$color}44`};
  color: ${({ $color }) => $color};
  width: fit-content;
`;

export const MemberSince = styled.div`
  font-size: 11px;
  color: ${({ theme }) => theme.colors.text.muted};
  font-family: 'Share Tech Mono', monospace;
`;

export const InfoCard = styled.div`
  background: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 10px;
  padding: 24px;
  margin-bottom: 16px;
  width: 100%;
  max-width: 600px;
`;

export const SectionTitle = styled.div`
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  color: ${({ theme }) => theme.colors.primary};
  letter-spacing: 2px;
  margin-bottom: 20px;
`;

export const FieldGroup = styled.div`
  margin-bottom: 16px;
  &:last-child { margin-bottom: 0; }
`;

export const FieldLabel = styled.label`
  display: block;
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  color: ${({ theme }) => theme.colors.text.muted};
  letter-spacing: 1px;
  margin-bottom: 6px;
`;

export const FieldValue = styled.div`
  color: ${({ theme }) => theme.colors.text.primary};
  font-size: 13px;
  padding: 10px 0;
`;

export const FieldInput = styled.input`
  width: 100%;
  background: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.primary}66;
  border-radius: 6px;
  padding: 10px 14px;
  color: ${({ theme }) => theme.colors.text.primary};
  font-size: 13px;
  font-family: 'Inter', sans-serif;
  outline: none;
  transition: border-color 0.2s;

  &:focus {
    border-color: ${({ theme }) => theme.colors.primary};
  }
`;

export const RoleNote = styled.span`
  color: ${({ theme }) => theme.colors.text.muted};
  font-size: 10px;
  margin-left: 8px;
`;

export const ErrorMessage = styled.div`
  width: 100%;
  max-width: 600px;
  padding: 10px 14px;
  margin-bottom: 12px;
  background: ${({ theme }) => theme.colors.danger}12;
  border: 1px solid ${({ theme }) => theme.colors.danger}44;
  border-left: 3px solid ${({ theme }) => theme.colors.danger};
  border-radius: 4px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  color: ${({ theme }) => theme.colors.danger};
`;

export const SuccessMessage = styled.div`
  width: 100%;
  max-width: 600px;
  padding: 10px 14px;
  margin-bottom: 12px;
  background: ${({ theme }) => theme.colors.success}12;
  border: 1px solid ${({ theme }) => theme.colors.success}44;
  border-left: 3px solid ${({ theme }) => theme.colors.success};
  border-radius: 4px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  color: ${({ theme }) => theme.colors.success};
`;

export const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  width: 100%;
  max-width: 600px;
`;

export const CancelButton = styled.button`
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  background: transparent;
  border: 1px solid ${({ theme }) => theme.colors.border};
  color: ${({ theme }) => theme.colors.text.muted};
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  transition: all 0.2s;

  &:hover {
    border-color: ${({ theme }) => theme.colors.text.muted};
    color: ${({ theme }) => theme.colors.text.primary};
  }
`;

export const SaveButton = styled.button`
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  background: ${({ theme }) => theme.colors.primary};
  border: none;
  color: #fff;
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  font-weight: 700;
  transition: opacity 0.2s;

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &:hover:not(:disabled) {
    opacity: 0.85;
  }
`;

export const EditButton = styled.button`
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  background: ${({ theme }) => theme.colors.primary}18;
  border: 1px solid ${({ theme }) => theme.colors.primary}44;
  color: ${({ theme }) => theme.colors.primary};
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  font-weight: 700;
  transition: all 0.2s;

  &:hover {
    background: ${({ theme }) => theme.colors.primary}28;
  }
`;