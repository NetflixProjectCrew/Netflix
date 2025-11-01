import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { createPortal } from 'react-dom';

// === 1) Контекст/хук =========================================================
const ModalContext = createContext(null);

export const useModal = () => {
  const ctx = useContext(ModalContext);
  if (!ctx) throw new Error('useModal must be used within <ModalProvider>');
  return ctx;
};

// Тип модалки: { name: string, props?: object }
const initialState = null;

// === 2) Провайдер ============================================================
/**
 * ModalProvider
 * @param {object} props
 * @param {Record<string, React.ComponentType<any>>} props.registry - реестр модалок: { auth: AuthModal, settings: SettingsModal, ... }
 * @param {React.ReactNode} props.children
 */
export function ModalProvider({ registry = {}, children }) {
  const [modal, setModal] = useState(initialState); // {name, props}

  const openModal = useCallback((name, props = {}) => {
    if (!registry[name]) {
      console.warn(`[ModalProvider] Modal "${name}" is not registered`);
      return;
    }
    setModal({ name, props });
  }, [registry]);

  const closeModal = useCallback(() => {
    setModal(null);
  }, []);

  const toggleModal = useCallback((name, props = {}) => {
    setModal(curr => (curr?.name === name ? null : { name, props }));
  }, []);

  // Esc для закрытия
  useEffect(() => {
    if (!modal) return;
    const onKeyDown = (e) => {
      if (e.key === 'Escape') closeModal();
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [modal, closeModal]);

  // Лочим скролл body, когда модалка открыта
  useEffect(() => {
    if (modal) {
      const prev = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      return () => { document.body.style.overflow = prev; };
    }
  }, [modal]);

  const value = useMemo(() => ({
    modal, openModal, closeModal, toggleModal,
    isOpen: (name) => modal?.name === name,
  }), [modal, openModal, closeModal, toggleModal]);

  // Текущая модалка из реестра
  const CurrentModal = modal ? registry[modal.name] : null;

  return (
    <ModalContext.Provider value={value}>
      {children}

      {/* Портал с оверлеем и контейнером модалки */}
      {modal && CurrentModal && createPortal(
        <div
          aria-modal="true"
          role="dialog"
          className="fixed inset-0 z-[1000] flex items-center justify-center"
        >
          {/* overlay */}
          <div
            className="absolute inset-0 bg-black/60"
            onClick={closeModal}
          />
          {/* modal container */}
          <div className="relative z-[1001] w-[min(92vw,640px)] max-h-[92vh] overflow-auto rounded-2xl bg-white p-6 shadow-2xl dark:bg-neutral-900">
            <CurrentModal {...(modal.props || {})} onClose={closeModal} />
          </div>
        </div>,
        document.body
      )}
    </ModalContext.Provider>
  );
}