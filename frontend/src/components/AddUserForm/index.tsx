import { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { ToggleSwitch } from '../ToggleSwitch';
import {
  Form,
  FormGroup,
  Label,
  Input,
  Select,
  PasswordInputWrapper,
  PasswordInput,
  PasswordToggle,
  PasswordStrength,
  StrengthBar,
  StrengthBarFill,
  CheckboxGroup,
  ButtonGroup,
  CancelButton,
  SubmitButton,
} from './styles';

interface AddUserFormProps {
  onCancel: () => void;
  onSubmit: (data: any) => void;
}

export function AddUserForm({ onCancel, onSubmit }: AddUserFormProps) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('analista');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [forcePasswordChange, setForcePasswordChange] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setLoading(true);

    try {
      await onSubmit({ name, email, role, password, forcePasswordChange });
        setSuccess(true);
        setName('');
        setEmail('');
        setRole('analista');
        setPassword('');
        setTimeout(() => onCancel(), 1500);
    } catch (err: any) {
      setError(err.message || 'Erro ao criar usuário');
    } finally {
      setLoading(false);
    }
  };

  // Calcula força da senha (simplificado)
  const passwordStrength = password.length > 8 ? 80 : password.length > 4 ? 50 : 20;

  return (
    <Form onSubmit={handleSubmit}>
      {error && (
        <FormGroup style={{ backgroundColor: '#fee', borderLeft: '4px solid #f44', padding: '12px' }}>
          <span style={{ color: '#d32f2f', fontSize: '14px' }}>✗ {error}</span>
        </FormGroup>
      )}

      {success && (
        <FormGroup style={{ backgroundColor: '#efe', borderLeft: '4px solid #4caf50', padding: '12px' }}>
          <span style={{ color: '#2e7d32', fontSize: '14px' }}>✓ Usuário criado com sucesso!</span>
        </FormGroup>
      )}

      <FormGroup>
        <Label>NOME COMPLETO</Label>
        <Input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="ex: Roberto Silva"
          required
          disabled={loading}
        />
      </FormGroup>

      <FormGroup>
        <Label>E-MAIL CORPORATIVO</Label>
        <Input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="roberto@empresa.com"
          required
          disabled={loading}
        />
      </FormGroup>

      <FormGroup>
        <Label>NÍVEL DE ACESSO</Label>
        <Select value={role} onChange={(e) => setRole(e.target.value)} disabled={loading}>
          <option value="admin">Administrador</option>
          <option value="analista">Analista</option>
          <option value="operador">Operador</option>
        </Select>
      </FormGroup>

      <FormGroup>
        <Label>SENHA TEMPORÁRIA</Label>
        <PasswordInputWrapper>
          <PasswordInput
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••••••"
            required
            disabled={loading}
          />
          <PasswordToggle type='button' onClick={() => !loading && setShowPassword(!showPassword)}>
            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
          </PasswordToggle>
        </PasswordInputWrapper>
        {password && (
          <PasswordStrength>
            <span style={{ fontSize: '11px', color: '#888' }}>
              FORÇA DA SENHA: <strong>{passwordStrength > 60 ? 'FORTE' : passwordStrength > 40 ? 'MÉDIA' : 'FRACA'}</strong>
            </span>
            <StrengthBar>
              <StrengthBarFill strength={passwordStrength} />
            </StrengthBar>
          </PasswordStrength>
        )}
      </FormGroup>

      <ButtonGroup>
        <CancelButton type="button" onClick={onCancel} disabled={loading}>
          CANCELAR
        </CancelButton>
        <SubmitButton type="submit" disabled={loading}>
          {loading ? 'CRIANDO...' : 'CRIAR USUÁRIO'}
        </SubmitButton>
      </ButtonGroup>
    </Form>
  );
}