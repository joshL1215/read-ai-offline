import JournalBook from "../components/JournalBook";
import { Box, Container } from '@mui/material';

export default function JournalScene() {

    return (
        <JournalBook pages={[
            <div>Hello!</div>,
            <p>Hello!</p>,
            <p>Hello!</p>,
            <p>test</p>,
            <p>test</p>,
            <p>test</p>,

        ]
        } />
    )
}