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

    // severidade: vem do banco OU inferida do tipo Scapy
    const severidade = data.severidade
        || (data.tipo === 'anomalia' ? 'ALTA' : data.tipo === 'normal' ? 'BAIXA' : '-');

    // cor da severidade
    const sevColor =
        severidade === 'critica' || severidade === 'CRITICA' ? '#EF4444' :
        severidade === 'alta'    || severidade === 'ALTA'    ? '#FFAB00' :
        severidade === 'media'   || severidade === 'MEDIA'   ? '#00A3FF' :
        severidade === 'BAIXA'                               ? '#00C853' : '#64748B';

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
                            {data.bloqueado ? '🔒 BLOQUEADO' : severidade}
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