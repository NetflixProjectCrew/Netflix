import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { authApi } from "../../api/authApi";
import { subApi } from "../../api/subApi";
import { useAuth } from "../../context/AuthContext";
import { toast, ToastContainer } from "react-toastify";

export default function AuthPage() {
  const [mode, setMode] = useState("login"); // 'login' | 'register'
  const [form, setForm] = useState({ email: "", username: "", password: "", password_сonfirm: "" });
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);

  const { login } = useAuth();
  const nav = useNavigate();
  const loc = useLocation();
  const from = useMemo(() => loc.state?.from?.pathname, [loc.state]);

  useEffect(() => { setErr(null); }, [mode]);

  const onChange = (e) => setForm((s) => ({ ...s, [e.target.name]: e.target.value }));

  const afterAuth = async (payload) => {
    const { user, access, refresh } = payload;
    login({ access, refresh }, user);
    try {
      const me = await subApi.getMySubscriptionStatus();
      if (me?.is_active) {
        nav(from || "/browse", { replace: true });
      } else {
        nav("/subscribe", { replace: true });
      }
    } catch {
      nav("/subscribe", { replace: true });
    }
  };

  const onSubmit = async (e) => {
      e.preventDefault();
      setLoading(true); setErr(null);
      try {
        if (mode === "login") {
          await authApi.login(form.email, form.password); // <— твоя сигнатура
      } else {
        const reg = await authApi.register({
            email: form.email,
            username: form.username,
            password: form.password,
            password_confirm: form.password_confirm, // если у тебя отдельное поле — подставь его
        });

        // Если регистрация не вернула токены — сразу логинимся
        const access = localStorage.getItem("access_token");
        if (!access) {
            await authApi.login(form.email, form.password);
        }
      }

      // 1) профиль
      const profile = await authApi.getProfile();
      // 2) токены из LS
      const access = localStorage.getItem("access_token");
      const refresh = localStorage.getItem("refresh_token");
      // 3) стейт авторизации
      login({ access, refresh }, profile);
      // 4) подписка → редирект
      const me = await subApi.getMySubscription();
      if (me?.is_active) nav(from || "/browse", { replace: true });
      else nav("/subscribe", { replace: true });

    } catch (e2) {
      setErr(e2?.response?.data?.detail || "Ошибка авторизации");
      toast(e2?.response?.data?.detail)
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-[70vh] grid place-items-center px-4">
      <ToastContainer></ToastContainer>
      <div className="w-full max-w-md rounded-2xl border p-6 space-y-6">
        <div className="flex justify-center gap-2">
          <button
            className={`px-4 py-2 rounded-xl ${mode==='login'?'bg-black text-white':'bg-gray-100'}`}
            onClick={() => setMode("login")}
          >
            Войти
          </button>
          <button
            className={`px-4 py-2 rounded-xl ${mode==='register'?'bg-black text-white':'bg-gray-100'}`}
            onClick={() => setMode("register")}
          >
            Регистрация
          </button>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <div className="space-y-2">
            <label className="block text-sm">Email</label>
            <input
              required
              type="email"
              name="email"
              value={form.email}
              onChange={onChange}
              className="w-full rounded-xl border px-3 py-2"
              placeholder="you@example.com"
            />
          </div>

          {mode === "register" && (
            <div className="space-y-2">
              <label className="block text-sm">Username</label>
              <input
                type="text"
                name="username"
                value={form.username}
                onChange={onChange}
                className="w-full rounded-xl border px-3 py-2"
                placeholder="your nickname"
              />
            </div>
          )}

          <div className="space-y-2">
            <label className="block text-sm">Пароль</label>
            <input
              required
              type="password"
              name="password"
              value={form.password}
              onChange={onChange}
              className="w-full rounded-xl border px-3 py-2"
              placeholder="••••••••"
            />
          </div>

          {mode === "register" && (
          <div className="space-y-2">
            <label className="block text-sm">Подтвердите пароль</label>
            <input
              required
              type="password"
              name="password_confirm"
              value={form.password_confirm}
              onChange={onChange}
              className="w-full rounded-xl border px-3 py-2"
              placeholder="••••••••"
            />
          </div>
        )}

          {err && <p className="text-red-600 text-sm">{err}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full px-4 py-3 rounded-xl bg-black text-white disabled:opacity-60"
          >
            {loading ? "Обработка..." : (mode === "login" ? "Войти" : "Создать аккаунт")}
          </button>
        </form>
      </div>
    </main>
  );
}
