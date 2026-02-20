import styled from 'styled-components';

export const Container = styled.div`
  width: 100%;
  max-width: 1220px;
`;

export const Header = styled.div`
  margin-bottom: 24px;
`;

export const Title = styled.h2`
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 15px;
  font-weight: 600;
  border-bottom: 1px solid ${(props) => props.theme.colors.border};
  padding-bottom: 1.5rem;
  color: ${(props) => props.theme.colors.text.primary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0;
`;

export const Grid = styled.div`
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 8px;
  padding: 24px;
  background: ${(props) => props.theme.colors.surface};
  border-radius: 4px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  column-gap: 32px;
`;

export const Column = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

export const ColumnTitle = styled.h3`
  font-size: 11px;
  font-weight: 600;
  color: ${(props) => props.theme.colors.text.secondary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 8px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid ${(props) => props.theme.colors.border};
`;

export const PermissionItem = styled.div`
  display: flex;
  flex-direction: column;
`;

export const PermissionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
`;

export const PermissionTitle = styled.h4`
  font-size: 14px;
  font-weight: 500;
  color: ${(props) => props.theme.colors.text.primary};
  margin: 0 0 4px 0;
`;

export const PermissionDescription = styled.p`
  font-size: 12px;
  color: ${(props) => props.theme.colors.text.secondary};
  margin: 0;
  line-height: 1.4;
`;