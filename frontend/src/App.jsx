import Login from './pages/login'; // This imports your file

function App() {
  
  // This function receives the data from your LoginPage component
  const handleLoginSubmit = async ({ email, password, remember }) => {
    try {
      // 1. Send the data to Python
      const response = await fetch("http://localhost:8000/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password, remember }),
      });

      // 2. Read Python's response
      const data = await response.json();

      if (response.ok) {
        // Success! Python said the password was right.
        alert("Success! Your token is: " + data.token);
        // Next steps: Save token to localStorage and redirect to Dashboard
      } else {
        // Python sent an error (wrong password)
        alert("Error: " + data.detail);
      }
      
    } catch (error) {
      console.error("Failed to connect to the backend", error);
    }
  };

  return (
    <div>
      {/* Pass our function into your beautiful UI component */}
      <Login onLogin={handleLoginSubmit} />
    </div>
  );
}

export default App;