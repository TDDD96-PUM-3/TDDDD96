import { PieChart as MuiPieChart } from "@mui/x-charts/PieChart";
import { valueFormatter } from "./test_data";

export default function PieChart({data}) {
  return (
    <MuiPieChart
      series={[
        {
          data,
          highlightScope: { fade: "global", highlight: "item" },
          faded: { innerRadius: 0, additionalRadius: -15, color: "gray" },
          valueFormatter,
        },
      ]}
      colors={["#025F3A", "#FF9F1C", "#FF9800", "#9C27B0", "#607D8B"]}
      width={300}
      height={300}
      slotProps={{
        legend: {
          direction: "row",      
          position: {
            vertical: "bottom",  
            horizontal: "middle"
          },
        },
      }}
    />
  );
}