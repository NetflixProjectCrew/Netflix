import { useEffect, useMemo, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { subApi } from "../../api/subApi"; // путь подправь под свой проект

export default function SubscribePage() {
  const navigate = useNavigate();
  const location = useLocation();

  const [plans, setPlans] = useState([]);
  const [loadingPlans, setLoadingPlans] = useState(true);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState(null); // простой тост

  const qs = useMemo(() => new URLSearchParams(location.search), [location.search]);
  const success = qs.get("success");
  const sessionId = qs.get("session_id");
  const canceled = qs.get("canceled");

  // 1) Обработка сценария возврата со Stripe
  useEffect(() => {
    (async () => {
      // Успешный платеж — подтвердить и очистить query
      if (success === "1" && sessionId) {
        try {
          setBusy(true);
          await subApi.confirmCheckout({ session_id: sessionId });
          setMessage("Підписку активовано ✅");
        } catch (e) {
          console.error(e);
          setMessage("Не вдалося підтвердити оплату");
        } finally {
          setBusy(false);
          // очищаем querystring, чтобы не триггерить повторно
          navigate("/subscribe", { replace: true });
        }
        return;
      }

      // Отмена — просто показать сообщение; ничего не создаём
      if (canceled === "1") {
        setMessage("Оплату скасовано");
        navigate("/subscribe", { replace: true });
        return;
      }

      // Обычный сценарий — подгружаем планы
      try {
        setLoadingPlans(true);
        const data = await subApi.getPlans();
        setPlans(Array.isArray(data) ? data : (data?.results ?? []));
      } catch (e) {
        console.error(e);
        setMessage("Не вдалося завантажити плани");
      } finally {
        setLoadingPlans(false);
      }
    })();
  }, [success, sessionId, canceled, navigate]);

  const startCheckout = async (planId) => {
    const planIdNum = Number(planId);
    if (!Number.isInteger(planIdNum)) {
      console.error("Invalid plan id", planId);
      setMessage("Помилка: некоректний ID плану");
      return;
    }

    try {
      setBusy(true);
      const success_url = `${window.location.origin}/subscribe?success=1&session_id={CHECKOUT_SESSION_ID}`;
      const cancel_url = `${window.location.origin}/subscribe?canceled=1`;

      const session = await subApi.createCheckoutSession({
        subscription_plan_id: planIdNum,   // <-- число
        success_url,
        cancel_url,
      });

      if (session?.checkout_url) window.location.assign(session.checkout_url);
      else if (session?.url) window.location.assign(session.url);
      else setMessage("Не отримав URL для оплати");
    } catch (e) {
      if (e?.response?.status === 409) {
          const { checkout_url } = e.response.data || {};
          setMessage("Є незавершений платіж. Завершіть або скасуйте його.");
          if (checkout_url) {
              window.location.assign(checkout_url);
          }
      } else if (e?.response?.status===400 && e?.response?.data) {
          await subApi.cancelPendingPayment();
      } 
      else {
        console.error(e);
        setMessage("Не вдалося створити сесію оплати");
      }
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <h1>Підписка</h1>

      {message && (
        <div style={{ margin: "12px 0", padding: 12, border: "1px solid #ccc" }}>
          {message}
        </div>
      )}

      {loadingPlans ? (
        <p>Завантаження планів…</p>
      ) : (
        <div style={{ display: "grid", gap: 16, gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))" }}>
            {plans.map((p) => (
            <div key={p.id} style={{ border: "1px solid #eee", borderRadius: 12, padding: 16 }}>
              <h3 style={{ marginTop: 0 }}>{p.name}</h3>
              <p style={{ opacity: 0.8 }}>
                {Number(p.price).toFixed(2)} / {p.duration_days} дн.
              </p>
              <button
                disabled={busy}
                onClick={() => startCheckout(p.id)}
                style={{ padding: "8px 12px", borderRadius: 8 }}
              >
                {busy ? "…" : "Оформити"}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
