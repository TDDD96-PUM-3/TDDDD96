import { Routes, Route, Link } from "react-router-dom";

function Home() {
  return <h1>Home</h1>;
}
function Results() {
  return <h1>Results page</h1>;
}
function Login() {
  return <h1>Login page</h1>;
}
function Statistics() {
  return <h1>Statistics page</h1>;
}

export default function App() {
  return (
    <>
      <nav style={{ display: "flex", gap: 12, padding: 12 }}>
        <Link to="/">Home</Link>
        <Link to="/Results">Results</Link>
        <Link to="/Login">Login</Link>
        <Link to="/Statistics">Statistics</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/Results" element={<Results />} />
        <Route path="/Login" element={<Login />} />
        <Route path="/Statistics" element={<Statistics />} />
      </Routes>
    </>
  );
}
