import { useState } from 'react'
import NavBar from '../components/NavBar';
import { Box, Container } from '@mui/material';

function MenuScene() {

    return (
        <Box
            sx={{
                display: 'flex',
                flexDirection: 'column',
                width: '100vw',
                height: '100vh',
                backgroundColor: '',
            }}
        >
            <Container sx={{ display: 'flex', justifyContent: 'center', marginTop: '30px' }}>
                <NavBar />
            </Container>

            <Container sx={{ display: 'flex', justifyContent: 'center', marginTop: '30px', backgroundColor: 'black', height: "80vh" }}>
            </Container>
        </Box>

    );
}

export default MenuScene;
