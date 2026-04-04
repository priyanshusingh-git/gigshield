import { useMemo, useRef, useState } from "react";
import { Link, Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import "./App.css";

const OTP_CODE = "121212";

const rider = {
  name: "Arjun Sharma",
  zone: "Andheri East",
  city: "Mumbai",
  platform: "Swiggy",
  tier: "Rakshak",
  premium: 63,
  payout: 510,
  status: "Protected",
  language: "Hindi + English",
  hours: "9 hrs/day",
  upi: "arjun@upi",
};

const riderTimeline = [
  { title: "Weekly cover active", detail: "Rakshak cover is active for this week." },
  { title: "Rainfall trigger matched", detail: "Heavy rainfall detected inside the active delivery zone." },
  { title: "Claim auto-created", detail: "No manual claim filing required from the rider." },
  { title: "Payout credited", detail: "₹510 credited to the registered UPI account." },
];

const riderMetrics = [
  { label: "Weekly premium", value: `₹${rider.premium}` },
  { label: "Potential payout", value: `₹${rider.payout}` },
  { label: "Active tier", value: rider.tier },
];

const adminMetrics = [
  { label: "Tracked riders", value: "18,420" },
  { label: "Active covers", value: "12,184" },
  { label: "Claims initiated", value: "1,248" },
  { label: "Payouts credited", value: "1,103" },
];

const adminClaims = [
  { rider: "Arjun Sharma", zone: "Andheri East", trigger: "Heavy rainfall", payout: "₹510", status: "Credited" },
  { rider: "Rahul Shaikh", zone: "Bandra West", trigger: "AQI spike", payout: "₹380", status: "Credited" },
  { rider: "Imran Khan", zone: "Kurla", trigger: "Flood alert", payout: "₹640", status: "Reviewing" },
];

function App() {
  const [authenticated, setAuthenticated] = useState(false);

  return (
    <Routes>
      <Route path="/" element={<LoginPage authenticated={authenticated} onVerify={() => setAuthenticated(true)} />} />
      <Route path="/rider" element={authenticated ? <RiderDashboard /> : <Navigate to="/" replace />} />
      <Route path="/.admin" element={<AdminDashboard />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function LoginPage({ authenticated, onVerify }) {
  const navigate = useNavigate();
  const [mobile, setMobile] = useState("9876543210");
  const [otp, setOtp] = useState(Array(6).fill(""));
  const [otpSent, setOtpSent] = useState(false);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const otpRefs = useRef([]);

  const otpValue = useMemo(() => otp.join(""), [otp]);
  const phoneReady = /^\d{10}$/.test(mobile);

  function updateOtp(index, rawValue) {
    const digit = rawValue.replace(/\D/g, "").slice(-1);
    setOtp((current) => {
      const next = [...current];
      next[index] = digit;
      return next;
    });

    if (digit && index < otpRefs.current.length - 1) {
      otpRefs.current[index + 1]?.focus();
    }
  }

  function handleOtpKeyDown(index, event) {
    if (event.key === "Backspace" && !otp[index] && index > 0) {
      otpRefs.current[index - 1]?.focus();
    }
    if (event.key === "ArrowLeft" && index > 0) {
      otpRefs.current[index - 1]?.focus();
    }
    if (event.key === "ArrowRight" && index < otpRefs.current.length - 1) {
      otpRefs.current[index + 1]?.focus();
    }
  }

  function handleOtpPaste(event) {
    const pasted = event.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    if (!pasted) {
      return;
    }

    event.preventDefault();
    const next = Array(6).fill("");
    pasted.split("").forEach((char, index) => {
      next[index] = char;
    });
    setOtp(next);
    otpRefs.current[Math.min(pasted.length, 6) - 1]?.focus();
  }

  function sendOtp() {
    if (!phoneReady) {
      setError("Enter a valid 10-digit mobile number.");
      return;
    }

    setBusy("send");
    setError("");

    setTimeout(() => {
      setOtpSent(true);
      setBusy("");
      otpRefs.current[0]?.focus();
    }, 700);
  }

  function verifyOtp(event) {
    event.preventDefault();

    if (!otpSent) {
      setError("Send the OTP first.");
      return;
    }

    if (otpValue.length !== 6) {
      setError("Enter the 6-digit OTP.");
      return;
    }

    setBusy("verify");
    setError("");

    setTimeout(() => {
      if (otpValue === OTP_CODE) {
        onVerify();
        navigate("/rider");
        return;
      }

      setBusy("");
      setError("Incorrect OTP. Please try again.");
    }, 850);
  }

  if (authenticated) {
    return <Navigate to="/rider" replace />;
  }

  return (
    <div className="app-shell">
      <div className="login-shell">
        <section className="login-card">
          <div className="brand-row">
            <span className="brand-mark">E</span>
            <h1>Earniq</h1>
          </div>

          <div className="login-copy">
            <h2>Sign in</h2>
            <p>Use your mobile number to receive a WhatsApp OTP.</p>
          </div>

          <form className="login-form" onSubmit={verifyOtp}>
            <label className="field">
              <span>Mobile number</span>
              <div className="phone-input">
                <span className="phone-prefix">+91</span>
                <input
                  type="tel"
                  inputMode="numeric"
                  placeholder="98765 43210"
                  value={mobile}
                  onChange={(event) => setMobile(event.target.value.replace(/\D/g, "").slice(0, 10))}
                />
              </div>
            </label>

            <button
              type="button"
              className="secondary-button"
              onClick={sendOtp}
              disabled={busy === "send"}
            >
              {busy === "send" ? "Sending OTP..." : "Send OTP on WhatsApp"}
            </button>

            <div className={`otp-status ${otpSent ? "is-active" : ""}`}>
              <span className="otp-status__dot" />
              <span>
                {otpSent
                  ? `OTP sent to WhatsApp ending in ${mobile.slice(-2).padStart(10, "•")}`
                  : "OTP will be delivered on WhatsApp"}
              </span>
            </div>

            <label className="field">
              <span>OTP</span>
              <div className="otp-grid" onPaste={handleOtpPaste}>
                {otp.map((digit, index) => (
                  <input
                    key={index}
                    ref={(node) => {
                      otpRefs.current[index] = node;
                    }}
                    type="text"
                    inputMode="numeric"
                    maxLength="1"
                    value={digit}
                    onChange={(event) => updateOtp(index, event.target.value)}
                    onKeyDown={(event) => handleOtpKeyDown(index, event)}
                  />
                ))}
              </div>
            </label>

            {error ? <div className="form-error">{error}</div> : null}

            <button type="submit" className="primary-button" disabled={busy === "verify"}>
              {busy === "verify" ? "Verifying..." : "Verify and continue"}
            </button>
          </form>
        </section>
      </div>
    </div>
  );
}

function RiderDashboard() {
  return (
    <div className="app-shell">
      <div className="dashboard-shell">
        <header className="dashboard-header">
          <div>
            <div className="brand-row">
              <span className="brand-mark">E</span>
              <h1>Earniq</h1>
            </div>
            <p className="dashboard-subtitle">Rider protection dashboard</p>
          </div>
          <div className="status-pill status-pill--good">{rider.status}</div>
        </header>

        <section className="hero-card">
          <div>
            <p className="section-label">Active worker</p>
            <h2>{rider.name}</h2>
            <p className="hero-copy">
              {rider.platform} partner in {rider.zone}, {rider.city} with {rider.tier} weekly
              protection and bilingual payout communication.
            </p>
          </div>
        </section>

        <section className="metrics-grid">
          {riderMetrics.map((metric) => (
            <article className="metric-card" key={metric.label}>
              <span>{metric.label}</span>
              <strong>{metric.value}</strong>
            </article>
          ))}
        </section>

        <section className="dashboard-grid">
          <article className="panel">
            <p className="section-label">Weekly protection</p>
            <div className="detail-list">
              <div className="detail-row">
                <span>Primary zone</span>
                <strong>{rider.zone}</strong>
              </div>
              <div className="detail-row">
                <span>Platform</span>
                <strong>{rider.platform}</strong>
              </div>
              <div className="detail-row">
                <span>Language</span>
                <strong>{rider.language}</strong>
              </div>
            </div>
          </article>

          <article className="panel">
            <p className="section-label">Claim flow</p>
            <div className="timeline-list">
              {riderTimeline.map((item) => (
                <div className="timeline-item" key={item.title}>
                  <span className="timeline-dot" />
                  <div>
                    <strong>{item.title}</strong>
                    <p>{item.detail}</p>
                  </div>
                </div>
              ))}
            </div>
          </article>
        </section>
      </div>
    </div>
  );
}

function AdminDashboard() {
  const location = useLocation();

  if (location.pathname !== "/.admin") {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="app-shell">
      <div className="dashboard-shell">
        <header className="dashboard-header">
          <div>
            <div className="brand-row">
              <span className="brand-mark">E</span>
              <h1>Earniq</h1>
            </div>
            <p className="dashboard-subtitle">Admin dashboard</p>
          </div>
          <Link className="text-link" to="/">
            Back to login
          </Link>
        </header>

        <section className="metrics-grid">
          {adminMetrics.map((metric) => (
            <article className="metric-card" key={metric.label}>
              <span>{metric.label}</span>
              <strong>{metric.value}</strong>
            </article>
          ))}
        </section>

        <section className="dashboard-grid">
          <section className="panel">
            <div className="section-heading">
              <div>
                <p className="section-label">Demo rider</p>
                <h3>{rider.name}</h3>
              </div>
              <span className="status-pill status-pill--good">{rider.status}</span>
            </div>
            <div className="detail-list">
              <div className="detail-row">
                <span>Platform</span>
                <strong>{rider.platform}</strong>
              </div>
              <div className="detail-row">
                <span>Zone</span>
                <strong>{rider.zone}, {rider.city}</strong>
              </div>
              <div className="detail-row">
                <span>Tier</span>
                <strong>{rider.tier}</strong>
              </div>
              <div className="detail-row">
                <span>Weekly premium</span>
                <strong>₹{rider.premium}</strong>
              </div>
              <div className="detail-row">
                <span>Latest payout</span>
                <strong>₹{rider.payout}</strong>
              </div>
              <div className="detail-row">
                <span>UPI</span>
                <strong>{rider.upi}</strong>
              </div>
              <div className="detail-row">
                <span>Shift pattern</span>
                <strong>{rider.hours}</strong>
              </div>
              <div className="detail-row">
                <span>Language</span>
                <strong>{rider.language}</strong>
              </div>
            </div>
          </section>

          <section className="panel">
            <div className="section-heading">
              <div>
                <p className="section-label">Recent claims</p>
                <h3>Live portfolio activity</h3>
              </div>
            </div>
            <div className="claims-list">
              {adminClaims.map((claim) => (
                <article className="claim-row" key={`${claim.rider}-${claim.trigger}`}>
                  <div>
                    <strong>{claim.rider}</strong>
                    <p>
                      {claim.zone} • {claim.trigger}
                    </p>
                  </div>
                  <div className="claim-values">
                    <strong>{claim.payout}</strong>
                    <span>{claim.status}</span>
                  </div>
                </article>
              ))}
            </div>
          </section>
        </section>
      </div>
    </div>
  );
}

export default App;
