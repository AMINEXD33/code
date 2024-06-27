"use client";
import "./navbar.css";
import { useEffect, useRef, useState } from "react";
import moon from "../../../public/dark_mode_moon.svg";
import sun from "../../../public/light_mode_sun.svg"
import dynamic from 'next/dynamic';
/**
 * 
 * @param {*} activeLink : the current page you're on
 * 
 * 1: home
 * 2: login
 * 3: signin
 * @returns 
 */
function Navbar({activeLink}){
    const [active1, setActive1] = useState("");
    const [active2, setActive2] = useState("");
    const [active3, setActive3] = useState("");
    const [menue_state, setMenueState] = useState(false)
    const [theme, setTheme] = useState("light");
    const [themeicon, setThemeIcon] = useState(sun);
    useEffect(()=>{
        if (activeLink == 1){setActive1("active");}
        else if (activeLink == 2){setActive2("active");}
        else if (activeLink == 3){setActive3("active");}
    }, [])
    // theme controller
    function toggle_theme(){
        if(theme==="light"){setTheme("dark")}
        else{setTheme("light")}
    }
    useEffect(()=>{
        let body = document.getElementById('bod');
        if(theme === "light"){
            body.classList.remove("darkmode");
            setThemeIcon(sun);
        }
        else{
            body.classList.add("darkmode")
            setThemeIcon(moon);
        }
    }, [theme])

    // menue controller
    function trigger_menue()
    {
        setMenueState(!menue_state);
    }
    useEffect(()=>{
        let elem = document.getElementById("menue_target");
        if (menue_state===true)
        {
            elem.classList.replace("retract", "expand");
        }
        else{
            elem.classList.replace("expand", "retract");
        }
    }, [menue_state])

    // dynamically importing some components
    const  Link  = dynamic(()=>import("next/link"), {suspense:true})
    const  Image = dynamic(()=>import("next/image"), {suspense:true})
    return (
        <>
            <div className="navbar">
                <div className="logo"></div>
                <div className="link_list retract" id="menue_target">
                    <ul>
                        <li>
                            <Link href="/login" prefetch={false} className={active1}>home</Link>
                        </li>
                        <li>
                            <Link  href="/" prefetch={false}  className={active2}>login</Link>
                        </li>
                        <li>
                            <Link  href="/" prefetch={false}  className={active3} content="signin" >signin</Link>
                        </li>

                    </ul>
                </div>
                <div className="toggler">
                    <Image
                        src={themeicon}
                        alt="things"
                        width={30}
                        height={30}
                        priority
                        onClick={toggle_theme}
                    />
                </div>
                <div className="menue" onClick={trigger_menue}>
                </div>
            </div>

            
        </>
    )
}
export default Navbar;