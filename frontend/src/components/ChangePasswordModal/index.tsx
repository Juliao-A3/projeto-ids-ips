import { useState } from "react";
import { useForm } from "react-hook-form";
import {
  Overlay, Modal, ModalHeader, ModalTitle, CloseBtn, Divider,
  Form, Field, Label, InputRow, InputIcon, EyeBtn, StyledInput,
  ErrorMsg, ApiError, FooterButtons, CancelBtn, ConfirmBtn
} from "./styles";

type FormData = {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
};

type Props = {
  onClose: () => void;
};

const IconLock = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
    <rect x="5" y="11" width="14" height="10" rx="2" />
    <path d="M8 11V7a4 4 0 0 1 8 0v4" />
  </svg>
);

const IconEye = ({ open }: { open: boolean }) =>
  open ? (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  ) : (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M17.94 17.94A10.9 10.9 0 0 1 12 20C5 20 1 12 1 12a18.6 18.6 0 0 1 5.06-5.94" />
      <path d="M9.9 4.24A9.1 9.1 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
      <line x1="1" y1="1" x2="23" y2="23" />
    </svg>
  );

export function ChangePasswordModal({ onClose }: Props) {
  const [showCurrent, setShowCurrent]   = useState(false);
  const [showNew, setShowNew]           = useState(false);
  const [showConfirm, setShowConfirm]   = useState(false);
  const [loading, setLoading]           = useState(false);
  const [apiError, setApiError]         = useState("");

  const { register, handleSubmit, watch, formState: { errors } } = useForm<FormData>();

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    setApiError("");
    try {
      const response = await fetch("/api/auth/change-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          current_password: data.currentPassword,
          new_password: data.newPassword,
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        setApiError(err.detail || "Senha atual incorreta.");
        return;
      }

      onClose(); // sucesso → fecha modal
    } catch {
      setApiError("Erro de ligação ao servidor.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Overlay onClick={onClose}>
      <Modal onClick={(e) => e.stopPropagation()}>

        <ModalHeader>
          <ModalTitle>REDEFINIR SENHA</ModalTitle>
          <CloseBtn onClick={onClose}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </CloseBtn>
        </ModalHeader>

        <Divider />

        <Form onSubmit={handleSubmit(onSubmit)}>

          {/* Senha atual */}
          <Field>
            <Label htmlFor="currentPassword">SENHA ATUAL</Label>
            <InputRow>
              <InputIcon><IconLock /></InputIcon>
              <StyledInput
                id="currentPassword"
                type={showCurrent ? "text" : "password"}
                placeholder="••••••••"
                $error={!!errors.currentPassword}
                {...register("currentPassword", { required: "Campo obrigatório" })}
              />
              <EyeBtn type="button" onClick={() => setShowCurrent(v => !v)} tabIndex={-1}>
                <IconEye open={showCurrent} />
              </EyeBtn>
            </InputRow>
            {errors.currentPassword && <ErrorMsg>⚠ {errors.currentPassword.message}</ErrorMsg>}
          </Field>

          {/* Nova senha */}
          <Field>
            <Label htmlFor="newPassword">NOVA SENHA</Label>
            <InputRow>
              <InputIcon><IconLock /></InputIcon>
              <StyledInput
                id="newPassword"
                type={showNew ? "text" : "password"}
                placeholder="••••••••"
                $error={!!errors.newPassword}
                {...register("newPassword", {
                  required: "Campo obrigatório",
                  minLength: { value: 8, message: "Mínimo 8 caracteres" },
                })}
              />
              <EyeBtn type="button" onClick={() => setShowNew(v => !v)} tabIndex={-1}>
                <IconEye open={showNew} />
              </EyeBtn>
            </InputRow>
            {errors.newPassword && <ErrorMsg>⚠ {errors.newPassword.message}</ErrorMsg>}
          </Field>

          {/* Confirmar nova senha */}
          <Field>
            <Label htmlFor="confirmPassword">CONFIRMAR NOVA SENHA</Label>
            <InputRow>
              <InputIcon><IconLock /></InputIcon>
              <StyledInput
                id="confirmPassword"
                type={showConfirm ? "text" : "password"}
                placeholder="••••••••"
                $error={!!errors.confirmPassword}
                {...register("confirmPassword", {
                  required: "Campo obrigatório",
                  validate: val => val === watch("newPassword") || "Senhas não coincidem",
                })}
              />
              <EyeBtn type="button" onClick={() => setShowConfirm(v => !v)} tabIndex={-1}>
                <IconEye open={showConfirm} />
              </EyeBtn>
            </InputRow>
            {errors.confirmPassword && <ErrorMsg>⚠ {errors.confirmPassword.message}</ErrorMsg>}
          </Field>

          {/* Erro da API */}
          {apiError && (
            <ApiError>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <circle cx="12" cy="16" r="1" fill="currentColor" stroke="none" />
              </svg>
              {apiError}
            </ApiError>
          )}

          <FooterButtons>
            <CancelBtn type="button" onClick={onClose}>CANCELAR</CancelBtn>
            <ConfirmBtn type="submit" disabled={loading} $loading={loading}>
              {loading ? "A GUARDAR..." : "CONFIRMAR →"}
            </ConfirmBtn>
          </FooterButtons>

        </Form>
      </Modal>
    </Overlay>
  );
}