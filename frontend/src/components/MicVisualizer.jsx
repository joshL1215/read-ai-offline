import React, { useEffect, useState } from "react";
import MicIcon from '@mui/icons-material/Mic';
import { Avatar, Box } from "@mui/material";

function MicVisualizer() {
    const [voiceDetected, setVoiceDetected] = useState(false);

    useEffect(() => {
        let animationId;
        let stream;

        const startMicVisualizer = async () => {
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            const audioContext = new AudioContext();
            const source = audioContext.createMediaStreamSource(stream);
            const analyser = audioContext.createAnalyser();
            analyser.fftSize = 256;
            const dataArray = new Uint8Array(analyser.frequencyBinCount);
            source.connect(analyser);

            const getVolume = () => {
                analyser.getByteFrequencyData(dataArray);
                const avg = dataArray.reduce((acc, val) => acc + val, 0) / dataArray.length;
                setVoiceDetected(avg > 30);
                animationId = requestAnimationFrame(getVolume);
            };

            getVolume();
        };

        startMicVisualizer();

        return () => {
            cancelAnimationFrame(animationId);
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
        };
    }, []);

    return (
        <Box
            sx={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                mt: 4,
            }}
        >
            <Avatar
                sx={{
                    bgcolor: voiceDetected ? "#79cda2d4" : "grey.500",
                    width: 80,
                    height: 80,
                    transition: "all 0.25s ease",
                }}
            >
                <MicIcon sx={{ fontSize: voiceDetected ? 45 : 40 }} />
            </Avatar>
        </Box>
    );
}

export default MicVisualizer;
