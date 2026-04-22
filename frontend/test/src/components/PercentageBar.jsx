import * as React from "react";
import PropTypes from "prop-types";
import LinearProgress from "@mui/material/LinearProgress";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";

function LinearProgressWithLabel(props) {
  return (
    <Box sx={{ display: "flex", alignItems: "center" }}>
      <Box sx={{ width: "100%", mr: 1 }}>
        <LinearProgress
          variant="determinate"
          aria-label="Upload photos"
          {...props}
          sx={{
            height: 10,
            borderRadius: 5,
            backgroundColor: "#ced7da",
            "& .MuiLinearProgress-bar": {
              backgroundColor: "#067a3c", // 👈 your color here
            },
          }}
        />
      </Box>
      <Box sx={{ minWidth: 35 }}>
        <Typography variant="body2" sx={{ color: "text.secondary" }}>
          {`${Math.round(props.value)}%`}
        </Typography>
      </Box>
    </Box>
  );
}

LinearProgressWithLabel.propTypes = {
  /**
   * The value of the progress indicator for the determinate and buffer variants.
   * Value between 0 and 100.
   */
  value: PropTypes.number.isRequired,
};

export default function LinearWithValueLabel({ percentage }) {
  return (
    <Box sx={{ width: "100%" }}>
      <LinearProgressWithLabel value={percentage} />
    </Box>
  );
}
