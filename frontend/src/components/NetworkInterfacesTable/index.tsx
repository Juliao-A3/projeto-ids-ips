import { useState } from 'react';
import { ToggleSwitch } from '../ToggleSwitch';
import {
  TableContainer,
  Table,
  TableHeader,
  TableHeaderCell,
  TableBody,
  TableRow,
  TableCell,
  StatusBadge,
  ToggleCell
} from './styles';

// depois virão do backend fastapi Ngola trabalha 😂
const interfaces = [
  {
    id: 1,
    name: 'eth0',
    ip: '192.168.1.50',
    status: 'CONECTADO',
    speed: '1000 Mbps',
    active: true
  },
  {
    id: 2,
    name: 'eth1',
    ip: '10.0.0.12',
    status: 'DESCONECTADO',
    speed: '---',
    active: false
  },
  {
    id: 3,
    name: 'wlan0',
    ip: '172.16.0.20',
    status: 'STANDBY',
    speed: '300 Mbps',
    active: true
  }
];

export function NetworkInterfacesTable() {
  const [interfaceStates, setInterfaceStates] = useState(() => {
    const initial: Record<number, boolean> = {};
    interfaces.forEach(iface => {
      initial[iface.id] = iface.active;
    });
    return initial;
  });

  const toggleInterface = (id: number) => {
    setInterfaceStates(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  return (
    <TableContainer>
      <Table>
        <TableHeader>
          <tr>
            <TableHeaderCell>ATIVA</TableHeaderCell>
            <TableHeaderCell>INTERFACE</TableHeaderCell>
            <TableHeaderCell>ENDEREÇO IP</TableHeaderCell>
            <TableHeaderCell>STATUS</TableHeaderCell>
            <TableHeaderCell>VELOCIDADE</TableHeaderCell>
          </tr>
        </TableHeader>
        <TableBody>
          {interfaces.map((iface) => (
            <TableRow key={iface.id}>
              <ToggleCell>
                <ToggleSwitch
                  checked={interfaceStates[iface.id]}
                  onChange={() => toggleInterface(iface.id)}
                />
              </ToggleCell>
              <TableCell>{iface.name}</TableCell>
              <TableCell>{iface.ip}</TableCell>
              <TableCell>
                <StatusBadge status={iface.status}>
                  {iface.status}
                </StatusBadge>
              </TableCell>
              <TableCell>{iface.speed}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}