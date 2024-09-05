import { useRef } from "react"
import "./SessionSettings.css";
import axios from "axios";
import { renameSession } from "../../api_caller/api_caller";
import { deletesession } from "../../api_caller/api_caller";



function changeName(sesionid, name, InjectableForLoggin, logger, token) {
    let response = axios.post(renameSession(), { "JWT": token.current, "sessionid": sesionid, "name": name });
    response.then(resp => {
        logger.success(InjectableForLoggin, resp.data);
        setTimeout(() => {
            location.reload();
        }, 1500)
    })
    response.catch(err => {
        logger.error(InjectableForLoggin, err);
    })
}

function delete_session(sesionid, InjectableForLoggin, logger, token) {
    let response = axios.post(deletesession(), {"JWT":token.current, "sessionid":sesionid});
    response.then(resp => {
        logger.success(InjectableForLoggin, resp.data);
        setTimeout(() => {
            location.reload();
        }, 1500)
    })
    response.catch(err => {
        logger.error(InjectableForLoggin, err);
    })
}

export function SessionSettings({
    token,
    InjectableForLoggin,
    logger,
    selectedSessionId
}) {
    let inputs = useRef(
        {
            sessionName: "",
        }
    )
    return (
        <div className="division2">
            <div className="subdiv2_0">
                <div className="settigns_container">
                    <div className="setting">
                        <label htmlFor="sessionname">Session Name</label>
                        <input id="sessionname"
                            onChange={(event) => { inputs.current.sessionName = event.target.value; }}
                        ></input>
                        <div className="changename" onClick={() => {
                            changeName(
                                selectedSessionId,
                                inputs.current.sessionName,
                                InjectableForLoggin,
                                logger,
                                token
                            )
                        }}>
                            <div className="changenameinner">
                                <h4>change name</h4>
                            </div>
                        </div>
                    </div>
                    <div className="setting" onClick={() => {
                        delete_session(
                            selectedSessionId,
                            InjectableForLoggin,
                            logger,
                            token
                        )
                    }}>
                        <label htmlFor="sessionname">End session</label>
                        <div className="outercirc">
                            <div className="innercirc">
                                <h4>delete session</h4>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}