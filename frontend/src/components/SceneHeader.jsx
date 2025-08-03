import React from "react";
import { Link } from "react-router-dom";
import IconButton from '@mui/material/IconButton';
import HomeIcon from '@mui/icons-material/Home';
import { Typography, Box } from "@mui/material";

function SceneHeader({ scene }) {
    return (
        <Box
            sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '20px',
            }}
        >
            <Typography
                variant="h2"
                sx={{
                    fontSize: '40px',
                    fontWeight: 'bold',
                    background: 'linear-gradient(45deg, #2a28a7ff, #31051eff)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                }}
            >
                {scene}
            </Typography>

            <IconButton
                component={Link}
                to="/"
                sx={{
                    color: '#000000ff',
                    transition: 'color 0.3s ease, transform 0.3s ease',
                    '&:hover': {
                        color: '#321a79ff',
                        transform: 'scale(1.2)',
                    },
                }}
                aria-label="home"
            >
                <HomeIcon fontSize="large" />
            </IconButton>
        </Box>
    );
}

export default SceneHeader;
