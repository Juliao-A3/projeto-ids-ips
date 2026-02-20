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
  const [role, setRole] = useState('ANALISTA');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [forcePasswordChange, setForcePasswordChange] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ name, email, role, password, forcePasswordChange });
  };

  // Calcula força da senha (simplificado)
  const passwordStrength = password.length > 8 ? 80 : password.length > 4 ? 50 : 20;

  return (
    <Form onSubmit={handleSubmit}>
      <FormGroup>
        <Label>NOME COMPLETO</Label>
        <Input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="ex: Roberto Silva"
          required
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
        />
      </FormGroup>

      <FormGroup>
        <Label>NÍVEL DE ACESSO</Label>
        <Select value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="ADMIN">Administrador</option>
          <option value="ANALISTA">Analista</option>
          <option value="OPERADOR">Operador</option>
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
          />
          <PasswordToggle onClick={() => setShowPassword(!showPassword)}>
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

      <CheckboxGroup>
        <ToggleSwitch
          checked={forcePasswordChange}
          onChange={setForcePasswordChange}
        />
        <span>Forçar troca de senha no primeiro acesso</span>
      </CheckboxGroup>

      <ButtonGroup>
        <CancelButton type="button" onClick={onCancel}>
          CANCELAR
        </CancelButton>
        <SubmitButton type="submit">
          CRIAR USUÁRIO
        </SubmitButton>
      </ButtonGroup>
    </Form>
  );
}