import React, { useEffect, useState } from "react";
import MicIcon from '@mui/icons-material/Mic';
import { Avatar, Box, Typography } from "@mui/material";

function MicVisualizer() {
    const [voiceDetected, setVoiceDetected] = useState(false);
    const [transcript, setTranscript] = useState("");
    const TIME_BETWEEN = 2000;

    useEffect(() => {
        let animationId;
        let chunks = [];
        let interval;
        let stream;
        let mediaRecorder;

        const startRecording = async () => {
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            const audioContext = new AudioContext();
            const source = audioContext.createMediaStreamSource(stream);
            const analyser = audioContext.createAnalyser();
            analyser.fftSize = 256;
            const dataArray = new Uint8Array(analyser.frequencyBinCount);
            source.connect(analyser);

            function getVolume() {
                analyser.getByteFrequencyData(dataArray);
                const avg = dataArray.reduce((acc, val) => acc + val, 0) / dataArray.length;
                setVoiceDetected(avg > 20);
                animationId = requestAnimationFrame(getVolume);
            }

            getVolume();

            const recordChunk = () => {
                chunks = [];
                mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

                mediaRecorder.ondataavailable = async (e) => {
                    if (e.data.size > 0) {
                        const formData = new FormData();
                        formData.append("file", e.data, "audio.webm");

                        try {
                            const response = await fetch("http://localhost:8000/transcribe", {
                                method: "POST",
                                body: formData,
                            });

                            if (response.ok) {
                                const data = await response.json();
                                setTranscript(prev => prev + " " + data.transcription);
                            } else {
                                console.error("Transcription failed", await response.text());
                            }
                        } catch (err) {
                            console.error("Error sending audio", err);
                        }
                    }
                };

                mediaRecorder.onstop = () => {
                    // Start the next chunk after current finishes
                    setTimeout(recordChunk, 0);
                };

                mediaRecorder.start();

                // Stop after 5 seconds
                setTimeout(() => {
                    if (mediaRecorder.state === "recording") {
                        mediaRecorder.stop();
                    }
                }, TIME_BETWEEN);
            };

            recordChunk();
        };

        startRecording();

        return () => {
            cancelAnimationFrame(animationId);
            if (interval) clearInterval(interval);
            if (mediaRecorder && mediaRecorder.state === "recording") {
                mediaRecorder.stop();
            }
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
