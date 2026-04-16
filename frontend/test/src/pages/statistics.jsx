import { useLocation } from "react-router-dom";
import PieChart from "../components/PieChart";
import { test, test1, test2, test3} from "../components/test_data";
import "./statistics.css"

export default function Statistics() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const query = params.get("query");


  return (
    <div className="statistics-container">
      <h1>Statistics</h1>
      <h6>Based on search: {query || "nothing"}</h6>
      <div  className="pie-charts"
        > 
         <div className="pie">
            <h2>Found counterfeits</h2>
            <PieChart data={test} /></div>

         <div className="pie">
            <h2>Result from YYYY-MM-DD</h2>
            <PieChart data={test1} /></div>

         <div className="pie">
            <h2>Previous results from webbsite</h2>
            <PieChart data={test2}/>
            <h6>Amount of searches compiled: XX</h6>
            </div>

         <div className="pie">
            <h2>Highest percentage of found counterfeits</h2>
            <PieChart data={test3} />
            <h6>https://www.exempel.se/bbygurl</h6>
            </div>

      </div>
    </div>
  );
}