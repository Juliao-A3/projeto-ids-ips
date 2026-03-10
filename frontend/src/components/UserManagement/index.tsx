import { useState } from 'react';
import { UserTable } from '../UserTable';
import { PermissionsSection } from '../PermissionsSection';
import { Modal } from '../Modal';
import { AddUserForm } from '../AddUserForm';
import { api } from '../../services/api';
import {
  Container,
  Header,
  Title,
  AddButton,
  Content
} from './styles';

export function UserManagement() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleAddUser = async (userData: any) => {
    try {
      const response = await api.post('/auth/criar-usuario', {
        nome: userData.name,
        email: userData.email,
        senha: userData.password,
        role: userData.role.toLowerCase(),
        ativo: true
      });
      console.log('Usuário criado com sucesso:', response.data);
      setRefreshKey(prev => prev + 1); // Trigger refresh
      return response.data;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Erro ao criar usuário';
      console.error('Erro ao criar usuário:', errorMsg);
      throw new Error(errorMsg);
    }
  };

  return (
    <Container>
      <Header>
        <Title>GESTÃO DE USUÁRIOS</Title>
        <AddButton onClick={() => setIsModalOpen(true)}>
          ADICIONAR NOVO USUÁRIO
        </AddButton>
      </Header>

      <Content>
        <UserTable refreshTrigger={refreshKey} />
      </Content>

      {/* Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="ADICIONAR NOVO USUÁRIO"
      >
        <AddUserForm
          onCancel={() => setIsModalOpen(false)}
          onSubmit={handleAddUser}
        />
      </Modal>
    </Container>
  );
}