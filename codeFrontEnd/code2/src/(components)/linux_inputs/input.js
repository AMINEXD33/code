
"use client";
import { useEffect, useRef, useState } from "react";
import "./input.css";






export default function Input({
    name,
    type,
    placeholder,
    id = "",
    onChange
}) {
    let inpt = useRef(null);
    let inpt2 = useRef(null);
    let inpt3 = useRef(null);
    const [isFoc, setIsFoc] = useState(false);
    function focusit() {
        setIsFoc(true);
    }
    function unfocus() {
        setIsFoc(false);
    }
    useEffect(() => {
        if (isFoc && inpt.current && inpt3.current) {
            inpt.current.classList.remove("unfocus_input");
            inpt.current.classList.add("focused_input");
        }
        else if (!isFoc && inpt.current && inpt3.current) {
            inpt.current.classList.remove("focused_input");
            inpt.current.classList.add("unfocus_input");
        }
        document.addEventListener("click", (e) => {
            if (e.target !== inpt2.current) {
                unfocus();
            }
        })

    }, [isFoc])

    return (
        <>
            <div className="linux_input" id={id} ref={inpt}>

                <input
                    type={type}
                    placeholder={placeholder}
                    onFocus={focusit}
                    ref={inpt2}
                    onChange={(e) => { onChange(e.target.value) }}
                />
            </div>
        </>
    )
}