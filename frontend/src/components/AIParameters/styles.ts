import styled from "styled-components";

export const CardContainer = styled.section`
  width: 100%;
  max-width: 1220px;
  padding: 24px;
  margin-top: -2.5rem;
`;

export const SectionHeader = styled.div`
  display: flex;
  align-items: center;
  padding-bottom: 1.5rem;
  gap: 8px;
  margin-bottom: 1rem;
  color: ${(props) => props.theme.colors.text.primary};
  font-size: 14px;
  font-weight: bold;
  letter-spacing: 1px;
  text-transform: uppercase;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
  span {
    color: ${(props) => props.theme.colors.primary};
    size:12px;
  }
`;

export const ControlsGrid = styled.div`
  border-radius: 4px;
  color: ${(props) => props.theme.colors.text.primary};
  font-family: 'Inter', sans-serif;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  column-gap: 32px; 
`;

export const ControlWrapper = styled.div`
  display: flex;
  flex-direction: column;

  background: ${({ theme }) => theme.colors.surface};
  border-radius: 6px;

  padding: 24px;
`;


export const LabelRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 11px;
  color: #8a949d;
`;

export const ValueDisplay = styled.span`
  color: ${props => props.color || '#00a3ff'};
  font-weight: bold;
`;

export const StyledSlider = styled.input.attrs({ type: 'range' })`
  width: 100%;
  appearance: none;
  background: #232a31;
  height: 4px;
  border-radius: 2px;
  outline: none;

  &::-webkit-slider-thumb {
    appearance: none;
    width: 12px;
    height: 12px;
    background: #00a3ff;
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 0 10px rgba(0, 163, 255, 0.5);
  }
`;

export const RangeLabels = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 9px;
  color: #4b5563;
  font-weight: 600;
`;
