import { useEffect, useMemo, useRef, useState } from "react";
import "./codeEditor.css";
import { Editor } from "@monaco-editor/react";
import { dbManager } from "@/database_manager/dbmanager";
import Taskathand from "../dashboard/taskathand/taskathand";
import Counter from "../dashboard/counter/counter";

function setCostumSaveEventListeners(saveCallBack, db_instace, codeRef) {
    window.addEventListener("keydown", (e) => {
        if (e.ctrlKey && e.key == "s") {
            e.preventDefault();
            saveCallBack(db_instace, codeRef);
        }
    })
}

function handlesaving(value, metrics) {
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
    try {
        window.localStorage.setItem("code", value);
        // update the metrics
        metrics.current[0].code = value;
    } catch (error) {
        throw "can't store code in local storage\n" + error;
    }
}

function handlechangingLanguage(event, setLanguage) {
    window.localStorage.setItem("fontsize", event.target.value);
    setLanguage(event.target.value);
}

function handlechangingFontsize(event, setFontsize) {
    window.localStorage.setItem("language", event.target.value);
    setFontsize(event.target.value);
}

export function CodeEditor({
    token,
    selectedSessionId,
    sessionsTasks,
    sockConnReff,
    metrics
}) {
    let codeRef = useRef("");
    let onholdDiv = useRef(null);
    let [code, setCode] = useState("");
    let [fontSize, setFontsize] = useState("16px");
    let [language, setLanguage] = useState("not set");
    let number = useMemo(() => { return (selectedSessionId) });
    const sockRequest1 = {
        msgType: "request",
        msg: "hahaaaa",
        successCallback: (data) => { console.log(data) },
        failedCallback: (error) => { console.log(error) },
        expectedAfter: 2,
        permanent: false
    }
    const sockRequest2 = {
        msgType: "request",
        msg: "yaaaa layliiii",
        successCallback: (data) => { console.log(data) },
        failedCallback: (error) => { console.log(error) },
        expectedAfter: 4,
        permanent: true
    }

    useEffect(() => {
        let storedCode = window.localStorage.getItem("code");
        setCode(storedCode);
        onholdDiv.current.style.display = "none";
        let storedFontsize = window.localStorage.getItem("fontsize");
        if (storedFontsize) {
            setFontsize(storedFontsize);
        }
        if (selectedSessionId != null) {
            // change this to reflect the langu in the future
            try {
                setLanguage(sessionsTasks.current[selectedSessionId]["languages_name"]);
            } catch (error) {
                console.error("can't reload")
                console.log("selectedSessionId   ", selectedSessionId);
                console.log("sessionsTasks", sessionsTasks);
            }
        }

    }, [selectedSessionId])


    return (
        <div className="editormask" id="editmast1">
            <div className="editor_on_hold" ref={onholdDiv}>
                <div className="waitIcon"></div>
                <h2>please wait a second !</h2>
            </div>
            <Taskathand token={token} selectedSessionId={selectedSessionId} sessionsTasks={sessionsTasks} />
            <div className="editorsettings">
                <label htmlFor="fontsize">font size</label>
                <select id="fontsize" defaultValue={fontSize} onChange={(event) => { handlechangingFontsize(event, setFontsize) }}>
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
                <label htmlFor="language">language</label>
                <div id="language">{language}</div>
                {/*ONLY SHOW WHEN A SESSION IS SELECTED */}
                {selectedSessionId !== null &&
                    <Counter
                        token={token}
                        selectedSessionId={selectedSessionId}
                        sessionsTasks={sessionsTasks}
                    />}
            </div>
            <Editor
                height="100vh"
                className="editor"
                language={language}
                theme="vs-dark"
                value={code}
                onChange={(value) => { handlesaving(value, metrics) }}
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