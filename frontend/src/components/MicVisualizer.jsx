import React, { useEffect, useRef, useState } from "react";
import MicIcon from '@mui/icons-material/Mic';
import { Avatar, Box } from "@mui/material";

function MicVisualizer() {
    const [voiceDetected, setVoiceDetected] = useState(false);
    const [recording, setRecording] = useState(false);

    const audioContextRef = useRef(null);
    const streamRef = useRef(null);
    const analyserRef = useRef(null);
    const animationIdRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    useEffect(() => {
        return () => {
            cancelAnimationFrame(animationIdRef.current);
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
        };
    }, []);

    const getVolume = () => {
        const analyser = analyserRef.current;
        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(dataArray);
        const avg = dataArray.reduce((acc, val) => acc + val, 0) / dataArray.length;
        setVoiceDetected(avg > 30);
        animationIdRef.current = requestAnimationFrame(getVolume);
    };

    const startRecording = async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        streamRef.current = stream;

        // Voice visualization
        audioContextRef.current = new AudioContext();
        const source = audioContextRef.current.createMediaStreamSource(stream);
        const analyser = audioContextRef.current.createAnalyser();
        analyser.fftSize = 256;
        source.connect(analyser);
        analyserRef.current = analyser;
        getVolume();

        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) {
                audioChunksRef.current.push(event.data);
            }
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
            const formData = new FormData();
            formData.append("file", audioBlob, "recording.webm");
            try {
                await fetch('http://localhost:8000/eval', {
                    method: 'POST',
                    body: formData
                });
            } catch (error) {
                console.error('Error sending audio:', error);
            }
        };

        mediaRecorder.start();
    };

    const stopRecording = () => {
        cancelAnimationFrame(animationIdRef.current);
        setVoiceDetected(false);

        if (mediaRecorderRef.current?.state === "recording") {
            mediaRecorderRef.current.stop();
        }

        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
        }

        if (audioContextRef.current) {
            audioContextRef.current.close();
        }
    };

    const handleMicClick = () => {
        if (!recording) {
            startRecording();
        } else {
            stopRecording();
        }
        setRecording(!recording);
    };

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
                onClick={handleMicClick}
                sx={{
                    bgcolor: voiceDetected ? "#79cda2d4" : "grey.500",
                    width: 80,
                    height: 80,
                    cursor: "pointer",
                    transition: "all 0.25s ease",
                }}
            >
                <MicIcon sx={{ fontSize: voiceDetected ? 45 : 40 }} />
            </Avatar>
        </Box>
    );
}

export default MicVisualizer;
