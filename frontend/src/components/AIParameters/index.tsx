import { useState } from "react";
import { CardContainer, ControlsGrid, ControlWrapper, LabelRow, RangeLabels, SectionHeader, StyledSlider, ValueDisplay } from "./styles";


export function AIParameters(){
    const [confidence, setConfidence] = useState(85);
    const [sensitivity, setSensitivity] = useState(2); // 1: Baixa, 2: Média, 3: Crítica

    const getSensitivityLabel = (val: string | number) => {
        if (val === "1") return "BAIXA";
        if (val === "3") return "CRÍTICA";
        return "MÉDIA";
    };

    return (
        <CardContainer>
        <SectionHeader>
            <span>⚛</span> PARÂMETROS DA IA
        </SectionHeader>

        <ControlsGrid>
            {/* Limiar de Confiança */}
            <ControlWrapper>
            <LabelRow>
                <span>LIMIAR DE CONFIANÇA</span>
                <ValueDisplay>{confidence}%</ValueDisplay>
            </LabelRow>
            <StyledSlider 
                min={0} max={100} 
                value={confidence} 
                onChange={(e) => setConfidence(Number(e.target.value))} 
            />
            <RangeLabels>
                <span>PERMISSIVO</span>
                <span>RIGOROSO</span>
            </RangeLabels>
            </ControlWrapper>

            {/* Sensibilidade de Anomalia */}
            <ControlWrapper>
            <LabelRow>
                <span>SENSIBILIDADE DE ANOMALIA</span>
                <ValueDisplay color="#f1c40f">
                {getSensitivityLabel(sensitivity)}
                </ValueDisplay>
            </LabelRow>
            <StyledSlider 
                min={1} max={3} step={1}
                value={sensitivity}
                onChange={(e) => setSensitivity(Number(e.target.value))}
            />
            <RangeLabels>
                <span>BAIXA</span>
                <span>CRÍTICA</span>
            </RangeLabels>
            </ControlWrapper>
        </ControlsGrid>
        </CardContainer>
  );
};