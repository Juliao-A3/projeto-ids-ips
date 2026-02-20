import {Routes, Route} from 'react-router-dom'
import { Dashboard } from './pages/Dashboard'
import { SystemSettings } from './pages/SystemSettings'
import { ConfigLayout } from './layouts/ConfigLayout'
import { DefaultLayout } from './layouts/DefaultLayout'
import { SuricataSettings } from './pages/SuricataSettings'
import { UserPage } from './pages/UserPage'
import { NetworkSettings } from './pages/NetworkSettings'
import { AIModelSettings } from './pages/AIModelSettings'
import { ReportsSettings } from './pages/ReportsSettings'
import { NotificationsSettings } from './pages/NotificationsSettings'

export function Router() {
    return (
        <Routes>
            <Route path='/' element={<DefaultLayout/>}>
                <Route path='/' element={<Dashboard/>}/>
            </Route>

            <Route path='/settings' element={<ConfigLayout/>}>
                <Route path='general' element={<SystemSettings/>}/>
                <Route path='user' element={<UserPage/>}/>
                <Route path='suricata' element={<SuricataSettings/>}/>
                <Route path='ai-model' element={<AIModelSettings/>}/>
                <Route path='network' element={<NetworkSettings/>}/>
                <Route path='notifications' element={<NotificationsSettings/>}/>
                <Route path='relatorio' element={<ReportsSettings/>}/>
            </Route>
        </Routes>
    )
}