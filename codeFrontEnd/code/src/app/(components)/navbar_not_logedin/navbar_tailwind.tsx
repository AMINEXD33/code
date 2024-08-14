"use client";
import dynamic from 'next/dynamic';
import { useState, useEffect } from 'react';
import Toggler from '../theme_toggler/theme_toggler';
interface propFromChild{
    theme: string|null,
    themeSetter : React.Dispatch<React.SetStateAction<string>>;
}
const Navbar: React.FC<propFromChild> = ({theme, themeSetter})=> {
    return (
        <>
            <nav className={`bg-white shadow ${theme}:bg-gray-800`}>
                <div className={`container flex items-center justify-center p-6 mx-auto text-gray-600 capitalize ${theme}:text-gray-300`}>
                    <a href="#" className={`text-gray-800 transition-colors duration-300 transform ${theme}:text-gray-200 border-b-2 border-blue-500 mx-1.5 sm:mx-6`}>home</a>

                    <a href="#" className={`border-b-2 border-transparent hover:text-gray-800 transition-colors duration-300 transform ${theme}:hover:text-gray-200 hover:border-blue-500 mx-1.5 sm:mx-6`}>login</a>

                    <a href="#" className={`border-b-2 border-transparent hover:text-gray-800 transition-colors duration-300 transform ${theme}:hover:text-gray-200 hover:border-blue-500 mx-1.5 sm:mx-6`}>register</a>

                    <a href="#" className={`border-b-2 border-transparent hover:text-gray-800 transition-colors duration-300 transform ${theme}:hover:text-gray-200 hover:border-blue-500 mx-1.5 sm:mx-6`}>about</a>
                    <>
                        <Toggler theme={theme} themeSetter={themeSetter}/>
                    </>
                </div>
            </nav>
        </>
    )
}
export default Navbar;