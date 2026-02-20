import React, { useState } from 'react';
import { Card, CardContent, CardHeader, Switch } from './styles';

interface SettingSwitchProps {
  title: string;
  description: string;
  initialValue?: boolean;
  onSave?: (newValue: boolean) => void; // Para usar com o Back-end depois
}

export const SettingSwitch: React.FC<SettingSwitchProps> = ({ 
  title, 
  description, 
  initialValue = false,
  onSave 
  }) => {
  const [isActive, setIsActive] = useState<boolean>(initialValue);

  const handleToggle = () => {
    const newState = !isActive;
    setIsActive(newState);
    
    if (onSave) {
      onSave(newState);
    }
  };

  return (
    <Card>
      <CardHeader>
        <strong>{title}</strong>
        <Switch 
          $isActive={isActive} 
          onClick={handleToggle} 
        />
      </CardHeader>
      
      <CardContent>
        <span>{description}</span>
      </CardContent>
    </Card>
  );
};