import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { authApi } from "../api/authApi";

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export default function AuthProvider({ children }) {
    const [user, setUser] = useState(null);          
    const [access, setAccess] = useState(localStorage.getItem("access_token"));
    const [loading, setLoading] = useState(true);

    const bootstrap = useCallback(async () => {
        if (!access) { setLoading(false); return; }
        try {
        const profile = await authApi.getProfile();
        setUser(profile);
        } catch {
        // токен протух → подчистим
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        setAccess(null);
        setUser(null);
        } finally {
        setLoading(false);
        }
    }, [access]);

    useEffect(() => { bootstrap(); }, [bootstrap]);

    const login = (tokens, profile) => {
        localStorage.setItem("access_token", tokens.access);
        localStorage.setItem("refresh_token", tokens.refresh);
        setAccess(tokens.access);
        setUser(profile);
    };

    const logout = async () => {
        try {
        await authApi.logout(localStorage.getItem("refresh_token"));
        } catch {}
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        setAccess(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, isAuth: !!user, loading, login, logout }}>
        {children}
        </AuthContext.Provider>
    );
}
