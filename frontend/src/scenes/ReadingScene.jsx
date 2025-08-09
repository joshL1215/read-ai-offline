import React, { useState } from 'react';
import MicVisualizer from '../components/MicVisualizer.jsx';
import { Box, Button, TextField, Paper, Typography } from '@mui/material';
import InferenceBox from '../components/InferenceBox.jsx';
import SceneHeader from '../components/SceneHeader.jsx';

function ReadingScene() {
    const [prompt, setPrompt] = useState('Write about Google');
    const [showPrompt, setShowPrompt] = useState(true);

    const startGeneration = async () => {
        setShowPrompt(false);

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
                backgroundColor: '#f0f2f5',
                overflow: 'hidden',
            }}
        >
            <Box
                sx={{
                    filter: showPrompt ? 'blur(8px)' : 'none',
                    pointerEvents: showPrompt ? 'none' : 'auto',
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                }}
            >
                <SceneHeader scene="Read" />

                <Box
                    sx={{
                        flex: 1,
                        padding: 3,
                        paddingBottom: 2,
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

                    }}
                >
                    <MicVisualizer />
                    <InferenceBox
                        inferenceID="eval"
                        title="Eval"
                        style={{ width: '100%', height: '100%' }}
                    />

                </Box>
            </Box>

            {showPrompt && (
                <Box
                    sx={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        zIndex: 10,
                        backdropFilter: 'blur(4px)',
                        backgroundColor: 'rgba(255, 255, 255, 0.6)',
                    }}
                >
                    <Paper
                        elevation={4}
                        sx={{
                            width: '100%',
                            maxWidth: 500,
                            padding: 4,
                            display: 'flex',
                            flexDirection: 'column',
                            gap: 2,
                        }}
                    >
                        <Typography variant="h6">What would you like to read about?</Typography>
                        <TextField
                            fullWidth
                            label=""
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                        />
                        <Button variant="contained" onClick={startGeneration}>
                            Start Generation
                        </Button>
                    </Paper>
                </Box>
            )}
        </Box>
    );
}

export default ReadingScene;
