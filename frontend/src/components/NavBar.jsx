import React, { useEffect, useState } from "react";
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import { justifyContent, shadows } from '@mui/system';
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

function NavBar() {
    return (
        <Stack
            direction="column"
            spacing={15}

        >
            <Button LinkComponent={RouteLink} to="/reading" sx={buttonStyles}>Read</Button>
            <Button LinkComponent={RouteLink} to="/journal" sx={buttonStyles}>Journal</Button>

        </Stack>

    )
}

export default NavBar;