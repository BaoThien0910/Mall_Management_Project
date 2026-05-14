import { useState } from "react";

/* ─── Inline SVG icons ─────────────────────────────────────────── */
const IconDomain = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
  </svg>
);

const IconMail = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="4" width="20" height="16" rx="2"/>
    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
  </svg>
);

const IconLock = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="11" width="18" height="11" rx="2"/>
    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
  </svg>
);

const IconArrow = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M5 12h14M12 5l7 7-7 7"/>
  </svg>
);

const IconCheckCircle = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
  </svg>
);

/* ─── Styles ───────────────────────────────────────────────────── */
const s = {
  page: {
    display: "flex",
    minHeight: "100vh",
    width: "100%",
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    backgroundColor: "#f9f9f9",
    color: "#1a1c1c",
  },
  left: {
    width: "50%",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#ffffff",
    padding: "48px 32px",
    boxShadow: "2px 0 8px rgba(0,0,0,0.04)",
    zIndex: 1,
    position: "relative",
  },
  form: {
    width: "100%",
    maxWidth: "420px",
  },
  brand: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    color: "#000666",
    marginBottom: "28px",
  },
  brandName: {
    fontSize: "20px",
    fontWeight: 600,
    color: "#000666",
    letterSpacing: "-0.01em",
  },
  heading: {
    fontSize: "36px",
    fontWeight: 700,
    lineHeight: "44px",
    letterSpacing: "-0.02em",
    color: "#1a1c1c",
    margin: "0 0 8px",
  },
  subtitle: {
    fontSize: "16px",
    lineHeight: "24px",
    color: "#454652",
    margin: "0 0 32px",
  },
  fieldGroup: {
    marginBottom: "20px",
  },
  labelRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "6px",
  },
  label: {
    fontSize: "12px",
    fontWeight: 600,
    letterSpacing: "0.05em",
    color: "#1a1c1c",
    textTransform: "uppercase",
    display: "block",
    marginBottom: "6px",
  },
  forgotLink: {
    fontSize: "12px",
    fontWeight: 600,
    letterSpacing: "0.05em",
    color: "#000666",
    textDecoration: "none",
    cursor: "pointer",
  },
  inputWrap: {
    position: "relative",
  },
  inputIcon: {
    position: "absolute",
    left: "14px",
    top: "50%",
    transform: "translateY(-50%)",
    color: "#767683",
    pointerEvents: "none",
    display: "flex",
    alignItems: "center",
  },
  input: {
    width: "100%",
    boxSizing: "border-box",
    paddingLeft: "44px",
    paddingRight: "16px",
    paddingTop: "12px",
    paddingBottom: "12px",
    backgroundColor: "#ffffff",
    border: "1px solid #c6c5d4",
    borderRadius: "4px",
    fontSize: "14px",
    lineHeight: "20px",
    color: "#1a1c1c",
    outline: "none",
    transition: "border-color 0.2s, box-shadow 0.2s",
  },
  checkRow: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    marginBottom: "20px",
    marginTop: "8px",
  },
  checkbox: {
    width: "16px",
    height: "16px",
    borderRadius: "2px",
    border: "1px solid #c6c5d4",
    accentColor: "#000666",
    cursor: "pointer",
    flexShrink: 0,
  },
  checkLabel: {
    fontSize: "14px",
    color: "#454652",
    cursor: "pointer",
    userSelect: "none",
  },
  button: {
    width: "100%",
    padding: "14px 24px",
    backgroundColor: "#1a237e",
    color: "#ffffff",
    border: "none",
    borderRadius: "4px",
    fontSize: "12px",
    fontWeight: 600,
    letterSpacing: "0.05em",
    textTransform: "uppercase",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
    boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
    marginBottom: "32px",
    fontFamily: "inherit",
  },
  footer: {
    borderTop: "1px solid rgba(198,197,212,0.3)",
    paddingTop: "24px",
  },
  footerText: {
    fontSize: "14px",
    color: "#454652",
    margin: 0,
  },
  footerLink: {
    color: "#000666",
    textDecoration: "none",
    fontWeight: 600,
  },
  right: {
    width: "50%",
    position: "relative",
    backgroundColor: "#e2e2e2",
    overflow: "hidden",
  },
  mallImage: {
    position: "absolute",
    inset: 0,
    width: "100%",
    height: "100%",
    objectFit: "cover",
  },
  tintOverlay: {
    position: "absolute",
    inset: 0,
    backgroundColor: "rgba(26,35,126,0.05)",
    mixBlendMode: "multiply",
    pointerEvents: "none",
  },
  statusCard: {
    position: "absolute",
    bottom: "32px",
    right: "32px",
    backgroundColor: "rgba(255,255,255,0.92)",
    backdropFilter: "blur(12px)",
    WebkitBackdropFilter: "blur(12px)",
    padding: "16px",
    borderRadius: "8px",
    boxShadow: "0 8px 16px rgba(0,0,0,0.1)",
    border: "1px solid rgba(198,197,212,0.2)",
    maxWidth: "280px",
    pointerEvents: "none",
  },
  statusRow: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    marginBottom: "6px",
    color: "#000666",
  },
  statusTitle: {
    fontSize: "13px",
    fontWeight: 600,
    letterSpacing: "0.02em",
    color: "#1a1c1c",
  },
  statusDesc: {
    fontSize: "13px",
    color: "#454652",
    lineHeight: "18px",
    margin: 0,
  },
};

