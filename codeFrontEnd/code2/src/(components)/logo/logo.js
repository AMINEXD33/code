"use client";
import "./logo.css";
import { useEffect, useCallback, useState, useRef } from "react";




export default function Logo({glowing=false, id=""})
{
    let logo = useRef(null);
    useEffect(()=>{
        if (glowing && logo.current){
            logo.current.classList.add("glow");
        }
    },)
    return (
        <>
            <div className="logo" ref={logo} id={id}>
                <div className="letter">C</div>
                <div className="letter">O</div>
                <div className="letter">D</div>
                <div className="letter">E</div>
            </div>
        </>
    )
}