import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useSubscription } from "../context/SubscriptionContext";

export function GuestOnlyRoute() {
    const { isAuth, loading } = useAuth();
    const { active, loading: subLoading } = useSubscription();
    if (loading || subLoading) return null;

    if (isAuth && active) return <Navigate to="/browse" replace />;
    if (isAuth && !active) return <Navigate to="/subscribe" replace />;
    return <Outlet />;
    }

export function RequireAuth() {
    const { isAuth, loading } = useAuth();
    const loc = useLocation();
    if (loading) return null;
    return isAuth ? <Outlet /> : <Navigate to="/auth" state={{ from: loc }} replace />;
    }

export function RequireSubscription() {
    const { isAuth, loading } = useAuth();
    const { active, loading: subLoading } = useSubscription();
    const loc = useLocation();

    if (loading || subLoading) return null;

    if (!isAuth) return <Navigate to="/auth" state={{ from: loc }} replace />;
    if (!active) return <Navigate to="/subscribe" replace />;
    return <Outlet />;
    }
