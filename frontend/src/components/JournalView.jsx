import React from "react";
import JournalBook from "./JournalBook";


function GraphPage() {
    const paceUrl = `http://localhost:8000/pace-graph`;
    const silencesUrl = `http://localhost:8000/silences-graph`;

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <img src={paceUrl} alt="Pace Graph" style={{ maxWidth: '100%' }} />
            <img src={silencesUrl} alt="Silences Graph" style={{ maxWidth: '100%' }} />
        </div>
    );
}

const pages = [
    <GraphPage />,
    <div>Right Page Content</div>,
    <div>Another Left Page</div>,
    <div>Another Right Page</div>,
];

function JournalView() {
    return <JournalBook pages={pages} />;
}

export default JournalView;