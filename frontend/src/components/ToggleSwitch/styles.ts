import styled from 'styled-components';

export const Container = styled.label`
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  flex-shrink: 0;
  cursor: pointer;
`;

export const Input = styled.input`
  opacity: 0;
  width: 0;
  height: 0;
`;

interface SliderProps {
  checked: boolean;
}

export const Slider = styled.span<SliderProps>`
  z-index: 1;
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: ${({ checked, theme }) => 
    checked ? theme.colors.primary : '#333'
  };
  transition: 0.3s;
  border-radius: 24px;

  &:before {
    position: absolute;
    content: "";
    height: 18px;
    width: 18px;
    left: ${({ checked }) => checked ? '23px' : '3px'};
    bottom: 3px;
    background-color: white;
    transition: 0.3s;
    border-radius: 50%;
  }

  &:hover {
    opacity: 0.9;
  }
`;