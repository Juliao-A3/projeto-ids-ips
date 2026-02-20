import { Container, Option } from './styles';

interface RadioToggleProps {
  options: string[];
  selected: string;
  onChange: (value: string) => void;
}

export function RadioToggle({ options, selected, onChange }: RadioToggleProps) {
  return (
    <Container>
      {options.map((option) => (
        <Option
          key={option}
          isSelected={selected === option}
          onClick={() => onChange(option)}
        >
          {option}
        </Option>
      ))}
    </Container>
  );
}