import { Container, Label, InputWrapper, Input, AutoDetect, Description } from './styles';

interface NumberInputProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  description?: string;
  autoDetectValue?: number; // Novo: valor do backend
  min?: number;
  max?: number;
}

export function NumberInput({ 
  label, 
  value, 
  onChange, 
  description,
  autoDetectValue,
  min,
  max 
}: NumberInputProps) {
  return (
    <Container>
      <Label>{label}</Label>
      <InputWrapper>
        <Input
          type="number"
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          min={min}
          max={max}
        />
        {autoDetectValue && (
          <AutoDetect>AUTO-DETECT: {autoDetectValue}</AutoDetect>
        )}
      </InputWrapper>
      {description && <Description>{description}</Description>}
    </Container>
  );
}