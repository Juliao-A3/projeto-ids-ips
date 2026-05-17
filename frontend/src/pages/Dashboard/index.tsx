import { Card } from "../../components/Cards";
import { LogCard } from "../../components/LogCard";
import { MainContent, SystemContainer } from "./styles";


export function Dashboard() {
    return (
        <SystemContainer>
            <MainContent>
                <Card/>
                <LogCard />
            </MainContent>
        </SystemContainer>
    );
  }