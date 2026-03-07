import { useEffect, useState } from 'react';
import { Edit, Trash2 } from 'lucide-react';
import { api } from '../../services/api';
import {
  TableContainer,
  Table,
  TableHeader,
  TableHeaderCell,
  TableBody,
  TableRow,
  TableCell,
  UserInfo,
  UserAvatar,
  UserDetails,
  UserName,
  StatusBadge,
  ActionButton,
  Actions
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
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await api.get('/auth/users');
        setUsers(response.data);
      } catch (error) {
        console.error('Erro ao buscar usuários:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, [refreshTrigger]);

  if (loading) {
    return <div>Carregando usuários...</div>;
  }
  return (
    <TableContainer>
      <Table>
        <TableHeader>
          <tr>
            <TableHeaderCell>USUÁRIO</TableHeaderCell>
            <TableHeaderCell>E-MAIL</TableHeaderCell>
            <TableHeaderCell>NÍVEL DE ACESSO</TableHeaderCell>
            <TableHeaderCell>STATUS</TableHeaderCell>
            <TableHeaderCell>AÇÕES</TableHeaderCell>
          </tr>
        </TableHeader>
        <TableBody>
          {users.map((user) => {
            const avatar = user.nome.split(' ').map(n => n[0]).join('').toUpperCase();
            const status = user.ativo ? 'Ativo' : 'Inativo';
            const roleDisplay = user.role === 'admin' ? 'ADMIN' : user.role === 'analista' ? 'ANALISTA' : 'OPERADOR';
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
                <TableCell>{roleDisplay}</TableCell>
                <TableCell>
                  <StatusBadge status={status}>
                    {status}
                  </StatusBadge>
                </TableCell>
                <TableCell>
                  <Actions>
                    <ActionButton>
                      <Edit size={16} />
                    </ActionButton>
                    <ActionButton>
                      <Trash2 size={16} />
                    </ActionButton>
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