const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || window.location.origin;

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let detail = "Something went wrong";
    try {
      const payload = await response.json();
      detail = payload.detail || detail;
    } catch {
      // Keep default detail.
    }
    throw new Error(detail);
  }

  return response.json();
}

export const api = {
  sendOtp(phoneNumber) {
    return request("/auth/send-otp", {
      method: "POST",
      body: JSON.stringify({ phone_number: phoneNumber }),
    });
  },
  verifyOtp(workerId, otpCode) {
    return request("/auth/verify-otp", {
      method: "POST",
      body: JSON.stringify({ worker_id: workerId, otp_code: otpCode }),
    });
  },
  getWorker(workerId) {
    return request(`/worker/${workerId}`);
  },
  updateWorker(workerId, updates) {
    return request(`/worker/${workerId}`, {
      method: "PATCH",
      body: JSON.stringify(updates),
    });
  },
  buyPolicy(workerId, tier) {
    return request("/policy/buy", {
      method: "POST",
      body: JSON.stringify({ worker_id: workerId, tier }),
    });
  },
  simulateTrigger(workerId, triggerType) {
    return request("/trigger/simulate", {
      method: "POST",
      body: JSON.stringify({ worker_id: workerId, trigger_type: triggerType }),
    });
  },
  getClaim(workerId) {
    return request(`/claim/${workerId}`);
  },
  getNotification(claimId) {
    return request(`/notify/${claimId}`);
  },
  getAdminSummary() {
    return request("/admin/summary");
  },
  getAdminWorkers() {
    return request("/admin/workers");
  },
};
