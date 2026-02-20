import { Container, Label, StyledTextArea, Description } from './styles';

interface TextAreaProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  description?: string;
  rows?: number;
}

export function TextArea({ 
  label, 
  value, 
  onChange, 
  placeholder,
  description,
  rows = 8
}: TextAreaProps) {
  return (
    <Container>
      <Label>{label}</Label>
      <StyledTextArea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        rows={rows}
      />
      {description && <Description>{description}</Description>}
    </Container>
  );
}