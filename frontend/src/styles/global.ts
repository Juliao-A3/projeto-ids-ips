import { createGlobalStyle } from 'styled-components';

export const GlobalStyle = createGlobalStyle`
    * {
        margin: 0;
        padding: 0;

        box-sizing: border-box;
    }

    &::-webkit-scrollbar {
        display: none;
    }

    body, html {
        width: 100%;
        overflow-x: hidden;
        background-color: ${(props) => props.theme.colors.background}; 
        color: ${(props) => props.theme.colors.text.primary};
    }

    body, input, textarea, button {
        font: 400 1rem 'Inter', sans-serif;
    }
`;

