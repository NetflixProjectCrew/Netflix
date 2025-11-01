import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useAuth } from "./AuthContext";
import { subApi } from "../api/subApi";

const SubContext = createContext(null);
export const useSubscription = () => useContext(SubContext);

export default function SubscriptionProvider({ children }) {
    const { isAuth, loading: authLoading } = useAuth();
    const [status, setStatus] = useState({ active: false, plan: null, loading: true });

    useEffect(() => {
        const load = async () => {
        if (!isAuth) { setStatus({ active:false, plan:null, loading:false }); return; }
        try {
            const st = await subApi.getMySubscriptionStatus();
            setStatus({ active: st?.is_active, plan: st?.plan || null, loading:false });
        } catch {
            setStatus({ active:false, plan:null, loading:false });
        }
        };
        if (!authLoading) load();
    }, [isAuth, authLoading]);

    const markActive = useCallback(
                                 () => setStatus(s => ({ ...s, active: true })),
                                    []); // дернуть после успешной оплаты

    return (
        <SubContext.Provider value={{ ...status, markActive }}>
        {children}
        </SubContext.Provider>
    );
}
