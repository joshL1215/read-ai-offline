import React, { useState } from 'react';
import MicVisualizer from '../components/MicVisualizer.jsx';
import { Box, Button, TextField } from '@mui/material';
import InferenceBox from '../components/InferenceBox.jsx';
import SceneHeader from '../components/SceneHeader.jsx';

function ReadingScene() {
    const [prompt, setPrompt] = useState('Tell me a story about a brave cat.');

    const startGeneration = async () => {
        try {
            const response = await fetch('http://localhost:8000/gen-story', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt,
                    inference_id: 'reading-prompt',
                }),
            });

            const data = await response.json();
            console.log('Generation started, full story:', data.story);
        } catch (err) {
            console.error('Error starting generation:', err);
        }
    };

    return (
        <Box
            sx={{
                position: 'relative',
                width: '100vw',
                height: '100vh',
                backgroundColor: '#fafafa',
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
            }}
        >
            <SceneHeader scene="Read" />

            <Box sx={{ padding: 2 }}>
                <TextField
                    fullWidth
                    label="Prompt"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                />
                <Button variant="contained" onClick={startGeneration} sx={{ mt: 2 }}>
                    Start Generation
                </Button>
            </Box>

            <Box
                sx={{
                    flex: 1,
                    width: '100%',
                    overflow: 'hidden',
                }}
            >
                <InferenceBox
                    inferenceID="reading-prompt"
                    title="Unmute and read!"
                    style={{ width: '100%', height: '100%' }}
                />
            </Box>

            <Box
                sx={{
                    height: 160,
                    width: '100%',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    paddingBottom: 5,
                }}
            >
                <MicVisualizer />
            </Box>
        </Box>
    );
}

export default ReadingScene;
