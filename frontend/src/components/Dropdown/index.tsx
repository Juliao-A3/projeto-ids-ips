import { ChevronDown } from 'lucide-react';
import { Container, Label, Select, SelectWrapper, Description } from './styles';

interface DropdownProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: { value: string; label: string }[];
  description?: string;
  disabled?: boolean;
}

export function Dropdown({ 
  label, 
  value, 
  onChange, 
  options,
  description,
  disabled = false 
}: DropdownProps) {
  return (
    <Container>
      <Label>{label}</Label>
      <SelectWrapper>
        <Select 
          value={value} 
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
        >
          <option value="">Selecione uma interface</option>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </Select>
        <ChevronDown size={16} />
      </SelectWrapper>
      {description && <Description>{description}</Description>}
    </Container>
  );
}