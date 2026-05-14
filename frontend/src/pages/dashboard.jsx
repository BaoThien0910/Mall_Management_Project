/**
 * Dashboard.jsx — MallAdmin Pro
 * Only dependency: React & react-router-dom.
 */

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

/* ─── Inline SVG icons ─────────────────────────────────────────── */
const IconDomain = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
  </svg>
);

const IconDashboard = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
    <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>
  </svg>
);

const IconLogout = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>
  </svg>
);

/* ─── Styles (Matching Login Palette) ──────────────────────────── */
const theme = {
  bg: "#f9f9f9",
  surface: "#ffffff",
  primary: "#000666",
  primaryDark: "#1a237e",
  textMain: "#1a1c1c",
  textMuted: "#454652",
  textLight: "#767683",
  border: "#c6c5d4",
  borderLight: "rgba(198,197,212,0.3)",
};

const s = {
  layout: {
    display: "flex",
    height: "100vh",
    width: "100%",
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    backgroundColor: theme.bg,
    color: theme.textMain,
    overflow: "hidden",
  },
  sidebar: {
    width: "260px",
    backgroundColor: theme.surface,
    borderRight: `1px solid ${theme.borderLight}`,
    display: "flex",
    flexDirection: "column",
    flexShrink: 0,
  },
  brand: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    padding: "24px",
    borderBottom: `1px solid ${theme.borderLight}`,
    color: theme.primary,
  },
  brandText: {
    display: "flex",
    flexDirection: "column",
  },
  brandTitle: {
    fontSize: "18px",
    fontWeight: 700,
    letterSpacing: "-0.01em",
    margin: 0,
  },
  brandSub: {
    fontSize: "11px",
    color: theme.textMuted,
    margin: 0,
  },
  nav: {
    padding: "16px",
    flex: 1,
  },
  navItemActive: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    padding: "12px 16px",
    backgroundColor: theme.primaryDark,
    color: theme.surface,
    borderRadius: "6px",
    textDecoration: "none",
    fontSize: "14px",
    fontWeight: 600,
    marginBottom: "8px",
  },
  navItem: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    padding: "12px 16px",
    color: theme.textMuted,
    borderRadius: "6px",
    textDecoration: "none",
    fontSize: "14px",
    fontWeight: 500,
    marginBottom: "8px",
    cursor: "pointer",
  },
  sidebarBottom: {
    padding: "16px",
    borderTop: `1px solid ${theme.borderLight}`,
  },
  logoutBtn: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    padding: "12px 16px",
    width: "100%",
    backgroundColor: "transparent",
    border: "none",
    color: theme.textMuted,
    fontSize: "14px",
    fontWeight: 500,
    cursor: "pointer",
    textAlign: "left",
    borderRadius: "6px",
  },
  main: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
  },
  header: {
    height: "72px",
    backgroundColor: theme.surface,
    borderBottom: `1px solid ${theme.borderLight}`,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "0 32px",
  },
  searchInput: {
    width: "300px",
    padding: "10px 16px",
    backgroundColor: theme.bg,
    border: `1px solid ${theme.borderLight}`,
    borderRadius: "20px",
    fontSize: "13px",
    outline: "none",
    color: theme.textMain,
  },
  content: {
    flex: 1,
    padding: "32px",
    overflowY: "auto",
  },
  pageTitle: {
    fontSize: "28px",
    fontWeight: 700,
    margin: "0 0 4px 0",
    color: theme.textMain,
  },
  pageSub: {
    fontSize: "14px",
    color: theme.textMuted,
    margin: "0 0 32px 0",
  },
  grid4: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: "24px",
    marginBottom: "24px",
  },
  card: {
    backgroundColor: theme.surface,
    padding: "20px",
    borderRadius: "8px",
    border: `1px solid ${theme.borderLight}`,
    boxShadow: "0 2px 4px rgba(0,0,0,0.02)",
  },
  cardTitle: {
    fontSize: "12px",
    fontWeight: 600,
    color: theme.textLight,
    textTransform: "uppercase",
    letterSpacing: "0.05em",
    marginBottom: "12px",
    display: "block",
  },
  cardValue: {
    fontSize: "24px",
    fontWeight: 700,
    color: theme.primary,
    margin: 0,
  },
};

