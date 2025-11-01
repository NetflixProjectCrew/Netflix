import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../../context/AuthContext";
import { useSubscription } from "../../../context/SubscriptionContext";
import { useState } from "react";

export default function Header() {
  const { user, isAuth, logout } = useAuth();
  const { active } = useSubscription();
  const [open, setOpen] = useState(false);
  const nav = useNavigate();
  const loc = useLocation();

  const onLogout = async () => {
    await logout();
    nav("/welcome", { replace: true });
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-white/80 backdrop-blur border-b">
      <div className="mx-auto max-w-7xl px-4 py-3 flex items-center gap-3">
        <Link to={isAuth ? (active ? "/browse" : "/subscribe") : "/welcome"} className="font-bold text-lg">
          WANNA<span className="opacity-50"> watch?</span>
        </Link>

        <nav className="ml-auto flex items-center gap-2">
          {/* Баннер «Оформить подписку», если залогинен, но без активной подписки */}
          {isAuth && !active && loc.pathname !== "/subscribe" && (
            <Link
              to="/subscribe"
              className="hidden sm:inline-flex items-center px-3 py-2 rounded-xl bg-black text-white"
            >
              Оформить подписку
            </Link>
          )}

          {!isAuth ? (
            <Link to="/auth" className="px-3 py-2 rounded-xl border hover:bg-gray-50">
              Войти
            </Link>
          ) : (
            <div className="relative">
              <button
                onClick={() => setOpen((v) => !v)}
                className="flex items-center gap-2 rounded-full border px-2 py-1"
                title={user?.username || user?.email}
              >
                <img
                  src={user?.avatar || "https://api.dicebear.com/9.x/identicon/svg?seed=user"}
                  alt="avatar"
                  className="h-8 w-8 rounded-full object-cover"
                />
                <span className="hidden sm:inline text-sm">{user?.username || user?.email}</span>
                <svg width="16" height="16" viewBox="0 0 20 20" className="opacity-60">
                  <path d="M5 7l5 6 5-6H5z" fill="currentColor" />
                </svg>
              </button>

              {open && (
                <div
                  onMouseLeave={() => setOpen(false)}
                  className="absolute right-0 mt-2 w-56 rounded-2xl border bg-white shadow-lg overflow-hidden"
                >
                  <MenuItem to="/browse" onClick={() => setOpen(false)}>Главная</MenuItem>
                  <MenuItem to="/subscribe" onClick={() => setOpen(false)}>
                    {active ? "Управление подпиской" : "Оформить подписку"}
                  </MenuItem>
                  <div className="border-t" />
                  <button
                    onClick={onLogout}
                    className="w-full text-left px-4 py-2.5 hover:bg-gray-50 text-red-600"
                  >
                    Выйти
                  </button>
                </div>
              )}
            </div>
          )}
        </nav>
      </div>

      {/* Узкий баннер сверху страницы, если нет подписки */}
      {isAuth && !active && (
        <div className="bg-amber-50 border-t border-b">
          <div className="max-w-7xl mx-auto px-4 py-2 text-sm flex items-center justify-between">
            <span>У вас нет активной подписки. Доступ к просмотру будет открыт после оплаты.</span>
            <Link to="/subscribe" className="underline underline-offset-4">Оформить</Link>
          </div>
        </div>
      )}
    </header>
  );
}

function MenuItem({ to, children, onClick }) {
  return (
    <Link
      to={to}
      onClick={onClick}
      className="block px-4 py-2.5 hover:bg-gray-50"
    >
      {children}
    </Link>
  );
}
