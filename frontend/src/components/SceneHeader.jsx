import React, { useEffect, useState } from "react";
import Button from '@mui/material/Button';
import { Typography } from "@mui/material";
import { Box, justifyContent, shadows } from '@mui/system';
import { Link as RouteLink } from 'react-router-dom';


const buttonStyles = {
    justifyContent: 'center',
    transition: 'transform 0.75s ease, color 0.75s ease',
    fontSize: 50,
    fontFamily: 'Inter',
    color: '#000000ff',
    textTransform: 'none',
    letterSpacing: '0.1px',
    backgroundColor: 'transparent',
    willChange: 'transform',
    '&:hover': {
        color: '#321a79ff',
        transform: 'scale(1.2)',
    },
};

function SceneHeader({ scene }) {
    return (
        <Box>

            <Typography variant="h2" sx={{
                fontSize: '40px ',
                padding: '10px',
                fontWeight: 'bold',
                background: 'linear-gradient(45deg, #2a28a7ff, #31051eff)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
            }}>

                {scene}

            </Typography>
        </Box>

    )
}

export default SceneHeader;
