import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import LoginPage from './pages/login'; 
import Dashboard from './pages/dashboard';

// We create a wrapper component for the Login page so we can use the 'useNavigate' hook
function LoginWrapper() {
  const navigate = useNavigate();

  const handleLoginSubmit = async ({ email, password, remember }) => {
    try {
      const response = await fetch("http://localhost:8000/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, remember }),
      });

      const data = await response.json();

      if (response.ok) {
        // 1. Save the token to the browser's memory
        localStorage.setItem("token", data.token);
        
        // 2. Send the user to the dashboard
        navigate("/");
      } else {
        alert("Error: " + data.detail);
      }
    } catch (error) {
      console.error("Failed to connect to the backend", error);
    }
  };

  return <LoginPage onLogin={handleLoginSubmit} />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* The root path shows the Dashboard */}
        <Route path="/" element={<Dashboard />} />
        
        {/* The /login path shows the Login Page */}
        <Route path="/login" element={<LoginWrapper />} />
      </Routes>
    </BrowserRouter>
  );
}