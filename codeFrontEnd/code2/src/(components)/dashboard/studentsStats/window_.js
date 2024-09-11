import { useRef } from "react";
import "./window_.css";

function closeWidnow(mainWindow, setShowcode) {
    mainWindow.current.style.display = "none";
    setShowcode(false);
}
export function Window_({ children, setShowcode }) {
    let mainWindow = useRef(null);
    return (
        <div className="window_" ref={mainWindow}>
            <div className="window_container">
                <div className="close_widows" onClick={() => {
                    closeWidnow(mainWindow, setShowcode);
                }}></div>
                {children}
            </div>
        </div>
    )
}