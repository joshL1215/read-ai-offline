import React from 'react';
import MicVisualizer from '../components/MicVisualizer.jsx'
import { useEffect, useState } from "react";

function ReadingScene() {

    const [message, setMessage] = useState("");

    useEffect(() => {
        fetch("http://localhost:8000/ping")
            .then(res => res.json())
            .then(data => setMessage(data.message))
            .catch(err => console.error("API Error:", err));
    }, []);

    return (
        <div style={{ padding: 20 }}>
            <p>Message from backend: <strong>{message}</strong></p>

            <MicVisualizer />
        </div>

    );
}


export default ReadingScene;
