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
        id: number;
        timestamp?: string;
        src_ip?: string;
        dest_ip?: string;
        protocolo?: string;
        severidade?: string;
        status?: string;
    };
}

export function LogInfo({ data }: LogInfoProps) {
    const dateStr = data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : '-';

    return (
        <LogContainer>
            <LogMain>
                <LogContent>
                <LogRow>
                <span>{dateStr}</span>
                <span>{data.src_ip || '-'}</span>
                <span>{data.dest_ip || '-'}</span>
                <span>{data.protocolo || '-'}</span>
                <Severity>{data.severidade || '-'}</Severity>
                <Actions>
                    <button>DETALHES</button>
                </Actions>
                </LogRow>
                </LogContent>
            </LogMain>
            <Divider/>
        </LogContainer>
    );
}