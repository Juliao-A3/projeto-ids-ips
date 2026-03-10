import { useEffect, useState } from 'react';
import { Edit, Trash2, Check, X } from 'lucide-react';
import { api } from '../../services/api';
import {
  TableContainer, Table, TableHeader, TableHeaderCell,
  TableBody, TableRow, TableCell, UserInfo, UserAvatar,
  UserDetails, UserName, StatusBadge, ActionButton, Actions
} from './styles';

interface User {
  id: number;
  nome: string;
  email: string;
  role: string;
  ativo: boolean;
  criado_em: string;
}

interface UserTableProps {
  refreshTrigger?: number;
}

export function UserTable({ refreshTrigger }: UserTableProps) {
  const [users, setUsers]         = useState<User[]>([]);
  const [loading, setLoading]     = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editRole, setEditRole]   = useState('');
  const [editAtivo, setEditAtivo] = useState(true);
  const [error, setError]         = useState('');

  const fetchUsers = async () => {
    try {
      const response = await api.get('/auth/users');
      setUsers(response.data);
    } catch {
      setError('Erro ao carregar utilizadores');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchUsers(); }, [refreshTrigger]);

  const handleEdit = (user: User) => {
    setEditingId(user.id);
    setEditRole(user.role);
    setEditAtivo(user.ativo);
    setError('');
  };

  const handleSaveEdit = async (userId: number) => {
    try {
      await api.put(`/auth/users/${userId}`, {
        role: editRole,
        ativo: editAtivo
      });
      setEditingId(null);
      fetchUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao editar utilizador');
    }
  };

  const handleDelete = async (userId: number, nome: string) => {
    if (!confirm(`Tens a certeza que queres apagar ${nome}?`)) return;
    try {
      await api.delete(`/auth/users/${userId}`);
      fetchUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao apagar utilizador');
    }
  };

  if (loading) return (
    <div style={{ color: '#64748B', fontSize: '12px', fontFamily: "'Share Tech Mono', monospace", padding: '20px' }}>
      A CARREGAR UTILIZADORES...
    </div>
  );

  return (
    <TableContainer>
      {error && (
        <div style={{
          padding: '10px 14px', marginBottom: '12px',
          background: '#ef444412', border: '1px solid #ef444444',
          borderLeft: '3px solid #ef4444', borderRadius: '4px',
          fontFamily: "'Share Tech Mono', monospace", fontSize: '11px', color: '#ef4444'
        }}>
          ⚠ {error}
        </div>
      )}
      <Table>
        <TableHeader>
          <tr>
            <TableHeaderCell>UTILIZADOR</TableHeaderCell>
            <TableHeaderCell>E-MAIL</TableHeaderCell>
            <TableHeaderCell>NÍVEL DE ACESSO</TableHeaderCell>
            <TableHeaderCell>STATUS</TableHeaderCell>
            <TableHeaderCell>AÇÕES</TableHeaderCell>
          </tr>
        </TableHeader>
        <TableBody>
          {users.map((user) => {
            const avatar    = user.nome.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
            const isEditing = editingId === user.id;

            return (
              <TableRow key={user.id}>
                <TableCell>
                  <UserInfo>
                    <UserAvatar>{avatar}</UserAvatar>
                    <UserDetails>
                      <UserName>{user.nome}</UserName>
                    </UserDetails>
                  </UserInfo>
                </TableCell>

                <TableCell>{user.email}</TableCell>

                {/* ROLE — editável */}
                <TableCell>
                  {isEditing ? (
                    <select
                      value={editRole}
                      onChange={e => setEditRole(e.target.value)}
                      style={{
                        background: '#151921', border: '1px solid #262C36',
                        color: '#fff', borderRadius: '4px', padding: '4px 8px',
                        fontFamily: "'Share Tech Mono', monospace", fontSize: '11px'
                      }}
                    >
                      <option value="admin">ADMIN</option>
                      <option value="analista">ANALISTA</option>
                      <option value="operador">OPERADOR</option>
                    </select>
                  ) : (
                    <span style={{
                      fontFamily: "'Share Tech Mono', monospace", fontSize: '11px',
                      color: user.role === 'admin' ? '#ef4444' :
                             user.role === 'analista' ? '#00A3FF' : '#00C853'
                    }}>
                      {user.role.toUpperCase()}
                    </span>
                  )}
                </TableCell>

                {/* STATUS — editável */}
                <TableCell>
                  {isEditing ? (
                    <select
                      value={editAtivo ? 'ativo' : 'inativo'}
                      onChange={e => setEditAtivo(e.target.value === 'ativo')}
                      style={{
                        background: '#151921', border: '1px solid #262C36',
                        color: '#fff', borderRadius: '4px', padding: '4px 8px',
                        fontFamily: "'Share Tech Mono', monospace", fontSize: '11px'
                      }}
                    >
                      <option value="ativo">ATIVO</option>
                      <option value="inativo">INATIVO</option>
                    </select>
                  ) : (
                    <StatusBadge status={user.ativo ? 'Ativo' : 'Inativo'}>
                      {user.ativo ? 'Ativo' : 'Inativo'}
                    </StatusBadge>
                  )}
                </TableCell>

                {/* AÇÕES */}
                <TableCell>
                  <Actions>
                    {isEditing ? (
                      <>
                        {/* confirmar edição */}
                        <ActionButton
                          title="Guardar"
                          onClick={() => handleSaveEdit(user.id)}
                          style={{ color: '#00C853' }}
                        >
                          <Check size={16} />
                        </ActionButton>
                        {/* cancelar edição */}
                        <ActionButton
                          title="Cancelar"
                          onClick={() => setEditingId(null)}
                          style={{ color: '#ef4444' }}
                        >
                          <X size={16} />
                        </ActionButton>
                      </>
                    ) : (
                      <>
                        <ActionButton
                          title="Editar"
                          onClick={() => handleEdit(user)}
                        >
                          <Edit size={16} />
                        </ActionButton>
                        <ActionButton
                          title="Apagar"
                          onClick={() => handleDelete(user.id, user.nome)}
                          style={{ color: '#ef4444' }}
                        >
                          <Trash2 size={16} />
                        </ActionButton>
                      </>
                    )}
                  </Actions>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
}