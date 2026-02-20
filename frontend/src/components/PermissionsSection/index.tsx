import { ToggleSwitch } from '../ToggleSwitch';
import { Shield } from 'lucide-react';
import {
  Container,
  Header,
  Title,
  Grid,
  Column,
  ColumnTitle,
  PermissionItem,
  PermissionHeader,
  PermissionTitle,
  PermissionDescription
} from './styles';
import { useState } from 'react';

// Dados q viram do back depois
const modulePermissions = [
  {
    id: 1,
    title: 'Acesso ao Motor Suricata',
    description: 'Permite acessar e configurar as IDS.',
    enabled: false
  },
  {
    id: 2,
    title: 'Gerenciamento de IA',
    description: 'Controle total dos modelos de detecção.',
    enabled: false
  },
  {
    id: 3,
    title: 'Configuração de Rede',
    description: 'Acesso às configurações de interfaces.',
    enabled: false
  }
];

const systemPermissions = [
  {
    id: 4,
    title: 'Visualização de Logs Sensíveis',
    description: 'Ver logs com dados confidenciais.',
    enabled: false
  },
  {
    id: 5,
    title: 'Exportação de Dados',
    description: 'Exportar relatórios e análises em CSV.',
    enabled: false
  },
  {
    id: 6,
    title: 'Gestão de Alertas Críticos',
    description: 'Gerenciar alertas de alta prioridade.',
    enabled: false
  }
];

export function PermissionsSection() {
  const [permissions, setPermissions] = useState(() => {
    const initial: Record<number, boolean> = {};
    [...modulePermissions, ...systemPermissions].forEach(p => {
      initial[p.id] = p.enabled;
    });
    return initial;
  });

  const togglePermission = (id: number) => {
    setPermissions(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  return (
    <Container>
      <Header>
        <Title><Shield size={15}/> PERMISSÕES GRANULARES (Usuario a editar)</Title>
      </Header>

      <Grid>
        <Column>
          <ColumnTitle>CONTROLES DE MÓDULOS</ColumnTitle>
          {modulePermissions.map((permission) => (
            <PermissionItem key={permission.id}>
              <PermissionHeader>
                <div>
                  <PermissionTitle>{permission.title}</PermissionTitle>
                  <PermissionDescription>
                    {permission.description}
                  </PermissionDescription>
                </div>
                <ToggleSwitch 
                    checked={permissions[permission.id]}
                    onChange={() => togglePermission(permission.id)}
                />
              </PermissionHeader>
            </PermissionItem>
          ))}
        </Column>

        <Column>
          <ColumnTitle>PRIVILÉGIOS DO SISTEMA</ColumnTitle>
          {systemPermissions.map((permission) => (
            <PermissionItem key={permission.id}>
              <PermissionHeader>
                <div>
                  <PermissionTitle>{permission.title}</PermissionTitle>
                  <PermissionDescription>
                    {permission.description}
                  </PermissionDescription>
                </div>
                <ToggleSwitch 
                   checked={permissions[permission.id]}
                   onChange={() => togglePermission(permission.id)}
                />
              </PermissionHeader>
            </PermissionItem>
          ))}
        </Column>
      </Grid>
    </Container>
  );
}