import React, { useState } from "react";
import { Container, Button, Box, Typography } from "@mui/material";
import ArrowBackIosNewIcon from '@mui/icons-material/ArrowBackIosNew';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';

const styles = {
    container: {
        width: '100%',
        maxWidth: '800px',
        margin: '2rem auto',
        border: '1px solid #ddd',
        borderRadius: '16px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
        overflow: 'hidden',
        background: 'white',
        display: 'flex',
        flexDirection: 'column',
    },
    wholeBook: {
        display: 'flex',
        flexDirection: 'row',
        flex: 1,
        minHeight: '500px',
    },
    page: {
        flex: 1,
        padding: '2rem',
        fontSize: '1rem',
        borderRight: '1px solid #eee',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
    },
    lastPage: {
        borderRight: 'none',
    },

    controls: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',

    },
};

function JournalBook({ pages }) {
    const [currentPageset, setCurrentPageset] = useState(0);

    const pageCount = pages.length;
    const totalPagesets = Math.ceil(pageCount / 2);

    const leftPage = pages[currentPageset * 2];
    const rightPage = pages[currentPageset * 2 + 1] || <div />; // blank if missing

    const nextPageset = () => {
        if (currentPageset < totalPagesets - 1) {
            setCurrentPageset(currentPageset + 1);
        }
    };

    const prevPageset = () => {
        if (currentPageset > 0) {
            setCurrentPageset(currentPageset - 1);
        }
    };

    return (
        <Container sx={styles.container}>
            <Box sx={styles.wholeBook}>
                <Box sx={styles.page}>
                    {leftPage}
                </Box>
                <Box sx={{ ...styles.page, ...styles.lastPage }}>
                    {rightPage}
                </Box>
            </Box>

            <Box sx={styles.controls}>
                <Button
                    variant="contained"
                    onClick={prevPageset}
                    disabled={currentPageset === 0}
                    sx={{
                        backgroundColor: "transparent",
                        color: "black",
                        '&:hover': {
                            color: currentPageset === 0 ? '#474747ff' : '#111',
                        },
                    }}
                >
                    <ArrowBackIosNewIcon />
                </Button>

                <Button
                    variant="contained"
                    onClick={nextPageset}
                    disabled={currentPageset === totalPagesets - 1}
                    sx={{
                        backgroundColor: "transparent",
                        color: "black",
                        '&:hover': {
                            color: currentPageset === totalPagesets - 1 ? '#ccc' : '#111',
                        },
                    }}
                >
                    <ArrowForwardIosIcon />
                </Button>
            </Box>
        </Container >
    );
}

export default JournalBook;
