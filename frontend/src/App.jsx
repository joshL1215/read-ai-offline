import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import MenuScene from './scenes/MenuScene.jsx';
import ReadingScene from './scenes/ReadingScene.jsx';
import JournalScene from './scenes/JournalScene.jsx';
import '@fontsource/inter/300.css';

const theme = createTheme({
    typography: {
        fontFamily: 'Inter, Helvetica, sans-serif',
    },
});

function App() {
    return (
        <ThemeProvider theme={theme} >
            <CssBaseline />
            <Routes>
                <Route path="/" element={<MenuScene />} />
                <Route path="/reading" element={<ReadingScene />} />
                <Route path="/journal" element={<JournalScene />} />
            </Routes>
        </ThemeProvider>
    );
}

export default App;
