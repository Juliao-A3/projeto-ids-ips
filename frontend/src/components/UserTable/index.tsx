import { Edit, Trash2 } from 'lucide-react';
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

//depois virá do backend
const users = [
  {
    id: 1,
    name: 'admin_aegis',
    email: 'admin@aegis-ids.local',
    role: 'ADMIN',
    status: 'Ativo',
    avatar: 'AA'
  },
  {
    id: 2,
    name: 'rjms',
    email: 'rfimurgatroyde@gmail.com',
    role: 'ANALISTA',
    status: 'Ativo',
    avatar: 'RJ'
  },
  {
    id: 3,
    name: 'r.santos',
    email: 'rsantos@aegis-defender.com',
    role: 'OPERADOR',
    status: 'Inativo',
    avatar: 'RS'
  }
];

export function UserTable() {
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
          {users.map((user) => (
            <TableRow key={user.id}>
              <TableCell>
                <UserInfo>
                  <UserAvatar>{user.avatar}</UserAvatar>
                  <UserDetails>
                    <UserName>{user.name}</UserName>
                  </UserDetails>
                </UserInfo>
              </TableCell>
              <TableCell>{user.email}</TableCell>
              <TableCell>{user.role}</TableCell>
              <TableCell>
                <StatusBadge status={user.status}>
                  {user.status}
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
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}