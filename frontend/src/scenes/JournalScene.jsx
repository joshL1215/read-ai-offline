import JournalBook from "../components/JournalBook";
import { Box } from '@mui/material';
import SceneHeader from '../components/SceneHeader.jsx';

export default function JournalScene() {

    return (
        <Box
            sx={{
                width: '100vw',
                height: '100vh',
                backgroundColor: '#fafafa',
                display: 'flex',
                flexDirection: 'column',
            }}
        >
            <SceneHeader scene="Journal" />
            <JournalBook pages={[
                <div>Hello!</div>,
                <p>Hello!</p>,
                <p>Hello!</p>,
                <p>test</p>,
                <p>test</p>,
                <p>test</p>,
            ]
            } />
        </Box>


    )
}