/* ─── Component ────────────────────────────────────────────────── */
export default function Dashboard() {
  const navigate = useNavigate();
  const [hoverLogout, setHoverLogout] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div style={s.layout}>
      
      {/* ── Sidebar ── */}
      <div style={s.sidebar}>
        <div style={s.brand}>
          <IconDomain />
          <div style={s.brandText}>
            <h1 style={s.brandTitle}>Mall Management</h1>
            <p style={s.brandSub}>Management Suite</p>
          </div>
        </div>

        <div style={s.nav}>
          <div style={s.navItemActive}>
            <IconDashboard />
            Dashboard
          </div>
          <div style={s.navItem}>
            <span style={{width: 20, height: 20, backgroundColor: theme.borderLight, borderRadius: 4}}></span>
            Tenants
          </div>
          <div style={s.navItem}>
            <span style={{width: 20, height: 20, backgroundColor: theme.borderLight, borderRadius: 4}}></span>
            Leases
          </div>
        </div>

        <div style={s.sidebarBottom}>
          <button 
            onClick={handleLogout}
            onMouseEnter={() => setHoverLogout(true)}
            onMouseLeave={() => setHoverLogout(false)}
            style={{
              ...s.logoutBtn,
              backgroundColor: hoverLogout ? theme.bg : "transparent",
              color: hoverLogout ? theme.primary : theme.textMuted
            }}
          >
            <IconLogout />
            Logout
          </button>
        </div>
      </div>

      {/* ── Main Content ── */}
      <div style={s.main}>
        
        {/* Header */}
        <div style={s.header}>
          <input 
            type="text" 
            placeholder="Search tenants, leases, or tickets..." 
            style={s.searchInput}
          />
          <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
            <span style={{ color: theme.textMuted }}>🔔</span>
            <div style={{ width: 32, height: 32, borderRadius: "50%", backgroundColor: theme.primary, color: theme.surface, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: "bold" }}>
              A
            </div>
          </div>
        </div>

        {/* Scrollable Body */}
        <div style={s.content}>
          <h2 style={s.pageTitle}>Chào buổi sáng, Admin</h2>
          <p style={s.pageSub}>Here is what's happening at your property today.</p>

          {/* KPI Grid */}
          <div style={s.grid4}>
            <div style={s.card}>
              <span style={s.cardTitle}>Tổng Doanh Thu</span>
              <p style={s.cardValue}>đ 12.4B</p>
            </div>
            <div style={s.card}>
              <span style={s.cardTitle}>Tỷ Lệ Lấp Đầy</span>
              <p style={s.cardValue}>94%</p>
            </div>
            <div style={s.card}>
              <span style={s.cardTitle}>Lượt Khách</span>
              <p style={s.cardValue}>45,210</p>
            </div>
            <div style={s.card}>
              <span style={s.cardTitle}>Yêu Cầu Bảo Trì</span>
              <p style={{...s.cardValue, color: "#ba1a1a"}}>12</p>
            </div>
          </div>

          {/* Charts Placeholder Area */}
          <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "24px" }}>
            <div style={{...s.card, height: "300px", display: "flex", flexDirection: "column"}}>
               <span style={{...s.cardTitle, color: theme.textMain}}>Xu hướng doanh thu & Lượt khách</span>
               <div style={{ flex: 1, backgroundColor: theme.bg, borderRadius: 4, border: `1px dashed ${theme.border}` }}></div>
            </div>
            <div style={{...s.card, height: "300px", display: "flex", flexDirection: "column"}}>
               <span style={{...s.cardTitle, color: theme.textMain}}>Cơ cấu ngành hàng</span>
               <div style={{ flex: 1, backgroundColor: theme.bg, borderRadius: 4, border: `1px dashed ${theme.border}`, borderRadius: "50%", margin: "20px auto", width: "260px" }}></div>
            </div>
          </div>

        </div>
      </div>

    </div>
  );
}