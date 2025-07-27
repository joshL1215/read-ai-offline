import React, { useEffect, useState } from "react";
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import { Link as RouteLink } from 'react-router-dom';


const buttonStyles = {
    transition: 'transform 0.75s ease',
    fontSize: '30px',
    fontFamily: 'Arial',
    fontWeight: '300',
    color: 'black',
    textDecoration: 'none',
    textTransform: 'none',
    letterSpacing: '0.5px',
    willChange: 'transform',
    '&:hover': {
        backgroundColor: 'transparent',
        transform: 'scale(1.2)',
    },
};

function NavBar() {
    return (
        <Stack
            direction="row"
            spacing={25}
        >
            <RouteLink to="/reading">
                <Button sx={buttonStyles}>Read</Button>
            </RouteLink>

            <RouteLink to="/journal">
                <Button sx={buttonStyles}>Journal</Button>
            </RouteLink>

            <RouteLink to="/settings">
                <Button sx={buttonStyles}>Settings</Button>
            </RouteLink>
        </Stack>

    )
}

export default NavBar;