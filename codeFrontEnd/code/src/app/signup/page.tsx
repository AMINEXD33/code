"use client";
import dynamic from 'next/dynamic'
// import "./login.css";
import Navbar from '../(components)/navbar_not_logedin/navbar_tailwind';
import Image from 'next/image';
import { useState } from 'react';
function Login() {
    const [theme, setTheme] = useState("light");


    return (
        <>
            <Navbar theme={theme} themeSetter={setTheme} />
        </>
    )

}
export default Login;