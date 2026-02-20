import { AIParameters } from "../../components/AIParameters";
import { ConfigGeral } from "../../components/ConfigCard";
import { LogIntegration } from "../../components/LogIntegration";
import { SystemContainer, MainContent} from "./styles";

export function SystemSettings() {
    return (
        <SystemContainer>
                <MainContent>
                    <ConfigGeral/>
                    <AIParameters/>
                    <LogIntegration />
                </MainContent>
        </SystemContainer>
    )
}