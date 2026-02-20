import { SuricataManagement } from "../../components/SuricataManagement";
import { SystemContainer, MainContent } from "./styles";

export function SuricataSettings() {
    return (
        <SystemContainer>
            <MainContent>
                <SuricataManagement />
            </MainContent>
        </SystemContainer>
    );
}