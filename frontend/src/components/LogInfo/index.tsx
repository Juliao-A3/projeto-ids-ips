import {
    LogMain,
    LogRow,
    LogContent,
    Severity,
    Actions,
    LogContainer,
    Divider
} from './styles'

interface LogInfoProps {
    data: {
        // formato banco de dados
        id?: number;
        timestamp?: string;
        src_ip?: string;
        dest_ip?: string;
        dst_ip?: string;       // ← formato Scapy
        protocolo?: string;
        severidade?: string;
        tipo?: string;         // ← formato Scapy: 'anomalia' | 'normal'
        src_port?: number;     // ← formato Scapy
        dst_port?: number;     // ← formato Scapy
        cor?: string;          // ← formato Scapy: 'red' | 'green'
        bloqueado?: boolean;   // ← formato Scapy
        interface?: string;    // ← formato Scapy
        status?: string;
    };
}

export function LogInfo({ data }: LogInfoProps) {
    const dateStr = data.timestamp
        ? new Date(data.timestamp).toLocaleTimeString()
        : '-';

    // compatível com banco e com Scapy
    const destIp   = data.dest_ip || data.dst_ip || '-';
    const protocolo = data.protocolo || '-';

    const tipoNormalizado = (data.tipo || '').toLowerCase();
    const isAttackEvent = tipoNormalizado === 'ataque' || tipoNormalizado === 'anomalia' || tipoNormalizado === 'alerta';

    // Mostrar exatamente como no terminal: NORMAL ou ALERTA
    const tipoExibicao =
        tipoNormalizado === 'normal' ? 'NORMAL' :
        isAttackEvent ? 'ALERTA' :
        (data.severidade ? data.severidade.toUpperCase() : '-');

    // cor da severidade
    const sevColor =
        tipoExibicao === 'ALERTA'                                               ? '#EF4444' :
        tipoExibicao === 'NORMAL' || tipoExibicao === 'BAIXA'                  ? '#00C853' :
        tipoExibicao === 'MEDIA'                                                ? '#00A3FF' :
        tipoExibicao === 'CRITICA' || tipoExibicao === 'ALTA'                  ? '#EF4444' : '#64748B';

    return (
        <LogContainer>
            <LogMain>
                <LogContent>
                    <LogRow>
                        <span>{dateStr}</span>
                        <span>
                            {data.src_ip || '-'}
                            {data.src_port ? `:${data.src_port}` : ''}
                        </span>
                        <span>
                            {destIp}
                            {data.dst_port ? `:${data.dst_port}` : ''}
                        </span>
                        <span>{protocolo}</span>
                        <Severity style={{ color: sevColor, borderColor: `${sevColor}44`, background: `${sevColor}12` }}>
                            {data.bloqueado ? '🔒 BLOQUEADO' : tipoExibicao}
                        </Severity>
                        <Actions>
                            <button>DETALHES</button>
                        </Actions>
                    </LogRow>
                </LogContent>
            </LogMain>
            <Divider />
        </LogContainer>
    );
}