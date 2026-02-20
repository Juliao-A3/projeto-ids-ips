import styled from 'styled-components';

export const Container = styled.div`
  flex: 1;
  padding: 24px;
  max-width: 1220px;
  margin: auto 0;
  width: 100%;
  overflow-y: auto;
  height: calc(100vh - 80px);
  color: ${(props) => props.theme.colors.text.primary};
`;

export const Section = styled.section`
  margin-bottom: 16px;
`;

export const SectionTitle = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  font-size: 14px;
  font-weight: 700;
  color: ${(props) => props.theme.colors.text.primary};
  text-transform: uppercase;
  letter-spacing: 1px;

  svg {
    color: ${(props) => props.theme.colors.primary};
    font-size: 18px;
  }
`;

export const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr); 
  gap: 20px;
  border-top: 1px solid ${({ theme }) => theme.colors.border};
  padding-top: 1rem;
`;




