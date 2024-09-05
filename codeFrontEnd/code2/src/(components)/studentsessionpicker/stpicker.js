import { useRef } from "react";
import { CodeEditor } from "../codeEditor/codeEditor";
import { SessionSliderStudents } from "../session_slider/sessionSliderStudents";
import "./stpicker.css";





export default function Stpicker({
    token,
    setSelectedSessionId,
    InjectableForLoggin,
    selectedSessionId,
    sessionsTasks,
    sockConnReff,
    metrics,
}) {

    let editor_live = useRef(true);
    let dataLoadedFlag = useRef(true);
    return (
        <>
            <div className="sessionstats">
                <div className="division0">
                    <SessionSliderStudents
                        dataLoadedFlag={dataLoadedFlag}
                        token={token}
                        InjectableForLoggin={InjectableForLoggin}
                        selectedSessionId={selectedSessionId}
                        setSelectedSessionId={setSelectedSessionId}
                        sessionsTasks={sessionsTasks}
                    />
                </div>
                {editor_live.current === true &&
                    <CodeEditor
                        token={token}
                        selectedSessionId={selectedSessionId}
                        sessionsTasks={sessionsTasks}
                        sockConnReff={sockConnReff}
                        metrics={metrics}
                    />}
                {editor_live.current === false &&
                    <div className="session_picker">

                    </div>
                }
            </div>
        </>
    )
}