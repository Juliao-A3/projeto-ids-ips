import 'styled-components';
import { theme } from './theme/default';

type Theme = typeof theme;

declare module 'styled-components' {
  export interface DefaultTheme extends Theme {}
}

