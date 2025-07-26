import React, { useEffect, useState } from "react";
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import { Link as RouteLink } from 'react-router-dom';

function NavBar() {
    return (
        <Stack
            direction="row"
            spacing={3}
        >
            <RouteLink to="/reading">
                <Button>READ</Button>
            </RouteLink>

            <RouteLink to="/journal">
                <Button>JOURNAL</Button>
            </RouteLink>

            <Button>SETTINGS</Button>
        </Stack>

    )
}

export default NavBar;