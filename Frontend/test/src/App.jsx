import { Routes, Route, Link } from "react-router-dom";
import Login from "./pages/login";
import Search from "./pages/search";
import Results from "./pages/results";
import Statistics from "./pages/statistics";

// function Home() {
//   return <h1>Home</h1>;
// }
// function Results() {
//   return <h1>Results page</h1>;
// }
// function Login() {
//   return <h1>Login page</h1>;
// }
// function Statistics() {
//   return <h1>Statistics page</h1>;
// }

export default function App() {
  return (
    <>
      <nav style={{ display: "flex", gap: 12, padding: 12 }}>
        <Link to="/">Login</Link>
        <Link to="/search">Search</Link>
        <Link to="/results">Results</Link>
        <Link to="/statistics">Statistics</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/search" element={<Search />} />
        <Route path="/results" element={<Results />} />
        <Route path="/statistics" element={<Statistics />} />
      </Routes>
    </>
  );
}