/* ─── Component ────────────────────────────────────────────────── */
export default function LoginPage({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const [emailFocus, setEmailFocus] = useState(false);
  const [passFocus, setPassFocus] = useState(false);
  const [hovering, setHovering] = useState(false);
  const [active, setActive] = useState(false);

  const inputStyle = (focused) => ({
    ...s.input,
    borderColor: focused ? "#000666" : "#c6c5d4",
    boxShadow: focused ? "0 0 0 3px rgba(0,6,102,0.08)" : "none",
  });

  const buttonStyle = {
    ...s.button,
    opacity: hovering ? 0.9 : 1,
    transform: active ? "scale(0.98)" : "scale(1)",
    transition: "opacity 0.2s, transform 0.1s",
  };

  const handleSubmit = () => {
    if (onLogin) onLogin({ email, password, remember });
  };

  return (
    <div style={s.page}>
      {/* ── Left: Form ── */}
      <div style={s.left}>
        <div style={s.form}>

          {/* Brand */}
          <div style={s.brand}>
            <IconDomain />
            <span style={s.brandName}>Mall Management</span>
          </div>

          {/* Heading */}
          <h1 style={s.heading}>Sign In</h1>
          <p style={s.subtitle}>
            Enter your credentials to access the management suite.
          </p>

          {/* Email */}
          <div style={s.fieldGroup}>
            <label style={s.label} htmlFor="email">
              Email Address
            </label>
            <div style={s.inputWrap}>
              <span style={s.inputIcon}><IconMail /></span>
              <input
                style={inputStyle(emailFocus)}
                id="email"
                type="email"
                name="email"
                placeholder="admin@mainplaza.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onFocus={() => setEmailFocus(true)}
                onBlur={() => setEmailFocus(false)}
                autoComplete="email"
              />
            </div>
          </div>

          {/* Password */}
          <div style={s.fieldGroup}>
            <div style={s.labelRow}>
              <label style={{ ...s.label, marginBottom: 0 }} htmlFor="password">
                Password
              </label>
              <a style={s.forgotLink} href="#">
                Forgot Password?
              </a>
            </div>
            <div style={{ ...s.inputWrap, marginTop: "6px" }}>
              <span style={s.inputIcon}><IconLock /></span>
              <input
                style={inputStyle(passFocus)}
                id="password"
                type="password"
                name="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onFocus={() => setPassFocus(true)}
                onBlur={() => setPassFocus(false)}
                autoComplete="current-password"
              />
            </div>
          </div>

          {/* Remember Me */}
          <div style={s.checkRow}>
            <input
              style={s.checkbox}
              id="remember"
              type="checkbox"
              checked={remember}
              onChange={(e) => setRemember(e.target.checked)}
            />
            <label style={s.checkLabel} htmlFor="remember">
              Remember Me
            </label>
          </div>

          {/* Submit */}
          <button
            style={buttonStyle}
            type="button"
            onClick={handleSubmit}
            onMouseEnter={() => setHovering(true)}
            onMouseLeave={() => { setHovering(false); setActive(false); }}
            onMouseDown={() => setActive(true)}
            onMouseUp={() => setActive(false)}
          >
            Sign In
            <IconArrow />
          </button>

        </div>
      </div>

      {/* ── Right: Image ── */}
      <div style={s.right}>
        <img
          style={s.mallImage}
          src="https://lh3.googleusercontent.com/aida-public/AB6AXuBFXXtOc-Jvdb939ybodSZ6rGU5bMjWbAwGOKuEx1k1SfZu9YwURnFL3IurzpQHNRganl9EHho2dcPu0YGADsB-iteYuZI5ZqEfStEuCSlII6powuMInlNCL5A7MgRJrtW6erWoW6sPUEKeSFI9NS9ixYTvuLcSZGAhq72Sa6Chwhq-u40ElED-u9hD1GY9r5XlNoMPtIkPKx2J7Ay3gwuBqfo03I_kQg55F-UTlRaNVBSak2jUeQfmOT6LRgnF6_7GJdEaVEbDl1Gj"
          alt="Modern mall interior with glass skylights"
        />
        <div style={s.tintOverlay} />
      </div>
    </div>
  );
}
