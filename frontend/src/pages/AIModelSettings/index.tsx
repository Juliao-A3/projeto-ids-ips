import { AIModelManagement } from "../../components/AIModelManagement";
import { SystemContainer, MainContent } from "./styles";

export function AIModelSettings() {
    return (
        <SystemContainer>
            <MainContent>
                <AIModelManagement />
            </MainContent>
        </SystemContainer>
    );
}