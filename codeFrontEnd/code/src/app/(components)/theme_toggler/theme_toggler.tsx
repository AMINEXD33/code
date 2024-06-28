"use client";
import { stat } from 'fs';
import dynamic from 'next/dynamic';
import { useState, useEffect } from 'react';
import React from 'react';
import Image from 'next/image';
import sun from "../../../../public/sun.svg";
import moon from "../../../../public/moon.svg";
import "./theme_toggler.css";
interface propFromChild{
    theme: string|null,
    themeSetter : React.Dispatch<React.SetStateAction<string>>;
}
const Toggler: React.FC<propFromChild> = ({theme, themeSetter})=> {
    
    const [toggler_src, setToggler_src] = useState(moon);
    function switch_to_dark_mode(){
        localStorage.setItem("theme", "dark");
    }
    function switch_to_ligh_mode(){
        localStorage.setItem("theme", "light");
    }
    function trigger_change()
    {
        if (theme === "dark"){
            switch_to_ligh_mode();
            themeSetter("light")
        }
        else if (theme === "light"){
            switch_to_dark_mode()
            themeSetter("dark")
        }
    }
    useEffect(()=>{
        // checking  for stored themes in local storage
        let stored_theme = localStorage.getItem("theme");
        if (stored_theme && stored_theme === "dark"){switch_to_dark_mode();}
        else if (stored_theme && stored_theme === "light"){switch_to_ligh_mode();}
        
        if (theme === "light"){
                setToggler_src(sun);
        }
        else if (theme === "dark"){
                setToggler_src(moon);
        }
    }, [theme]);

    return (
        <>
            <div className='toggler' onClick={trigger_change}>
                <Image
                    src={toggler_src}
                    alt='toggler icon'
                    width={30}
                    height={30}
                    className='togicon'
                />
            </div>
        </>
    )
}
export default Toggler;