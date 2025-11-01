import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { ModalProvider } from './components/modals/ModalProvider.jsx';

import AuthModal from './pages/LoginPage/index.jsx';
import AccountModal from './components/modals/AccountModal/';
import SettingsModal from './components/modals/SettingsModal/';
import MovieModal from './components/modals/MovieModal/';

const registry = {
  auth: AuthModal,
  account: AccountModal,
  settings: SettingsModal,
  movie: MovieModal,
};

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ModalProvider >
      <App />
    </ModalProvider>
  </StrictMode>,
)
