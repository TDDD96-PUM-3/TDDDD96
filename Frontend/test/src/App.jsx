import { Routes, Route, NavLink, useLocation } from "react-router-dom";
import Login from "./pages/login";
import Search from "./pages/search";
import Results from "./pages/results";
import Statistics from "./pages/statistics";
import "./App.css";

export default function App() {
  const location = useLocation();

  const isLoginPage = location.pathname === "/";

  return (
    <div className="app">
      {!isLoginPage && (
        <nav className="topbar">
          <h2 className="logo">Counterfeit Detector 3000</h2>

          <div className="topbar-links">
            <NavLink
              to="/search"
              className={({ isActive }) =>
                isActive ? "topbar-link active" : "topbar-link"
              }
            >
              Search
            </NavLink>
            <NavLink
              to="/results"
              className={({ isActive }) =>
                isActive ? "topbar-link active" : "topbar-link"
              }
            >
              Results
            </NavLink>
            <NavLink
              to="/statistics"
              className={({ isActive }) =>
                isActive ? "topbar-link active" : "topbar-link"
              }
            >
              Statistics
            </NavLink>
            <NavLink
              to="/"
              className={({ isActive }) =>
                isActive ? "topbar-link active logout-link" : "topbar-link logout-link"
              }
            >
              Logout
            </NavLink>
          </div>
        </nav>
      )}

      <main className="page-content">
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/search" element={<Search />} />
          <Route path="/results" element={<Results />} />
          <Route path="/statistics" element={<Statistics />} />
        </Routes>
      </main>
    </div>
  );
}