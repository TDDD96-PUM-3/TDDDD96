import { PieChart as MuiPieChart } from "@mui/x-charts/PieChart";


export default function PieChart({ data }) {
  return (
    <MuiPieChart
      series={[
        {
          data,
          highlightScope: { fade: "global", highlight: "item" },
          faded: { innerRadius: 0, additionalRadius: -15, color: "gray" },
        },
      ]}
      colors={["#025F3A", "#97FF6F","#FF9800", "#607D8B"]}
      width={300}
      height={300}
      slotProps={{
        legend: {
          direction: "row",
          position: {
            vertical: "top",
            horizontal: "middle",
          },
        },
      }}
    />
  );
}
