"use client";
import { useEffect, useRef, useState } from "react"
import "./btnload.css";


export default function BtnLoad({
    content,// the content of the btn
    height,
    width,
    radius,
    callBack,// this is the function passed to handle what ever
    args,//the args that will be passed to the callBack
    handleResponse// this function is handling the response if the callBack is a fetch
})
{
    let loading_dots = useRef(null);
    let text_ = useRef(null);
    let buttun = useRef(null);
    let lock = useRef(false);

    // is butten clicked
    let [btn_state, set_btn_state] = useState(false);
    async function executer ()
    {
        // for the first run , lock the executer untile the first run is resolved
        if (lock.current === true){return;}
        // lock if it's the first run
        lock.current = true;
        // set the button as inactive  while the execution of the 
        // callBack isn't done, when done reset the state of the button
        set_btn_state(true);
        let ss = await callBack(...args)
        .then()
        .catch(error=>{console.log(error)})
        .finally(()=>{
            set_btn_state(false)
            lock.current = false;
        })
        // release lock
    }
    useEffect(()=>{
        if (btn_state === true && loading_dots.current && text_.current && buttun.current)
        {
            // if we're loading set the text's display tp none and display the loading dots
            text_.current.style.display = "none";
            loading_dots.current.style.display = "flex";
            buttun.current.classList.add("dull")
        }
        else if (btn_state === false && loading_dots.current && text_.current && buttun.current)
            {
            // we're done loading we can reset the button
                loading_dots.current.style.display = "none";
                text_.current.style.display = "flex";
                buttun.current.classList.remove("dull")
            }

    }, [btn_state])
    return (
        <>
            <div onClick={()=>{executer()}} ref={buttun} className="btnLoad" style={
                {
                    "height":height+"px",
                    'width':width+"px",
                    'borderRadius':radius+"px"
                }}>
                <div className="loading_" ref={loading_dots}>
                    <div className="dot">.</div>
                    <div className="dot">.</div>
                    <div className="dot">.</div>
                </div>
                <div className="text_" ref={text_}>
                    {content}
                </div>
            </div>
        </>
    )
}
