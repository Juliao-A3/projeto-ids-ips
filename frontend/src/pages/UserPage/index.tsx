import { UserManagement } from "../../components/UserManagement";
import { SystemContainer, MainContent } from "./styles";

export function UserPage() {
    return (
        <SystemContainer>
            <MainContent>
                <UserManagement />
            </MainContent>
        </SystemContainer>
    );
}
