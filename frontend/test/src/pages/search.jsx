import { useState } from "react";
import { useNavigate } from "react-router-dom";
import SearchBar from "../components/SearchBar";
import { scrapeUrl } from "../api";
import "./search.css";

export default function Search() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (query) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await scrapeUrl(query);
      // Pass the scraped data to results page via state
      navigate("/results?query=" + encodeURIComponent(query), { state: { data: result } });
    } catch (err) {
      const errorMessage = err?.message || err?.toString?.() || "Failed to scrape URL. Please try again.";
      setError(errorMessage);
      console.error("Search error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="search-container">
      <h1>Search.</h1>
      {error && <div className="error-message">{error}</div>}
      <SearchBar onSearch={handleSearch} disabled={isLoading} />
      {isLoading && <div className="loading-message">Scraping URL...</div>}
    </div>
  );
}