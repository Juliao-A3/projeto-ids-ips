// ─── Animations ───────────────────────────────────────────────────────────────
const fadeIn  = keyframes`from{opacity:0}to{opacity:1}`;
const slideUp = keyframes`from{opacity:0;transform:translateY(20px) scale(.97)}to{opacity:1;transform:translateY(0) scale(1)}`;
const scan    = keyframes`0%{top:-10%}100%{top:110%}`;
import styled, { keyframes, css } from 'styled-components';
// ─── Layout 

export const Overlay = styled.div`
  position:fixed;inset:0;z-index:9999;
  background:rgba(7,10,16,.85);
  backdrop-filter:blur(6px);
  display:flex;
  align-items:center;
  justify-content:center;
  animation:${fadeIn} .2s ease;
`;

export const Modal = styled.div`
  position:relative;
  width:390px;
  background:${({theme})=>theme.colors.surface};
  border:1px solid ${({theme})=>theme.colors.border};
  border-radius:6px;
  padding:40px 34px 30px;
  overflow:hidden;
  box-shadow:0 0 60px ${({theme})=>theme.colors.primary}18,0 30px 80px rgba(0,0,0,.7);
  animation:${slideUp} .3s ease both;
  &::before{
    content:'';
    position:absolute;
    top:-1px;
    left:-1px;
    right:-1px;
    height:2px;
    background:linear-gradient(90deg,transparent,#00A3FF,transparent);
    border-radius:6px 6px 0 0;
  }
  &::after{
    content:'';
    position:absolute;
    left:0;
    right:0;
    height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,163,255,.15),transparent);
    animation:${scan} 5s linear infinite;pointer-events:none;
  }
`;

export const CloseBtn = styled.button`
  position:absolute;
  top:14px;
  right:14px;
  background:none;
  border:none;
  color:${({theme})=>theme.colors.text.muted};
  cursor:pointer;
  padding:4px;
  display:flex;
  align-items:center;
  border-radius:4px;
  transition:color .2s,background .2s;
  &:hover{color:${({theme})=>theme.colors.text.primary};
  background:${({theme})=>theme.colors.border};}
`;

// ─── Step Indicator
export const StepRow = styled.div`
  display:flex;
  align-items:center;
  justify-content:center;
  margin-bottom:32px;
`;
export const StepDot = styled.div<{$active:boolean;$done:boolean}>`
  position:relative;
  width:30px;
  height:30px;
  border-radius:50%;
  display:flex;
  align-items:center;
  justify-content:center;
  font-family:'Share Tech Mono',monospace;font-size:11px;
  font-weight:700;
  transition:all .3s;
  background:${({$active,$done,theme})=>$done?theme.colors.success:$active?theme.colors.primary:'transparent'};
  border:1px solid ${({$active,$done,theme})=>$done?theme.colors.success:$active?theme.colors.primary:theme.colors.border};
  color:${({$active,$done})=>($active||$done)?'#fff':'#64748B'};
`;

export const StepLbl = styled.div`
  position:absolute;
  bottom:-18px;
  left:50%;
  transform:translateX(-50%);
  font-family:'Share Tech Mono',monospace;
  font-size:8px;
  color:${({theme})=>theme.colors.text.muted};
  white-space:nowrap;
  letter-spacing:1px;
`;

export const StepLine = styled.div<{$done:boolean}>`
  width:44px;
  height:1px;
  background:${({$done,theme})=>$done?theme.colors.success:theme.colors.border};
  transition:background .4s;
`;

// ─── Icon / Typography 
export const IconBox = styled.div`
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background:rgba(0,163,255,.08);
  border:1px solid rgba(0,163,255,.25);
  display: flex;
  align-items:center;
  justify-content: center;
  margin:0 auto 16px;
`;

export const Title = styled.div`
  font-family:'Orbitron',monospace;
  font-size:14px;
  font-weight:700;
  color:${({theme})=>theme.colors.text.primary};letter-spacing:2px;
  text-align:center;
  margin-bottom:6px;
`;

export const Desc = styled.div`
  font-family:'Share Tech Mono',monospace;
  font-size:10px;
  color:${({theme})=>theme.colors.text.muted};
  text-align:center;
  line-height:1.8;
  margin-bottom:22px;
  letter-spacing:.4px;
  strong{color:${({theme})=>theme.colors.primary};}
`;

// ─── Form 
export const FLabel = styled.label`
  font-family:'Share Tech Mono',monospace;
  font-size: 10px;
  letter-spacing: 2px;
  color:${({theme})=>theme.colors.text.muted};
  display: block;
  margin-bottom: 6px;
`;

export const InputRow = styled.div`
    position:relative;
    display:flex;
    align-items:center;
`;

export const InputIcon = styled.span`
  position:absolute;
  left:12px;
  color:${({theme})=>theme.colors.text.muted};
  display:flex;
  align-items:center;
  pointer-events:none;
`;

