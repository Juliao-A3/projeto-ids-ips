

import styled from 'styled-components';

export const LoginContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: ${({ theme }) => theme.colors.background};
`;

export const LoginContent = styled.div`
  width: 400px;
  padding: 2rem;
  border-radius: 8px;
  background: ${({ theme }) => theme.colors.surface};
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
`;

export const LoginHeader = styled.header`
  text-align: center;
  margin-bottom: 1.5rem;

  svg {
    margin-bottom: 1rem;
  }

  h1 {
    margin: 0;
  }

  span {
    font-size: 0.9rem;
    color: ${({ theme }) => theme.colors.textSecondary};
  }
`;

export const LoginForm = styled.form`
  display: grid;
  gap: 0.5rem;

  label {
    font-weight: bold;
  }

  button {
    margin-top: 1rem;
    padding: 0.75rem;
    border: none;
    background: ${({ theme }) => theme.colors.primary};
    color: #fff;
    border-radius: 4px;
    cursor: pointer;
  }
`;

export const InputEmail = styled.input`
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
`;

export const InputSenha = styled(InputEmail).attrs({ type: 'password' })``;

export const LoginFooter = styled.footer`
  margin-top: 1rem;
  text-align: center;
  font-size: 0.8rem;
  color: ${({ theme }) => theme.colors.textSecondary};
`;
