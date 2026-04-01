import PieChart from "../components/PieChart";
import { desktopOS, test, test2 } from "../components/test_data";

export default function Statistics() {
  return (
    <div style={{ padding: 16 }}>
      <h1>Statistics</h1>
      <p>Show search results here.</p>
      <div  
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(2, 1fr)",
          gap: 50,
          justifyItems: "center",
        }}
      >
        <PieChart data={desktopOS} />
        <PieChart data={test} />
        <PieChart data={test2} />
        <PieChart data={test} />

      </div>
    </div>
  );
}