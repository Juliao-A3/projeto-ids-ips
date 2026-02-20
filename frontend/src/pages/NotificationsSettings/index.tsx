import { NotificationsManagement } from "../../components/NotificationsManagement";
import { SystemContainer, MainContent } from "./styles";

export function NotificationsSettings() {
    return (
        <SystemContainer>
            <MainContent>
                <NotificationsManagement />
            </MainContent>
        </SystemContainer>
    );
}