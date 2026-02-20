import { NetworkManagement } from "../../components/NetworkManagement";
import { SystemContainer, MainContent } from "./styles";

export function NetworkSettings() {
    return (
        <SystemContainer>
            <MainContent>
                <NetworkManagement />
            </MainContent>
        </SystemContainer>
    );
}