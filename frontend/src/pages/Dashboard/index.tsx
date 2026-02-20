import { Card } from "../../components/Cards";
import { LogCard } from "../../components/LogCard";
import { OutputTecnico } from "../../components/OutputTecnico";
import { MainContent, SystemContainer } from "./styles";


export function Dashboard() {
    return (
        <SystemContainer>
            <MainContent>
                <Card/>
                <LogCard />
                <OutputTecnico/>
            </MainContent>
        </SystemContainer>
    );
  }