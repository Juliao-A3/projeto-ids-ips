import { ToggleSwitch } from '../ToggleSwitch';
import {
  Card,
  CardHeader,
  CardTitle,
  CardSubtitle,
  CardStatus
} from './styles';

interface RuleSetCardProps {
  title: string;
  subtitle: string;
  status: string;
  enabled: boolean;
  onToggle: () => void;
}

export function RuleSetCard({ 
  title, 
  subtitle, 
  status, 
  enabled, 
  onToggle 
}: RuleSetCardProps) {
  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>{title}</CardTitle>
          <CardSubtitle>{subtitle}</CardSubtitle>
        </div>
        <ToggleSwitch checked={enabled} onChange={onToggle} />
      </CardHeader>
      <CardStatus enabled={enabled}>{status}</CardStatus>
    </Card>
  );
}