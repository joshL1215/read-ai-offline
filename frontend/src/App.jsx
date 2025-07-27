import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { CssBaseline } from '@mui/material';

import MenuScene from './scenes/MenuScene.jsx';
import ReadingScene from './scenes/ReadingScene.jsx';
import JournalScene from './scenes/JournalScene.jsx';


function App() {

    return (
        <>
            <CssBaseline />
            <Routes>
                <Route path="/" element={<MenuScene />} />
                <Route path="/reading" element={<ReadingScene />} />
                <Route path="/journal" element={<JournalScene />} />
            </Routes>

        </>


    )

}

export default App;
