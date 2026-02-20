import styled, { keyframes } from 'styled-components';

export const SystemContainer = styled.div `
    display: flex;
`

export const MainContent = styled.div `
    margin-left: 240px; 
    padding-top: 60px; 
    width: calc(100% - 240px);
  
    display: flex;
    flex-direction: column;
    align-items: center;
`

const slideUp = keyframes`
  from { transform: translateY(100%); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
`;

export const SaveBar = styled.div`
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  max-width: 800px;
  background-color: #1a1a1a;
  border: 1px solid #333;
  padding: 16px 24px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  z-index: 1000;
  animation: ${slideUp} 0.3s ease-out;

  span {
    color: #ccc;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
`;

export const SaveButton = styled.button`
  background-color: #00a2ff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: 0.2s;

  &:hover {
    background-color: #0081cc;
  }
`;

export const CancelButton = styled.button`
  background: transparent;
  color: #888;
  border: none;
  margin-right: 15px;
  cursor: pointer;
  font-weight: 500;

  &:hover {
    color: #fff;
  }
`;
