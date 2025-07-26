import React, { useEffect, useState } from "react";
import MicIcon from '@mui/icons-material/Mic';
import { Avatar, Box, Typography } from "@mui/material";


function MicVisualizer() {
    const [voiceDetected, setVoiceDetected] = useState(false);
    const [transcript, setTranscript] = useState("");

    useEffect(() => {

        // Microphone lights up when sound is picked up
        let animationId;

        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {

                const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

                const audioContext = new AudioContext();
                const source = audioContext.createMediaStreamSource(stream);

                const analyser = audioContext.createAnalyser();
                analyser.fftSize = 256;
                const dataArray = new Uint8Array(analyser.frequencyBinCount);
                source.connect(analyser);

                function getVolume() {

                    analyser.getByteFrequencyData(dataArray);
                    const sum = dataArray.reduce((acc, val) => acc + val, 0);
                    const average = sum / dataArray.length;


                    if (average > 30) {

                        setVoiceDetected(true)

                    };

                    animationId = requestAnimationFrame(getVolume);
                }

                getVolume();

            })

            .catch(err => {
                console.error("Mic not found", err);
            });

        return () => {
            cancelAnimationFrame(animationId);
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
                gap: 5,
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

            <Typography
                sx={{
                    fontSize: 20,
                }}
            >
                Live Transcription: {transcript}
            </Typography>
        </Box>
    );
}

export default MicVisualizer;
