import { useEffect, useRef, useState } from "react";
import "./codeEditor.css";
import { Editor } from "@monaco-editor/react";
import { dbManager } from "@/database_manager/dbmanager";

function setCostumSaveEventListeners(saveCallBack, db_instace, codeRef) {
    window.addEventListener("keydown", (e) => {
        if (e.ctrlKey && e.key == "s") {
            e.preventDefault();
            saveCallBack(db_instace, codeRef);
        }
    })
}
function handlesaving(value, codeRef)
{
    function show_message() {
        let editormask = document.getElementById("editmast1");
        let domftag = document.createDocumentFragment();
        let new_info = document.createElement("div");
        new_info.classList.add("savedcode");
        let h4 = document.createElement("h4");
        h4.innerText = "your code is saved !";
        new_info.append(h4);
        domftag.appendChild(new_info);
        editormask.appendChild(domftag);
    }
    try{
        window.localStorage.setItem("code", value);
        console.log("setting code");
    }catch(error){
        throw "can't store code in local storage\n"+error;
    }
}
function handlechangingLanguage(event , setLanguage)
{
    window.localStorage.setItem("fontsize", event.target.value);
    setLanguage(event.target.value);
}
function handlechangingFontsize(event, setFontsize)
{
    window.localStorage.setItem("language", event.target.value);
    setFontsize(event.target.value);
}
export function CodeEditor() {
    let allowedL = ["javascrypt", "typescript", "python", "c", "c++", "c#", "java"];
    let codeRef = useRef("");
    let onholdDiv = useRef(null);
    let [code, setCode] = useState("");
    let [fontSize, setFontsize] = useState("16px");
    let [language, setLanguage] = useState("javascript");
    useEffect(() => {
        let storedCode = window.localStorage.getItem("code");
        setCode(storedCode);
        onholdDiv.current.style.display = "none";
        return () => {
        }
    }, [])
    useEffect(()=>{
        let storedFontsize = window.localStorage.getItem("fontsize");
        let storedLanguage = window.localStorage.getItem("language");

        if (storedFontsize)
        {
            setFontsize(storedFontsize);
        }
        if (storedLanguage)
        {
            setLanguage(storedLanguage);
        }
    }, [])

    
    return (
        <div className="editormask" id="editmast1">
            <div className="editor_on_hold" ref={onholdDiv}>
                <div className="waitIcon"></div>
                <h2>did you know that python is a snake !</h2>
            </div>
            <div className="taskathand">
                <div className="title">
                    <h4>Codding a quick sort algorithm</h4>
                </div>
                <div className="topics">
                    <div className="topic">
                        algorithms
                    </div>
                    <div className="topic">
                        python
                    </div>
                    <div className="topic">
                        dynamic programming
                    </div>
                </div>
                <div className="task_definition">
                    
                    <p className="task_def_start">
                        {`this assignment is going to be about a sorting algorithm all of you
                        have learned about , so what we're going to do is code a sorting algorithm
                        that takes O(n log(n)) time to sort an array of n element`}
                    </p>
                    <p className="task_def_middle">
                        for exampla we have an array sv = [1, 5, 1, 5, 8, 3, 2]
                        it should be sorted as [1, 1, 2, 3, 5, 6, 8]
                    </p>
                    <p className="task_def_end">
                        best of luck.
                    </p>
                </div>


            </div>
            <div className="editorsettings">
                <label htmlFor="fontsize">font size</label>
                <select id="fontsize" defaultValue={fontSize}onChange={(event)=>{handlechangingFontsize(event, setFontsize)}}>
                    <option value={"10px"}>10px</option>
                    <option value={"12px"}>12px</option>
                    <option value={"14px"}>14px</option>
                    <option value={"16px"}>16px</option>
                    <option value={"18px"}>18px</option>
                    <option value={"20px"}>20px</option>
                    <option value={"22px"}>22px</option>
                    <option value={"24px"}>24px</option>
                    <option value={"26px"}>26px</option>
                    <option value={"28px"}>28px</option>
                    <option value={"30px"}>30px</option>
                </select>
                <label htmlFor="language">languages</label>
                <select id="language" defaultValue={language} onChange={(event)=>{handlechangingLanguage(event, setLanguage)}}>
                    <option value={"javascript"}>javascript</option>
                    <option value={"typescript"}>typescript</option>
                    <option value={"python"}>python</option>
                    <option value={"java"}>java</option>
                    <option value={"c"}>c</option>
                    <option value={"c++"}>c++</option>
                    <option value={"c#"}>c#</option>
                    <option value={"ruby"}>ruby</option>
                    <option value={"json"}>json</option>
                </select>
            </div>
            <Editor
                height="100vh"
                className="editor"
                language={language}
                theme="vs-dark"
                value={code}
                onChange={(value) => {handlesaving(value)}}
                options={{
                    inlineSuggest: true,
                    fontSize: fontSize,
                    formatOnType: true,
                    autoClosingBrackets: true,
                    minimap: { scale: 4 },
                }}
            />
        </div>
    );
}