import styled from 'styled-components';

export const Container = styled.div`
  display: inline-flex;
  background: #1a1a1a;
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 6px;
  overflow: hidden;
`;

interface OptionProps {
  isSelected: boolean;
}

export const Option = styled.button<OptionProps>`
  padding: 8px 24px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  background: ${({ isSelected, theme }) => 
    isSelected ? theme.colors.primary : 'transparent'
  };
  color: ${({ isSelected }) => 
    isSelected ? '#fff' : '#888'
  };

  &:not(:last-child) {
    border-right: 1px solid ${(props) => props.theme.colors.border};
  }

  &:hover {
    color: ${({ isSelected }) => isSelected ? '#fff' : '#fff'};
  }
`;