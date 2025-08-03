import React from 'react';
import MicVisualizer from '../components/MicVisualizer.jsx'
import { useEffect, useState } from "react";
import InferenceBox from '../components/InferenceBox.jsx';

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
            <MicVisualizer />
            <InferenceBox inferenceID="placeholder" title="Hello" style={{ maxWidth: 600, mx: "auto", mt: 4, p: 2, boxShadow: 3 }} />
        </div>

    );
}


export default ReadingScene;
