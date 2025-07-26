import React from 'react';
import { Routes, Route } from 'react-router-dom';
import MenuScene from './scenes/MenuScene.jsx';
import ReadingScene from './scenes/ReadingScene.jsx';
import JournalScene from './scenes/JournalScene.jsx';

function App() {

    return (
        <div>
            <Routes>
                <Route path="/" element={<MenuScene />} />
                <Route path="/reading" element={<ReadingScene />} />
                <Route path="/journal" element={<JournalScene />} />
            </Routes>
        </div>
    )

}

export default App;
