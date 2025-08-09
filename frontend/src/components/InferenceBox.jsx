import React, { useState, useEffect } from "react";
import { Box, Typography } from "@mui/material";

function InferenceBox({ title, inferenceID, style }) {
  const [text, setText] = useState("");

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/inf-stream/${inferenceID}`);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.inferenceID === inferenceID && data.text) {
          setText((prev) => prev + data.text);
        }
      } catch (e) {
        console.error("Failed to get WebSocket message:", e);
      }
    };
    ws.onerror = (e) => console.error("WebSocket error:", e);

    return () => ws.close();
  }, [inferenceID]);

  return (
    <Box sx={{ style }}>
      <Typography variant="h6">{title}</Typography>
      <Box mt={2} p={2} bgcolor="#d1d1d1ff" borderRadius={2} minHeight={500}>
        <Typography variant="body1" whiteSpace="pre-wrap">
          {text || "Your story..."}
        </Typography>
      </Box>
    </Box>
  );
}

export default InferenceBox;