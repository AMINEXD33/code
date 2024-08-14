import { useRef } from "react";
import { CodeEditor } from "../codeEditor/codeEditor";
import "./stpicker.css";





export default function Stpicker()
{
    let editor_live = useRef(true);


    return (
        <>
            {editor_live.current === true && <CodeEditor/>}
            {editor_live.current === false &&
                <div className="session_picker">

                </div>
            }
        </>
    )
}