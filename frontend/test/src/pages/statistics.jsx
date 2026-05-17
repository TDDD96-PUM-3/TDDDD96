import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import PieChart from "../components/PieChart";
import { getStats } from "../api";
import "./statistics.css";

function toNumber(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : 0;
}

function buildCounterfeitChart(flagged, total) {
  const flaggedCount = toNumber(flagged);
  const totalCount = toNumber(total);
  const cleanTotal = Math.max(totalCount, flaggedCount);

  return [
    {
      label: "Counterfeits",
      value: flaggedCount,
    },
    {
      label: "Non-counterfeits",
      value: Math.max(cleanTotal - flaggedCount, 0),
    },
  ];
}

export default function Statistics() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const query = params.get("query");
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let ignore = false;

    const loadStats = async () => {
      try {
        const data = await getStats();
        if (!ignore) {
          setStats(data);
        }
      } catch (err) {
        if (!ignore) {
          setError(err?.message || "Could not load statistics.");
        }
      } finally {
        if (!ignore) {
          setIsLoading(false);
        }
      }
    };

    loadStats();

    return () => {
      ignore = true;
    };
  }, []);

  const totalImageStats = stats?.found_counterfeits_tot_img || {};
  const websiteStats = stats?.found_counterfeits_per_web || {};
  const latestStats = stats?.result_from_prev_scrape || {};
  const highestStats = stats?.highest_flagged_count || {};

  const totalImageChart = buildCounterfeitChart(
    totalImageStats.flagged_img,
    totalImageStats.total_img,
  );
  const websiteChart = buildCounterfeitChart(
    websiteStats.flagged_web,
    websiteStats.total_web,
  );
  const latestChart = buildCounterfeitChart(
    latestStats.flagged_img,
    latestStats.total_img,
  );
  const highestChart = buildCounterfeitChart(
    highestStats.flagged_img,
    highestStats.total_img,
  );

  if (isLoading) {
    return (
      <div className="statistics-container">
        <h1>Statistics</h1>
        <p className="statistics-message">Loading statistics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="statistics-container">
        <h1>Statistics</h1>
        <p className="statistics-message error-message">{error}</p>
      </div>
    );
  }

  return (
    <div className="statistics-container">
      <h1>Statistics</h1>
      <h6>Based on search: {query || "nothing"}</h6>
      <div className="pie-charts">
        <div className="pie">
          <h2>Saved image results</h2>
          <PieChart data={totalImageChart} />
          <h6>{totalImageStats.flagged_img || 0} of {totalImageStats.total_img || 0} images flagged</h6>
        </div>

        <div className="pie">
          <h2>Latest scrape image results</h2>
          <PieChart data={latestChart} />
          <h6>{latestStats.webname || latestStats.web_url || "No scrape saved yet"}</h6>
        </div>

        <div className="pie">
          <h2>Websites with counterfeits</h2>
          <PieChart data={websiteChart} />
          <h6>Amount of searches compiled: {websiteStats.total_web || 0}</h6>
        </div>

        <div className="pie">
          <h2>Scrape with most flagged images</h2>
          <PieChart data={highestChart} />
          <h6>{highestStats.web_url || "No scrape saved yet"}</h6>
        </div>
      </div>
    </div>
  );
}
