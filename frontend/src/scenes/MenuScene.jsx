import { useState, useRef } from 'react'
import NavBar from '../components/NavBar';
import { Box, Container } from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';
import Typography from '@mui/material/Typography';



function SettingsIconComponent() {
    return (

        <SettingsIcon sx={{
            fontSize: '450px',
            color: 'rgba(255, 255, 255, 1)',
            animation: 'spin 20s linear infinite',
            '@keyframes spin': {
                '0%': { transform: 'rotate(0deg)' },
                '100%': { transform: 'rotate(360deg)' },
            }
        }
        } />


    );
}

function MenuScene() {

    return (
        <Box sx={{
            display: 'flex',
            flexDirection: 'row',
            justifyContent: 'center',
            alignItems: 'center',
            width: '100vw',
            height: '100vh',
            overflow: 'hidden',
            backgroundColor: 'white',
            backgroundImage: 'linear-gradient(135deg,rgba(192, 192, 192, 0.05) 10%,rgba(229, 229, 229, 0.95) 90%)',
        }}
        >
            <Box sx={{
                display: 'flex',
                flexDirection: ' row',
                width: '80vw',

            }}
            >
                <Container
                    sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'center',
                        width: '50vw',
                        gap: 1, // adds spacing between lines
                    }}
                >
                    <Typography variant="h5" sx={{ fontSize: '40px' }}>
                        Welcome to...
                    </Typography>
                    <Typography variant="h1" sx={{
                        fontSize: '90px',
                        fontWeight: 'bold',
                        background: 'linear-gradient(45deg, #2a28a7ff, #31051eff)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent'
                    }}>

                        GemmaRead

                    </Typography>
                    <Typography variant="h6" sx={{ fontSize: '30px' }}>
                        An AI Literacy Coach
                    </Typography>
                    <Typography variant="body2" sx={{ fontSize: '20px', color: 'text.secondary' }}>
                        Powered by Gemma 3n directly on your machine
                    </Typography>
                </Container>


                <Container sx={{ display: 'flex', justifyContent: 'center', width: '40vh' }}>
                    <NavBar />
                </Container>

            </Box>

        </Box>

    );
}

export default MenuScene;
