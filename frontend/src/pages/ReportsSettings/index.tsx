import { ReportsManagement } from "../../components/RelatorioManagement";
import { SystemContainer, MainContent } from "./styles";

export function ReportsSettings() {
    return (
        <SystemContainer>
            <MainContent>
                <ReportsManagement />
            </MainContent>
        </SystemContainer>
    );
}