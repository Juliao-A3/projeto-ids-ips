import { useState } from 'react';
import { UserTable } from '../UserTable';
import { PermissionsSection } from '../PermissionsSection';
import { Modal } from '../Modal';
import { AddUserForm } from '../AddUserForm';
import {
  Container,
  Header,
  Title,
  AddButton,
  Content,
  Footer,
  RestoreButton,
  SaveButton
} from './styles';

export function UserManagement() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleAddUser = (userData: any) => {
    console.log('Novo usuário:', userData);
    // Aqui você enviaria os dados para o backend
    setIsModalOpen(false);
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
        <UserTable />
        <PermissionsSection />
      </Content>

      <Footer>
        <RestoreButton>RESTAURAR PADRÕES</RestoreButton>
        <SaveButton>SALVAR ALTERAÇÕES</SaveButton>
      </Footer>

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