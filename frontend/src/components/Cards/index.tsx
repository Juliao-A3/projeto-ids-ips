import {
    CardContainer,
    CardContent,
    CardTitle,
    CardInfo,
    CardNum,
    CardSubtitle
} from './styles'

export function Card() {
    return (
        <CardContainer>
            <CardContent>
                <CardTitle>Alertas Totais(24H)</CardTitle>
                <CardInfo>
                    <CardNum>1,248</CardNum>
                    <CardSubtitle> 12%</CardSubtitle>
                </CardInfo>
            </CardContent>
            <CardContent>
                <CardTitle>ATAQUES BLOQUEADOS</CardTitle>
                <CardInfo>
                    <CardNum>48</CardNum>
                    <CardSubtitle> Frequencia Baixa</CardSubtitle>
                </CardInfo>
            </CardContent>
            <CardContent>
                <CardTitle>ATIVIDADE SUSPEITA</CardTitle>
                <CardInfo>
                    <CardNum>18</CardNum>
                    <CardSubtitle>NORMALIZADO</CardSubtitle>
                </CardInfo>
            </CardContent>
            <CardContent>
                <CardTitle>INDEGRIDADE DO TRAFEGO</CardTitle>
                <CardInfo>
                    <CardNum>ESTAVEL</CardNum>
                    <CardSubtitle></CardSubtitle>
                </CardInfo>
            </CardContent>
        </CardContainer>
    )
}