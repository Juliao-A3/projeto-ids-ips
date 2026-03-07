import { ThemeProvider } from "styled-components";
import { GlobalStyle } from "./styles/global";
import { BrowserRouter} from 'react-router-dom'
import { theme } from "./styles/theme/default";
import { Router } from './Router'
import { AuthProvider } from "./contexts/AuthContext";

export function App() {
  return (
    <AuthProvider>
      <ThemeProvider theme={theme}>
        <BrowserRouter>
          <Router/>
        </BrowserRouter>
        <GlobalStyle />
      </ThemeProvider>
    </AuthProvider>
  )
}