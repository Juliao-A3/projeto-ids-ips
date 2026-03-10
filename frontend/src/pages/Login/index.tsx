import { useForm } from "react-hook-form";
import {
  Wrapper, GridBg, Panel,
  ShieldWrapper, ShieldOuter, Ring1, Ring2, ShieldSvg,
  Logo, Subtitle, Divider,
  Form, Field, FieldHeader, Label, Anchor,
  InputRow, InputIcon, EyeBtn, StyledInput, ErrorMsg,
  SubmitBtn,
  RegisterRow,
  RegisterText,
  RegisterLink,
  RestrictedBadge,
  Copyright,
  RestrictedText,
  StatusBar,
  StatusDot,
  StatusItem,
  StatusLabel,
} from "./styles";

import { api } from "../../services/api";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

const timeStr = new Date().toTimeString().slice(0, 8);
const tzStr = Intl.DateTimeFormat().resolvedOptions().timeZone;

type FormData = {
  email: string;
  password: string;
};

export default function Login() {
  const [showPass, setShowPass]   = useState(false);
  const [loading, setLoading]     = useState(false);
  const [success, setSuccess]     = useState(false);
  const [apiError, setApiError]   = useState('');
  const [, setTick]               = useState(0);

  useEffect(() => {
    const id = setInterval(() => setTick(t => t + 1), 1000);
    return () => clearInterval(id);
  }, []);

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>();
  const navigate = useNavigate();
  const { setUser, user } = useAuth();

  useEffect(() => {
    if (user) navigate("/", { replace: true });
  }, [user]);

  const onSubmit = async (data: FormData) => {
    try {
      setLoading(true);
      setApiError('');

      const response = await api.post("/auth/login", {
        email: data.email,
        senha: data.password,
      });

      localStorage.setItem("access_token", response.data.access_token);
      localStorage.setItem("refresh_token", response.data.refresh_token);

      const userData = response.data.user;
      localStorage.setItem("user_name", userData.name);
      localStorage.setItem("user_role", userData.role.toLowerCase());

      const initials = userData.name
        .trim()
        .split(/\s+/)
        .filter((word: string) => word.length > 0)
        .map((word: string) => word[0])
        .join("")
        .toUpperCase()
        .slice(0, 2) || "U";

      setUser({
        name: userData.name,
        role: userData.role.toLowerCase(),
        initials
      });

      setSuccess(true);
      setTimeout(() => navigate("/", { replace: true }), 500);

    } catch (error: any) {
      const status = error.response?.status;
      const detail = error.response?.data?.detail;

      if (status === 403) {
        setApiError('Conta desativada. Contacta o administrador.');
      } else if (status === 401) {
        setApiError('Email ou senha inválidos.');
      } else {
        setApiError(detail || 'Erro ao conectar ao servidor.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Wrapper>
      <GridBg />
      <Panel>
        <ShieldWrapper>
          <ShieldOuter>
            <Ring1 />
            <Ring2 />
            <ShieldSvg viewBox="0 0 24 24" fill="none">
              <path d="M12 2L3 6v6c0 5.25 3.75 10.15 9 11.25C17.25 22.15 21 17.25 21 12V6L12 2z" fill="#00A3FF22" stroke="#00A3FF" strokeWidth="1.5" strokeLinejoin="round" />
              <path d="M9 12l2 2 4-4" stroke="#00A3FF" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
            </ShieldSvg>
          </ShieldOuter>
        </ShieldWrapper>

        <Logo data-text="AEGIS">AEGIS</Logo>
        <Subtitle>LOGIN DE SEGURANÇA</Subtitle>
        <Divider />

        <Form onSubmit={handleSubmit(onSubmit)}>
          {/* Email */}
          <Field>
            <Label htmlFor="email">USUÁRIO / EMAIL</Label>
            <InputRow>
              <InputIcon>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                  <circle cx="12" cy="8" r="4" />
                  <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" />
                </svg>
              </InputIcon>
              <StyledInput
                id="email"
                type="text"
                placeholder="usuario@dominio.com"
                $error={!!errors.email}
                {...register("email", {
                  required: "Campo obrigatório",
                  pattern: { value: /\S+@\S+\.\S+/, message: "Email inválido" },
                  onChange: () => setApiError(''),
                })}
              />
            </InputRow>
            {errors.email && <ErrorMsg>⚠ {errors.email.message}</ErrorMsg>}
          </Field>

          {/* Password */}
          <Field>
            <FieldHeader>
              <Label htmlFor="password">SENHA</Label>
              <Anchor href="#">Esqueci minha senha</Anchor>
            </FieldHeader>
            <InputRow>
              <InputIcon>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                  <rect x="5" y="11" width="14" height="10" rx="2" />
                  <path d="M8 11V7a4 4 0 0 1 8 0v4" />
                </svg>
              </InputIcon>
              <StyledInput
                id="password"
                type={showPass ? "text" : "password"}
                placeholder="••••••••"
                $error={!!errors.password}
                {...register("password", {
                  required: "Campo obrigatório",
                  minLength: { value: 6, message: "Mínimo 6 caracteres" },
                  onChange: () => setApiError(''),
                })}
              />
              <EyeBtn type="button" onClick={() => setShowPass(v => !v)} tabIndex={-1}>
                {showPass
                  ? <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  : <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M17.94 17.94A10.9 10.9 0 0 1 12 20C5 20 1 12 1 12a18.6 18.6 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.1 9.1 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                }
              </EyeBtn>
            </InputRow>
            {errors.password && <ErrorMsg>⚠ {errors.password.message}</ErrorMsg>}
          </Field>

          {/* Erro da API */}
          {apiError && (
            <ErrorMsg style={{
              display: 'block',
              padding: '10px 14px',
              background: '#ef444412',
              border: '1px solid #ef444444',
              borderLeft: '3px solid #ef4444',
              borderRadius: '4px',
              marginBottom: '12px',
              fontSize: '11px',
              textAlign: 'center',
            }}>
              ⚠ {apiError}
            </ErrorMsg>
          )}

          <SubmitBtn
            type="submit"
            disabled={loading || success}
            $loading={loading}
            $success={success}
          >
            {success ? "✓ ACESSO CONCEDIDO" : loading ? "VERIFICANDO..." : "ENTRAR NO SISTEMA →"}
          </SubmitBtn>

          <RegisterRow>
            <RegisterText>Não tens conta?</RegisterText>
            <RegisterLink href="/setup">Solicitar acesso</RegisterLink>
          </RegisterRow>
        </Form>

        <RestrictedBadge>
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" color="red">
            <rect x="5" y="11" width="14" height="10" rx="2" />
            <path d="M8 11V7a4 4 0 0 1 8 0v4" />
          </svg>
          <RestrictedText>Acesso restrito a pessoal autorizado</RestrictedText>
        </RestrictedBadge>

        <Copyright>© 2025 AEGIS SECURITY · Todos os direitos reservados</Copyright>

        <StatusBar>
          <StatusItem>
            <StatusDot />
            <StatusLabel>SISTEMA OPERACIONAL</StatusLabel>
          </StatusItem>
          <StatusItem>
            <StatusDot $color="#00A3FF" $fast />
            <StatusLabel>{timeStr} · {tzStr}</StatusLabel>
          </StatusItem>
        </StatusBar>

      </Panel>
    </Wrapper>
  );
}