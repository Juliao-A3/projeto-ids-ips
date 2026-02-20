import styled from 'styled-components';

export const SystemContainer = styled.div`
    display: flex;
    justify-content: center;
    width: 100%;
`;

export const MainContent = styled.div` 
    padding-top: 64px;
    padding-left: 32px;   /* mesmo padding do HeaderContainer */
    padding-right: 32px;  /* mesmo padding do HeaderContainer */
    width: 100%;
    max-width: 1400px;    /* mesmo max-width do HeaderContent */
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
`;