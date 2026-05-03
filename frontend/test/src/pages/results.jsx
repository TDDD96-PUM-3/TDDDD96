import { useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";
import "./results.css";
import LinearWithValueLabel from "../components/PercentageBar.jsx";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function getCounterfeitScore(value) {
  if (typeof value === "number") {
    return value > 1 ? value / 100 : value;
  }

  if (!value || value === "OK") {
    return 0;
  }

  return 1;
}

function getCounterfeitLabel(value) {
  if (!value || value === "OK") {
    return "No infringement found";
  }

  return String(value).replaceAll("_", " ");
}

function normalizeUrl(url) {
  const trimmedUrl = url.trim();

  if (!trimmedUrl || /^https?:\/\//i.test(trimmedUrl)) {
    return trimmedUrl;
  }

  return `https://${trimmedUrl}`;
}

export default function Results() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const query = normalizeUrl(params.get("query") || "");

  const [sortType, setSortType] = useState("risk-high");
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function scrapeUrl() {
      if (!query) {
        setProducts([]);
        setError("");
        return;
      }

      setIsLoading(true);
      setError("");

      try {
        const response = await fetch(
          `${API_BASE_URL}/scrape_url?url=${encodeURIComponent(query)}`,
          { signal: controller.signal }
        );
        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Could not scrape the URL.");
        }

        setProducts([
          {
            id: query,
            name: data.name || query,
            link: data.link || query,
            picture: data.picture,
            counterfeit: data.counterfeit,
          },
        ]);
      } catch (err) {
        if (err.name !== "AbortError") {
          setProducts([]);
          setError(err.message || "Could not scrape the URL.");
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    }

    scrapeUrl();

    return () => controller.abort();
  }, [query]);

  const sortedProducts = useMemo(() => {
    return [...products].sort((a, b) => {
      const aScore = getCounterfeitScore(a.counterfeit);
      const bScore = getCounterfeitScore(b.counterfeit);

      switch (sortType) {
        case "risk-high":
          return bScore - aScore;
        case "risk-low":
          return aScore - bScore;
        case "name-az":
          return a.name.localeCompare(b.name);
        case "name-za":
          return b.name.localeCompare(a.name);
        default:
          return 0;
      }
    });
  }, [products, sortType]);

  return (
    <div className="results-container">
      <h1 className="results-title">Results</h1>
      <div className="results-header">
        <h6>Based on search: {query || "nothing"}</h6>
        <div className="sort-controls">
          <label htmlFor="sort">Sort by: </label>
          <select
            id="sort"
            value={sortType}
            onChange={(e) => setSortType(e.target.value)}
          >
            <option value="risk-high">Counterfeit risk: High to low </option>
            <option value="risk-low">Counterfeit risk: Low to high</option>
            <option value="name-az">Name: A to Z</option>
            <option value="name-za">Name: Z to A</option>
          </select>
        </div>
      </div>

      {isLoading && <p className="results-status">Scraping URL...</p>}
      {error && <p className="results-status results-error">{error}</p>}
      {!isLoading && !error && query && sortedProducts.length === 0 && (
        <p className="results-status">No results found.</p>
      )}

      <div className="products">
        {sortedProducts.map((product) => {
          const score = getCounterfeitScore(product.counterfeit);

          return (
            <a
              className="product-container"
              key={product.id}
              href={product.link}
              target="_blank"
              rel="noopener noreferrer"
            >
              {product.picture ? (
                <img src={product.picture} alt={product.name} />
              ) : (
                <div className="product-image-placeholder">No image</div>
              )}
              <div className="bar-and-name">
                <div className="name">
                  <h5 className="product-link">{product.name}</h5>
                </div>
                <div className="bar-text">
                  <p>{getCounterfeitLabel(product.counterfeit)}</p>
                </div>
                <div className="bar">
                  <LinearWithValueLabel percentage={score * 100} />
                </div>
              </div>
            </a>
          );
        })}
      </div>
    </div>
  );
}
