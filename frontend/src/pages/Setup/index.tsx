import { useState } from "react";
import { useForm } from "react-hook-form";
import { Wrapper, GridBg } from "../Login/styles";
import {
  Panel, Header, StepBadge, Title, Description, Divider,
  Form, Field, Label, InputRow, InputIcon, EyeBtn,
  StyledInput, ErrorMsg, SubmitBtn, LoginRow, LoginText, LoginLink
} from "./styles";
import { api } from "../../services/api";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

type FormData = {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
};

export default function Setup() {
  const [showPass, setShowPass] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);

  const { register, handleSubmit, watch, formState: { errors } } = useForm<FormData>();
  const navigate = useNavigate();
  const { setUser } = useAuth();

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    try {
      const response = await api.post("/auth/register", {
        nome: data.name,
        email: data.email,
        senha: data.password
      });

      // Mostra mensagem de sucesso
      alert("Conta criada com sucesso! Faça login para continuar.");

      // Redireciona para o login
      navigate("/login", { replace: true });

    } catch (err: any) {
      if (err.response?.data?.detail) alert(err.response.data.detail);
      else alert("Erro ao criar conta. Tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Wrapper>
      <GridBg />
      <Panel>

        <Header>
          <StepBadge>⚙ CONFIGURAÇÃO INICIAL</StepBadge>
          <Title>PRIMEIRO ACESSO</Title>
          <Description>
            Cria a conta de administrador para<br />
            começar a usar o AEGIS
          </Description>
        </Header>

        <Divider />

        <Form onSubmit={handleSubmit(onSubmit)}>

          {/* Nome */}
          <Field>
            <Label htmlFor="name">NOME COMPLETO</Label>
            <InputRow>
              <InputIcon>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                  <circle cx="12" cy="8" r="4" />
                  <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" />
                </svg>
              </InputIcon>
              <StyledInput
                id="name"
                type="text"
                placeholder="João Silva"
                $error={!!errors.name}
                {...register("name", { required: "Campo obrigatório" })}
              />
            </InputRow>
            {errors.name && <ErrorMsg>⚠ {errors.name.message}</ErrorMsg>}
          </Field>

          {/* Email */}
          <Field>
            <Label htmlFor="email">EMAIL</Label>
            <InputRow>
              <InputIcon>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                  <rect x="2" y="4" width="20" height="16" rx="2" />
                  <path d="M2 7l10 7 10-7" />
                </svg>
              </InputIcon>
              <StyledInput
                id="email"
                type="text"
                placeholder="admin@dominio.com"
                $error={!!errors.email}
                {...register("email", {
                  required: "Campo obrigatório",
                  pattern: { value: /\S+@\S+\.\S+/, message: "Email inválido" },
                })}
              />
            </InputRow>
            {errors.email && <ErrorMsg>⚠ {errors.email.message}</ErrorMsg>}
          </Field>

          {/* Password */}
          <Field>
            <Label htmlFor="password">PASSWORD</Label>
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
                  minLength: { value: 8, message: "Mínimo 8 caracteres" },
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

          {/* Confirmar Password */}
          <Field>
            <Label htmlFor="confirmPassword">CONFIRMAR PASSWORD</Label>
            <InputRow>
              <InputIcon>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                  <rect x="5" y="11" width="14" height="10" rx="2" />
                  <path d="M8 11V7a4 4 0 0 1 8 0v4" />
                </svg>
              </InputIcon>
              <StyledInput
                id="confirmPassword"
                type={showConfirm ? "text" : "password"}
                placeholder="••••••••"
                $error={!!errors.confirmPassword}
                {...register("confirmPassword", {
                  required: "Campo obrigatório",
                  validate: val => val === watch("password") || "Passwords não coincidem",
                })}
              />
              <EyeBtn type="button" onClick={() => setShowConfirm(v => !v)} tabIndex={-1}>
                {showConfirm
                  ? <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  : <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M17.94 17.94A10.9 10.9 0 0 1 12 20C5 20 1 12 1 12a18.6 18.6 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.1 9.1 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                }
              </EyeBtn>
            </InputRow>
            {errors.confirmPassword && <ErrorMsg>⚠ {errors.confirmPassword.message}</ErrorMsg>}
          </Field>

          <SubmitBtn type="submit" disabled={loading} $loading={loading}>
            {loading ? "A CRIAR CONTA..." : "CRIAR CONTA DE ADMINISTRADOR →"}
          </SubmitBtn>

          <LoginRow>
            <LoginText>Já tens conta?</LoginText>
            <LoginLink href="/login">Fazer login</LoginLink>
          </LoginRow>

        </Form>
      </Panel>
    </Wrapper>
  );
}