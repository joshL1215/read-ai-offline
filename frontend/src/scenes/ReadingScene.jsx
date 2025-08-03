import React from 'react';
import MicVisualizer from '../components/MicVisualizer.jsx';
import { Box } from '@mui/material';
import InferenceBox from '../components/InferenceBox.jsx';
import SceneHeader from '../components/SceneHeader.jsx';

function ReadingScene() {
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
            <Box
                sx={{
                    flex: 1,
                    width: '100%',
                    overflow: 'hidden',
                }}
            >
                <InferenceBox inferenceID="full" title="Unmute and read!" style={{ width: '100%', height: '100%' }} />
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
