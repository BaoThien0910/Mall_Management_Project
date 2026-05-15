import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import axios from 'axios';
import LoginPage from './pages/login'; 
import Dashboard from './pages/dashboard';
import TenantsPage from './pages/tenants';

// We create a wrapper component for the Login page so we can use the 'useNavigate' hook
function LoginWrapper() {
  const navigate = useNavigate();

  const handleLoginSubmit = async (values) => {
    try {
      // 1. Send the data (Axios automatically handles the JSON conversion)
      const response = await axios.post("http://localhost:8000/api/login", values);

      // 2. If the code reaches this line, it means Python sent a 200 OK success!
      localStorage.setItem("token", response.data.token);
      navigate("/");

    } catch (error) {
      // 3. If Python sends an error (like 401 Wrong Password), Axios instantly jumps here
      if (error.response) {
        // The server replied, but said the password was wrong
        alert("Error: " + error.response.data.detail);
      } else {
        // The server is completely turned off or unreachable
        console.error("Failed to connect to the backend", error);
        alert("Cannot connect to the server. Is Python running?");
      }
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

        {/* The /tenants path shows the Tenants Management Page */}
        <Route path="/tenants" element={<TenantsPage />} />
      </Routes>
    </BrowserRouter>
  );
}