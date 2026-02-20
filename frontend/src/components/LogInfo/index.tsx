import {
    LogMain,
    LogRow,
    LogContent,
    Severity,
    Actions,
    LogContainer,
    Divider
} from './styles'

export function LogInfo() {
    return (
        <LogContainer>
            <LogMain>
                <LogContent>
                <LogRow>
                <span>15:30:12</span>
                <span>192.168.10.45</span>
                <span>DATABASE_SVR_02</span>
                <span>TCP/SQL</span>
                <Severity>INFO</Severity>
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