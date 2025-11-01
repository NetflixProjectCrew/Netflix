import api from "./axios";

export const subApi = {
  async getPlans() {
    const { data } = await api.get("/api/v1/subscribe/plans/");
    return data;
  },

  
  async getMySubscriptionStatus() {
    const { data } = await api.get("/api/v1/subscribe/status/");
    return data; // ожидаем { is_active: bool, ... }
  },

 

  async createCheckoutSession(sessionData) {
    // «универсально» — шлем оба поля + абсолютные url
    const payload = {
      subscription_plan_id: sessionData.subscription_plan_id,
      success_url: sessionData.successUrl,
      cancel_url: sessionData.cancelUrl,
    };

    const { data } = await api.post("/api/v1/payment/create-checkout-session/", payload);
    return data; // { checkout_url, payment_id }
  },

    async getPaymentStatus(payment_id) {
        const { data } = await api.get(`/api/v1/payment/payments/${payment_id}/status/`);
        return data;
    },

    async getPaymentHistory() {
        const { data } = await api.get("/api/v1/payment/payments/history/");
        return data;
    },

    async cancelAtPeriodEnd() {
        const { data } = await api.post("/api/v1/subscribe/cancel/");
        return data;
    },

    cancelPendingPayment: () => 
      api.post('/api/v1/payment/cancel-pending/').then(r=>r.data),

    confirmCheckout: ({ session_id }) =>
      api.post("/api/v1/payment/confirm-checkout/", { session_id })
        .then(r => r.data),

    async getStreamLink(slug) {
        const { data } = await api.get(`/api/v1/subscribe/movies/${slug}/stream-link/`);
        return data;
    },

    async refreshStreamLink(slug) {
        const { data } = await api.post(`/api/v1/subscribe/movies/${slug}/refresh-stream-link/`);
        return data;
    },
};
