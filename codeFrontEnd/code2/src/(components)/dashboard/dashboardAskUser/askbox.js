import { useEffect, useRef } from "react";
import "./askbox.css";





function setdimentions(askboxRef, width_percent, height_percent)
{
    askboxRef.current.style.width = width_percent+"px";
    askboxRef.current.style.height = height_percent+"px";
}
function adjustWindow(tempmaskRef, askboxContentRef)
{
    setTimeout(()=>{
        tempmaskRef.current.style.display = "none";
        askboxContentRef.current.style.display = "flex";
    }, 700)
}
function closeAskbox(setAddSession)
{
    setAddSession(false);
}

export default function Askbox({children, width=200, height=400, setAddSession, InjectableForLoggin})
{
    let askboxRef = useRef(null);
    let tempmaskRef = useRef(null);
    let askboxContentRef = useRef(null);
    useEffect(()=>{
        setdimentions(askboxRef, width, height);
        adjustWindow(tempmaskRef, askboxContentRef);
    }, [])


    return (
        <div className="askbox" ref={askboxRef}>
            <div className="tempmask" ref={tempmaskRef}></div>
            <div className="askbox_content" ref={askboxContentRef}>
                <div className="close_window" onClick={()=>{closeAskbox(setAddSession)}}></div>
                {children}
            </div>
        </div>
    )
}