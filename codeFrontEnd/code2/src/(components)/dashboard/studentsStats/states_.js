import { Window_ } from "./window_"
import { CodeEditor } from "../../codeEditor/codeEditor"
import { Editor } from "@monaco-editor/react"
import { useState } from "react"

export function StatsWindow({ setShowstats }) {
    return (
        <Window_ setShowcode={setShowstats}>
            <div className="statswindow">

            </div>
        </Window_>
    )
}