export const EyeBtn = styled.button`
  position:absolute;
  right:10px;
  background:none;
  border:none;
  padding:4px;
  color:${({theme})=>theme.colors.text.muted};cursor:pointer;
  display:flex;
  align-items:center;
  transition:color .2s;
  &:hover{color:${({theme})=>theme.colors.primary};}
`;

export const SInput = styled.input<{$error?:boolean}>`
  width:100%;
  background:${({theme})=>theme.colors.background};
  border:1px solid ${({$error,theme})=>$error?theme.colors.danger:theme.colors.border};
  border-radius:4px;color:${({theme})=>theme.colors.text.primary};
  font-family:'Share Tech Mono',monospace;
  font-size:13px;
  padding:10px 38px 10px 36px;
  outline:none;
  transition:border-color .2s,box-shadow .2s;
  &::placeholder{color:${({theme})=>theme.colors.text.muted};font-size:11px;}
  &:focus{border-color:${({theme})=>theme.colors.primary};box-shadow:0 0 0 2px ${({theme})=>theme.colors.primary}22;}
`;

export const FieldWrap = styled.div`
    margin-bottom:14px;
`;

export const FieldErr = styled.div`
  font-family:'Share Tech Mono',monospace;font-size:10px;
  color:${({theme})=>theme.colors.danger};margin-top:4px;
`;

// ─── Code 

export const CodeGrid = styled.div`
  display:flex;gap:8px;justify-content:center;margin:4px 0 18px;
`;

export const CodeBox = styled.input<{$filled:boolean}>`
  width:46px;
  height:54px;
  border-radius:6px;
  background:${({theme})=>theme.colors.background};
  border:1px solid ${({$filled,theme})=>$filled?theme.colors.primary:theme.colors.border};
  color:${({theme})=>theme.colors.text.primary};
  font-family:'Orbitron',monospace;
  font-size:20px;
  font-weight:700;
  text-align:center;
  outline:none;
  caret-color:transparent;
  transition:border-color .2s,box-shadow .2s;
  &:focus{border-color:${({theme})=>theme.colors.primary};
  box-shadow:0 0 0 2px ${({theme})=>theme.colors.primary}25;}
`;

// ─── Alert ────────────────────────────────────────────────────────────────────
export const AlertBox = styled.div<{$t:'error'|'success'|'info'}>`
  padding:10px 14px;
  border-radius:4px;
  margin-bottom:14px;
  font-family:'Share Tech Mono',monospace;
  font-size:10px;letter-spacing:.4px;line-height:1.6;
  ${({$t,theme})=>$t==='error'?css`
    background:${theme.colors.danger}10;
    border:1px solid ${theme.colors.danger}40;
    border-left:3px solid ${theme.colors.danger};
    color:${theme.colors.danger};
  `:$t==='success'?css`
    background:${theme.colors.success}10;
    border:1px solid ${theme.colors.success}40;
    border-left:3px solid ${theme.colors.success};
    color:${theme.colors.success};
  `:css`
    background:${theme.colors.primary}08;
    border:1px solid ${theme.colors.primary}30;
    border-left:3px solid ${theme.colors.primary};
    color:${theme.colors.primary};
  `}
`;

// ─── Buttons 

export const Btn = styled.button<{$outline?:boolean}>`
  width:100%;
  padding:12px;
  border-radius:4px;
  font-family:'Orbitron',monospace;
  font-size:11px;
  font-weight:700;
  letter-spacing:2px;
  cursor:pointer;
  transition:all .2s;
  margin-top:6px;
  ${({$outline,theme})=>$outline?css`
    background:transparent;
    border:1px solid ${theme.colors.border};
    color:${theme.colors.text.muted};
    &:hover{border-color:${theme.colors.primary};color:${theme.colors.primary};}
  `:css`
    background:${theme.colors.primary};
    border:1px solid ${theme.colors.primary};
    color:#fff;
    &:hover:not(:disabled){box-shadow:0 0 20px ${theme.colors.primary}55;transform:translateY(-1px);}
  `}
  &:disabled{opacity:.5;cursor:wait;transform:none !important;}
`;

export const ResendRow = styled.div`
  text-align:center;margin-top:12px;
  font-family:'Share Tech Mono',monospace;font-size:10px;
  color:${({theme})=>theme.colors.text.muted};
`;

export const ResendBtn = styled.button`
  background:none;
  border:none;
  color:${({theme})=>theme.colors.primary};
  font-family:'Share Tech Mono',monospace;
  font-size:10px;
  cursor:pointer;
  padding:0 4px;
  transition:opacity .2s;
  &:hover{opacity:.7;text-decoration:underline;}
  &:disabled{opacity:.4;cursor:not-allowed;text-decoration:none;}
`;

export const SuccessCircle = styled.div`
  width:68px;
  height:68px;
  border-radius:50%;
  background:${({theme})=>theme.colors.success}15;
  border:2px solid ${({theme})=>theme.colors.success}55;
  display:flex;
  align-items:center;
  justify-content:center;
  margin:0 auto 18px;
`;