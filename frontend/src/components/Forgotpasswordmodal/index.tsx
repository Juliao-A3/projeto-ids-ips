import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { api } from '../../services/api';
import {
  Overlay, Modal, CloseBtn, StepRow, StepDot, StepLine, Title, Desc,
  AlertBox, FieldWrap, FLabel, InputRow, InputIcon, SInput, FieldErr,
  Btn, ResendRow, ResendBtn, EyeBtn, SuccessCircle,
  StepLbl,
  CodeBox,
  CodeGrid,
  IconBox,
} from './styles';

// Component
interface Props { onClose: () => void; }
type Step = 1 | 2 | 3 | 4;

export function ForgotPasswordModal({ onClose }: Props) {
  const [step, setStep]         = useState<Step>(1);
  const [loading, setLoading]   = useState(false);
  const [alert, setAlert]       = useState<{t:'error'|'success'|'info';msg:string}|null>(null);
  const [email, setEmail]       = useState('');
  const [code, setCode]         = useState(['','','','','','']);
  const [showPass, setShowPass] = useState(false);
  const [showConf, setShowConf] = useState(false);
  const [resends, setResends]   = useState(0);

  const { register, handleSubmit, watch, formState:{errors}, reset } =
    useForm<{email:string;nova_senha:string;confirmar:string}>();

  const focusCode = (i: number) => document.getElementById(`rc-${i}`)?.focus();

  // ── Step 1 
  const onEnviarEmail = async (data: {email:string}) => {
    setLoading(true); setAlert(null);
    try {
      await api.post('/auth/forgot-password', { email: data.email });
      setEmail(data.email);
      setAlert({ t:'info', msg:`Código enviado para ${data.email}` });
      setTimeout(() => { setAlert(null); setStep(2); }, 1100);
    } catch (err: unknown) {
      setAlert({ t:'error', msg: (err as any)?.response?.data?.detail || 'Erro ao enviar código.' });
    } finally { setLoading(false); }
  };

  // ── Step 2 
  const handleCodeInput = (i: number, val: string) => {
    if (!/^\d?$/.test(val)) return;
    const next = [...code]; next[i] = val; setCode(next); setAlert(null);
    if (val && i < 5) setTimeout(() => focusCode(i + 1), 0);
  };
  const handleCodeKey = (i: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !code[i] && i > 0) {
      const next = [...code]; next[i-1] = ''; setCode(next);
      setTimeout(() => focusCode(i - 1), 0);
    }
  };
  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const digits = e.clipboardData.getData('text').replace(/\D/g,'').slice(0,6).split('');
    const next = ['','','','','','']; digits.forEach((d,i) => { next[i]=d; });
    setCode(next); setTimeout(() => focusCode(Math.min(digits.length,5)), 0);
  };

  const onVerificarCodigo = async () => {
    const codeStr = code.join('');
    if (codeStr.length < 6) { setAlert({ t:'error', msg:'Introduz o código completo de 6 dígitos.' }); return; }
    setLoading(true); setAlert(null);
    try {
      await api.post('/auth/verify-reset-code', { email, codigo: codeStr });
      setAlert({ t:'success', msg:'Código verificado! Define a tua nova senha.' });
      setTimeout(() => { setAlert(null); setStep(3); }, 900);
    } catch (err: unknown) {
      setAlert({ t:'error', msg: (err as any)?.response?.data?.detail || 'Código inválido ou expirado.' });
      setCode(['','','','','','']); setTimeout(() => focusCode(0), 0);
    } finally { setLoading(false); }
  };

  const onReenviar = async () => {
    if (resends >= 3) return;
    setLoading(true); setAlert(null);
    try {
      await api.post('/auth/forgot-password', { email });
      setResends(r => r+1); setCode(['','','','','','']);
      setAlert({ t:'info', msg:'Novo código enviado!' });
      setTimeout(() => focusCode(0), 100);
    } catch {
      setAlert({ t:'error', msg:'Erro ao reenviar código.' });
    } finally { setLoading(false); }
  };

  // ── Step 3
  const onRedefinir = async (data: {nova_senha:string}) => {
    setLoading(true); setAlert(null);
    try {
      await api.post('/auth/reset-password', { email, codigo: code.join(''), nova_senha: data.nova_senha });
      setStep(4);
    } catch (err: unknown) {
      setAlert({ t:'error', msg: (err as any)?.response?.data?.detail || 'Erro ao redefinir a senha.' });
    } finally { setLoading(false); }
  };

  // ── SVG helpers
  const EyeOn  = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>;
  const EyeOff = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M17.94 17.94A10.9 10.9 0 0 1 12 20C5 20 1 12 1 12a18.6 18.6 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.1 9.1 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>;

  const STEPS_META = [
    { lbl:'EMAIL' }, { lbl:'CÓDIGO' }, { lbl:'SENHA' },
  ];

  return (
    <Overlay onClick={onClose}>
      <Modal onClick={e => e.stopPropagation()}>

        <CloseBtn onClick={onClose}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </CloseBtn>

        {/* step indicator */}
        {step < 4 && (
          <StepRow>
            {STEPS_META.map(({lbl}, idx) => {
              const s = idx + 1;
              return (
                <div key={s} style={{display:'flex',alignItems:'center'}}>
                  <div style={{position:'relative',paddingBottom:20}}>
                    <StepDot $active={step===s} $done={step>s}>
                      {step > s
                        ? <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                        : s
                      }
                    </StepDot>
                    <StepLbl>{lbl}</StepLbl>
                  </div>
                  {idx < 2 && <StepLine $done={step>s}/>}
                </div>
              );
            })}
          </StepRow>
        )}

        {/* ════ STEP 1 — Email ════ */}
        {step === 1 && (
          <>
            <IconBox>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00A3FF" strokeWidth="1.5">
                <rect x="2" y="4" width="20" height="16" rx="2"/><path d="M2 8l10 7 10-7"/>
              </svg>
            </IconBox>
            <Title>RECUPERAR SENHA</Title>
            <Desc>Introduz o teu email de conta.<br/>Enviaremos um código de 6 dígitos.</Desc>

            {alert && <AlertBox $t={alert.t}>⚑ {alert.msg}</AlertBox>}

            <form onSubmit={handleSubmit(onEnviarEmail as any)}>
              <FieldWrap>
                <FLabel>EMAIL DA CONTA</FLabel>
                <InputRow>
                  <InputIcon>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                      <rect x="2" y="4" width="20" height="16" rx="2"/><path d="M2 8l10 7 10-7"/>
                    </svg>
                  </InputIcon>
                  <SInput
                    type="email" placeholder="usuario@dominio.com"
                    $error={!!errors.email}
                    {...register('email',{
                      required:'Campo obrigatório',
                      pattern:{value:/\S+@\S+\.\S+/,message:'Email inválido'},
                    })}
                  />
                </InputRow>
                {errors.email && <FieldErr>⚠ {errors.email.message}</FieldErr>}
              </FieldWrap>

              <Btn type="submit" disabled={loading}>
                {loading ? 'A ENVIAR...' : 'ENVIAR CÓDIGO →'}
              </Btn>
              <Btn type="button" $outline onClick={onClose}>CANCELAR</Btn>
            </form>
          </>
        )}

        {/* ════ STEP 2 — Código ════ */}
        {step === 2 && (
          <>
            <IconBox>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00A3FF" strokeWidth="1.5">
                <rect x="5" y="2" width="14" height="20" rx="2"/>
                <path d="M12 18h.01M9 7h6M9 11h6M9 15h3"/>
              </svg>
            </IconBox>
            <Title>CÓDIGO DE VERIFICAÇÃO</Title>
            <Desc>
              Código enviado para<br/>
              <strong>{email}</strong>.<br/>
              Válido por <strong>10 minutos</strong>.
            </Desc>

            {alert && <AlertBox $t={alert.t}>⚑ {alert.msg}</AlertBox>}

            <FLabel style={{textAlign:'center',display:'block'}}>INTRODUZ O CÓDIGO</FLabel>
            <CodeGrid onPaste={handlePaste}>
              {code.map((v,i) => (
                <CodeBox
                  key={i} id={`rc-${i}`} maxLength={1} value={v} $filled={!!v}
                  inputMode="numeric"
                  onChange={e => handleCodeInput(i, e.target.value)}
                  onKeyDown={e => handleCodeKey(i, e)}
                  autoFocus={i===0}
                />
              ))}
            </CodeGrid>

            <Btn type="button" onClick={onVerificarCodigo} disabled={loading||code.join('').length<6}>
              {loading ? 'A VERIFICAR...' : 'VERIFICAR →'}
            </Btn>

            <ResendRow>
              Não recebeste?{' '}
              <ResendBtn onClick={onReenviar} disabled={loading||resends>=3}>
                REENVIAR{resends>0&&` (${resends}/3)`}
              </ResendBtn>
            </ResendRow>

            <Btn type="button" $outline onClick={()=>{setStep(1);setAlert(null);reset();}}>
              ← VOLTAR
            </Btn>
          </>
        )}

        {/* ════ STEP 3 — Nova Senha ════ */}
        {step === 3 && (
          <>
            <IconBox>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00A3FF" strokeWidth="1.5">
                <rect x="5" y="11" width="14" height="10" rx="2"/>
                <path d="M8 11V7a4 4 0 0 1 8 0v4"/>
                <circle cx="12" cy="16" r="1" fill="#00A3FF"/>
              </svg>
            </IconBox>
            <Title>NOVA SENHA</Title>
            <Desc>Mínimo 8 caracteres,<br/>maiúsculas, minúsculas e número.</Desc>

            {alert && <AlertBox $t={alert.t}>⚑ {alert.msg}</AlertBox>}

            <form onSubmit={handleSubmit(onRedefinir as any)}>
              <FieldWrap>
                <FLabel>NOVA SENHA</FLabel>
                <InputRow>
                  <InputIcon>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                      <rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>
                    </svg>
                  </InputIcon>
                  <SInput
                    type={showPass?'text':'password'} placeholder="••••••••"
                    $error={!!errors.nova_senha}
                    {...register('nova_senha',{
                      required:'Campo obrigatório',
                      minLength:{value:8,message:'Mínimo 8 caracteres'},
                      pattern:{value:/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,message:'Precisa de maiúsculas, minúsculas e número'},
                    })}
                  />
                  <EyeBtn type="button" onClick={()=>setShowPass(v=>!v)} tabIndex={-1}>
                    {showPass?<EyeOn/>:<EyeOff/>}
                  </EyeBtn>
                </InputRow>
                {errors.nova_senha && <FieldErr>⚠ {errors.nova_senha.message}</FieldErr>}
              </FieldWrap>

              <FieldWrap>
                <FLabel>CONFIRMAR SENHA</FLabel>
                <InputRow>
                  <InputIcon>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                      <path d="M9 12l2 2 4-4"/><rect x="5" y="11" width="14" height="10" rx="2"/>
                      <path d="M8 11V7a4 4 0 0 1 8 0v4"/>
                    </svg>
                  </InputIcon>
                  <SInput
                    type={showConf?'text':'password'} placeholder="••••••••"
                    $error={!!errors.confirmar}
                    {...register('confirmar',{
                      required:'Campo obrigatório',
                      validate: v=>v===watch('nova_senha')||'As senhas não coincidem',
                    })}
                  />
                  <EyeBtn type="button" onClick={()=>setShowConf(v=>!v)} tabIndex={-1}>
                    {showConf?<EyeOn/>:<EyeOff/>}
                  </EyeBtn>
                </InputRow>
                {errors.confirmar && <FieldErr>⚠ {errors.confirmar.message}</FieldErr>}
              </FieldWrap>

              <Btn type="submit" disabled={loading}>
                {loading?'A GUARDAR...':'REDEFINIR SENHA →'}
              </Btn>
            </form>
          </>
        )}

        {/* ════ STEP 4 — Sucesso ════ */}
        {step === 4 && (
          <div style={{textAlign:'center',padding:'8px 0'}}>
            <SuccessCircle>
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#00C853" strokeWidth="2.5">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </SuccessCircle>
            <Title>SENHA REDEFINIDA</Title>
            <Desc style={{marginBottom:28}}>
              A tua senha foi atualizada com sucesso.<br/>
              Podes agora fazer login com a nova senha.
            </Desc>
            <Btn type="button" onClick={onClose}>IR PARA O LOGIN →</Btn>
          </div>
        )}

      </Modal>
    </Overlay>
  );
}