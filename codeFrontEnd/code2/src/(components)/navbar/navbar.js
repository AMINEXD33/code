"use client";
import "./navbar.css";
import { memo, useEffect, useRef, useState } from "react";
import moon from "../../../public/dark_mode_moon.svg";
import sun from "../../../public/light_mode_sun.svg";
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
    const active1 = useRef("");
    const active2 = useRef("");
    const active3 = useRef("");
    const [menue_state, setMenueState] = useState(false)
    const [theme, setTheme] = useState(["light", sun]);


    
    // functions to controll if the navbar in view or not
    console.log("rendered");
    function set_nav_out(nvbar_address)
    {
        nvbar_address.classList.remove("down");
        nvbar_address.classList.add("up");
    }
    function set_nav_in(nvbar_address)
    {
        nvbar_address.classList.remove("up");
        nvbar_address.classList.add("down");
    }
    useEffect(()=>{
        if (activeLink == 1){active1.current = "active";}
        else if (activeLink == 2){active2.current = "active";}
        else if (activeLink == 3){active3.current = "active";}

        // set the listiner for scrolling up and down
        let nvbar = document.getElementById("nvbar");
        let last_top_scrool = 0;
        let handleScroll = document.addEventListener("scroll", ()=>{
            let this_scroll = document.documentElement.scrollTop;
            if (last_top_scrool > this_scroll){set_nav_out(nvbar);}
            else if (last_top_scrool < this_scroll){set_nav_in(nvbar);}   
            last_top_scrool = this_scroll;
        })

        return () => {
            document.removeEventListener("scroll", handleScroll);
        };
    }, [activeLink])
    // theme controller
    function toggle_theme(){
        if(theme[0]==="light"){setTheme(["dark", moon])}
        else{setTheme(["light", sun])}
    }
    useEffect(()=>{
        let body = document.getElementById('bod');
        if(theme[0] === "light"){
            body.classList.remove("darkmode");
            localStorage.setItem("theme", "light");
        }
        else{
            body.classList.add("darkmode")
            localStorage.setItem("theme", "dark");
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
    const  Link  = dynamic(()=>import("next/link"), {suspense:false})
    const  Image = dynamic(()=>import("next/image"), {suspense:false})
    const  Logo  = dynamic(()=>import("@/(components)/logo/logo", {suspense:false}))
    return (
        <>
            <div className="navbar" id="nvbar">
                <div className="logo">
                    <Logo glowing={false} id={"logo_"}/>
                </div>
                <div className="link_list retract" id="menue_target">
                    <ul>
                        <li>
                            <Link href="/login" prefetch={false} className={active1.current}>home</Link>
                        </li>
                        <li>
                            <Link  href="/" prefetch={false}  className={active2.current}>login</Link>
                        </li>
                        <li>
                            <Link  href="/" prefetch={false}  className={active3.current} content="signin" >signin</Link>
                        </li>

                    </ul>
                </div>
                <div className="toggler">
                    <Image
                        src={theme[1]}
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