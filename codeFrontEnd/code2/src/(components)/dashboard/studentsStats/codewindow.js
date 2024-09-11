import { Window_ } from "./window_"
import { CodeEditor } from "../../codeEditor/codeEditor"
import { Editor } from "@monaco-editor/react"
import { useState } from "react"

export function Codewindow({ setShowcode }) {
    let [language, setLanguage] = useState("javascript");
    let [fontSize, setFontSize] = useState("12");
    let [code, setCode] = useState(``);
    return (
        <Window_ setShowcode={setShowcode}>
            <div className="codewindow">
                <Editor
                    height="100vh"
                    className="editor2"
                    language={language}
                    theme="vs-dark"
                    value={code}
                    onChange={(value) => { handlesaving(value, metrics) }}
                    options={{
                        readOnly: true,
                        inlineSuggest: true,
                        fontSize: fontSize,
                        formatOnType: true,
                        autoClosingBrackets: true,
                        minimap: { scale: 4 },
                    }}
                />
            </div>
        </Window_>
    )
}