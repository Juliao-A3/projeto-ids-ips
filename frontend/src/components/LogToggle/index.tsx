import { ToggleSwitch } from '../ToggleSwitch';
import { Container, Label } from './styles';

interface LogToggleProps {
  label: string;
  checked: boolean;
  onChange: () => void;
}

export function LogToggle({ label, checked, onChange }: LogToggleProps) {
  return (
    <Container>
      <Label>{label}</Label>
      <ToggleSwitch checked={checked} onChange={onChange} />
    </Container>
  );
}