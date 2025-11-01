import { Link } from "react-router-dom";

export default function WelcomePage() {
    return (
        <main className="min-h-[70vh] grid place-items-center px-6">
        <div className="max-w-xl text-center space-y-6">
            <h1 className="text-3xl md:text-5xl font-bold">Добро пожаловать!</h1>
            <p className="text-lg opacity-80">
            Смотри фильмы и сериалы без рекламы. Создай аккаунт или войди — и начнём.
            </p>
            <div className="flex items-center justify-center gap-3">
            <Link to="/auth" className="px-5 py-3 rounded-xl bg-black text-white hover:opacity-90">
                Войти / Зарегистрироваться
            </Link>
            </div>
        </div>
        </main>
    );
}