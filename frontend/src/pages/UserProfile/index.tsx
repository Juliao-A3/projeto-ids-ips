import { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { useAuth } from '../../../src/contexts/AuthContext';
import {
  Container, ProfileCard, Avatar, ProfileInfo, ProfileName,
  RoleBadge, MemberSince, InfoCard, SectionTitle, FieldGroup,
  FieldLabel, FieldValue, FieldInput, RoleNote,
  ErrorMessage, SuccessMessage, ButtonGroup,
  CancelButton, SaveButton, EditButton,
  MainContent
} from './styles';

type Perfil = {
  id:        number;
  nome:      string;
  email:     string;
  role:      string;
  criado_em: string;
};

export function UserProfile() {
  const { setUser }               = useAuth();
  const [perfil, setPerfil]       = useState<Perfil | null>(null);
  const [loading, setLoading]     = useState(true);
  const [editing, setEditing]     = useState(false);
  const [saving, setSaving]       = useState(false);
  const [nome, setNome]           = useState('');
  const [email, setEmail]         = useState('');
  const [error, setError]         = useState('');
  const [success, setSuccess]     = useState('');

  useEffect(() => {
    api.get('/auth/me')
      .then(r => {
        setPerfil(r.data);
        setNome(r.data.nome);
        setEmail(r.data.email);
      })
      .catch(() => setError('Erro ao carregar perfil'))
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    try {
      setSaving(true);
      setError('');
      const res = await api.put('/auth/me', { nome, email });
      setPerfil(res.data);

      localStorage.setItem('user_name', res.data.nome);
      const initials = res.data.nome
        .trim().split(/\s+/)
        .map((w: string) => w[0]).join('')
        .toUpperCase().slice(0, 2);
      setUser({ name: res.data.nome, initials, role: res.data.role ?? perfil?.role ?? '' });

      setSuccess('Perfil atualizado com sucesso!');
      setEditing(false);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao guardar');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditing(false);
    setNome(perfil?.nome || '');
    setEmail(perfil?.email || '');
    setError('');
  };

  const roleColor = (role: string) => {
    if (role === 'admin')    return '#ef4444';
    if (role === 'analista') return '#00A3FF';
    return '#00C853';
  };

  const formatDate = (iso: string) => {
    if (!iso) return '-';
    return new Date(iso).toLocaleDateString('pt-PT', {
      day: '2-digit', month: 'long', year: 'numeric'
    });
  };

  const initials = perfil?.nome
    .trim().split(/\s+/)
    .map(w => w[0]).join('')
    .toUpperCase().slice(0, 2) || '??';

  if (loading) return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      height: '200px', color: '#64748B',
      fontFamily: "'Share Tech Mono', monospace", fontSize: '12px'
    }}>
      A CARREGAR PERFIL...
    </div>
  );

  return (
  <Container>
    <MainContent>
      <ProfileCard>
        <Avatar>{initials}</Avatar>
        <ProfileInfo>
          <ProfileName>{perfil?.nome}</ProfileName>
          <RoleBadge $color={roleColor(perfil?.role || '')}>
            NÍVEL: {perfil?.role.toUpperCase()}
          </RoleBadge>
          <MemberSince>
            MEMBRO DESDE {formatDate(perfil?.criado_em || '')}
          </MemberSince>
        </ProfileInfo>
      </ProfileCard>

      <InfoCard>
        <SectionTitle>INFORMAÇÕES DA CONTA</SectionTitle>

        <FieldGroup>
          <FieldLabel>NOME COMPLETO</FieldLabel>
          {editing
            ? <FieldInput value={nome} onChange={e => setNome(e.target.value)} />
            : <FieldValue>{perfil?.nome}</FieldValue>
          }
        </FieldGroup>

        <FieldGroup>
          <FieldLabel>EMAIL</FieldLabel>
          {editing
            ? <FieldInput value={email} onChange={e => setEmail(e.target.value)} type="email" />
            : <FieldValue>{perfil?.email}</FieldValue>
          }
        </FieldGroup>

        <FieldGroup>
          <FieldLabel>NÍVEL DE ACESSO</FieldLabel>
          <FieldValue style={{ color: roleColor(perfil?.role || ''), fontFamily: "'Share Tech Mono', monospace" }}>
            {perfil?.role.toUpperCase()}
            <RoleNote>(apenas o administrador pode alterar)</RoleNote>
          </FieldValue>
        </FieldGroup>
      </InfoCard>

      {error   && <ErrorMessage>⚠ {error}</ErrorMessage>}
      {success && <SuccessMessage>✓ {success}</SuccessMessage>}

      <ButtonGroup>
        {editing ? (
          <>
            <CancelButton onClick={handleCancel}>CANCELAR</CancelButton>
            <SaveButton onClick={handleSave} disabled={saving}>
              {saving ? 'A GUARDAR...' : 'GUARDAR ALTERAÇÕES'}
            </SaveButton>
          </>
        ) : (
          <EditButton onClick={() => setEditing(true)}>
            EDITAR PERFIL
          </EditButton>
        )}
      </ButtonGroup>
    </MainContent>
  </Container>
);
}