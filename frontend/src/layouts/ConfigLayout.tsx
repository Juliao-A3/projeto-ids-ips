import { Outlet } from 'react-router-dom'
import { HeaderConfig } from '../components/HeaderConfig'
import { MenuLateral } from '../components/MenuLateral'

export function ConfigLayout() {
  return (
    <div>
      <HeaderConfig />
      <MenuLateral />
      <Outlet />
    </div>
  )
}