import { useEffect, useRef, useState } from "react";
import "./sessionSlider.css";
import axios, { Axios } from "axios";
import { callGetActiveSessionsStudents } from "@/(components)/api_caller/api_caller";
import Logger from "../message_display/meassage_display_manager";
import { splite_date } from "../../app/login/api_funcs";
var loggerInjectable;
var logger;
// functions to handle the state of the shower
/**
 * this function animate the arrow icon
 * @param {*} element the reference of icon
 */
function animateArrow(element) {
    let flag1 = element.classList.contains("arrow_active");
    let flag2 = element.classList.contains("arrow_inactive");
    if (!flag1 && !flag2) {
        element.classList.add("arrow_active");
    }
    else if (flag1 && !flag2) {
        element.classList.remove("arrow_active");
        element.classList.add("arrow_inactive");
    }
    else if (!flag1 && flag2) {
        element.classList.remove("arrow_inactive");
        element.classList.add("arrow_active");
    }
}
/**
 * this function toggles and animate the table of sessions to make it visible
 * @param {*} element the reference of the table
 */
function sessionsShowerToggle(element) {
    let flag1 = element.classList.contains("active_session_shower");
    let flag2 = element.classList.contains("inactive_session_shower");
    console.log("sessions shower", flag1, flag2)
    if (!flag1 && !flag2) {
        element.classList.add("active_session_shower");
        element.style.display = "block";
    }
    else if (flag1 && !flag2) {
        element.classList.remove("active_session_shower");
        element.classList.add("inactive_session_shower");
        setTimeout(() => {
            element.style.display = "none";
        }, 1000)


    }
    else if (!flag1 && flag2) {
        element.classList.remove("inactive_session_shower");
        element.classList.add("active_session_shower");
        element.style.display = "block";
    }
}
/**
 * handles when user clicks sessionShower 
 * @param {*} sessionShowerElement reference of the sessionShower element
 * @param {*} iconElement reference of the icon used
 */
function sessionShowerRootine(sessionShowerElement, iconElement) {

    sessionsShowerToggle(sessionShowerElement.current);
    animateArrow(iconElement.current);
}


function makeAsessionCell(sessionTitle, sessionGroup, sessionStartDate, sessionEndDate) {
    let tr = document.createElement("tr");
    let content = `
    <tr>
        <td>${sessionTitle}</td>
        <td>${sessionGroup}</td>
        <td>${sessionStartDate}</td>
        <td>${sessionEndDate}</td>
    </tr>`;
    tr.innerHTML = content;
    return tr;
}
var SessionPickeventListiners = [];
// APIs
/**
 * this function loads the correct data into the table of sessions
 * @param {*} data data that will get loaded in the sessions table
 * @param {*} sessionSLider a reference to the sessionSlider
 * @param {*} sessionHolder a reffrence to the place holder for sessionSlider
 */
function loadData(data, sessionSlider, sessionHolder, token, setSelectedSessionId, tbodyRef, sessionsTasks) {

    if (token && token.current) {
        axios.post(callGetActiveSessionsStudents(), { "data": { "JWT": token.current } })
            .then(response => {
                try{
                    let data = response.data["data"];
                    let docFrag = document.createDocumentFragment();
                    const options = { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true };

                    for (let index = 0; index < data.length; index++) {
                        let sessioniD = data[index]["session_id"];
                        let title = data[index]["session_title"];
                        let group = data[index]["session_users_groupe_name"];
                        let startDate = new Date(splite_date(data[index]["session_start_time"])).toLocaleTimeString('en-US', options);
                        let endDate = new Date(splite_date(data[index]["session_end_time"])).toLocaleTimeString('en-US', options);
                        let cell = makeAsessionCell(title, group, startDate, endDate);
                        sessionsTasks.current[data[index]["session_id"]] = {
                            session_allowed_to_run_code:data[index]["session_allowed_to_run_code"],
                            session_task:data[index]["session_task"],
                            session_title:data[index]["session_title"],
                            session_topics:data[index]["session_topics"],
                            languages_name:data[index]["languages_name"].toLowerCase(),
                            session_start_time:data[index]["session_start_time"],
                            session_end_time:data[index]["session_end_time"]
                        }
                        console.log(cell);
                        let evListener = cell.addEventListener("click", () => {
                            setSelectedSessionId(sessioniD);
                            for (let x = 0; x < SessionPickeventListiners.length; x++) {
                                removeEventListener("click", SessionPickeventListiners[index]);
                            }
                        });
                        SessionPickeventListiners.push(evListener);
                        console.log(cell);
                        console.log("heeeeere", tbodyRef.current)
                        docFrag.appendChild(cell)
                    }
                    tbodyRef.current.appendChild(docFrag);
                }catch(error)
                {
                    logger.error(loggerInjectable, "error parsing the server response");
                }
            })
            .catch(error => {
                // log the error and that's it for now
                if (error.response) {
                    logger.error(loggerInjectable, error.response.data);
                }
                else{
                    logger.error(loggerInjectable, "error fetching sessions from the server");
                }
            })
            .finally(() => {
                sessionHolder.style.display = "none";
                sessionSlider.style.display = "flex";
            });
    }
    else {
        // if no token yet we will wait 1s and try again with a valid token
        setTimeout(() => {
            loadData(data, sessionSlider, sessionHolder, token, setSelectedSessionId, tbodyRef, sessionsTasks);
        }, 1000);
    }

}


export function SessionSliderStudents({ dataLoadedFlag, data, token, selectedSessionId, setSelectedSessionId, InjectableForLoggin, sessionsTasks}) {
    loggerInjectable = InjectableForLoggin;
    logger = new Logger();
    let selectedSession = useRef('None');
    let sessionsShower = useRef(null);
    let arrowIcon = useRef(null);
    let sessionSLider = useRef(null);
    let sessionHolder = useRef(null);
    let tbodyRef = useRef(null);

    useEffect(() => {

        if (dataLoadedFlag.current) {
            loadData(data, sessionSLider.current, sessionHolder.current, token, setSelectedSessionId, tbodyRef, sessionsTasks);
        }
        else{
            console.log("no loaded data")
        }
    }, [dataLoadedFlag])
    return (
        <>
            <h4>Selected session:{selectedSessionId}</h4>
            <div className="sessions_slider" ref={sessionSLider} onClick={() => { sessionShowerRootine(sessionsShower, arrowIcon) }}>
                active sessions
                <div className="arrow_down_icon" ref={arrowIcon}></div>
                <div className="sessions_shower" ref={sessionsShower}>
                    <table className="sessionsalivetable" >
                        <thead>
                            <tr>
                                <th>session title</th>
                                <th>specified group</th>
                                <th>creation date</th>
                                <th>ending date</th>
                            </tr>
                        </thead>
                        <tbody ref={tbodyRef}>
                            {/* <tr>
                                <td>Test 1</td>
                                <td>DEV102</td>
                                <td>2024/12/12</td>
                            </tr> */}

                        </tbody>
                    </table>
                </div>
            </div>
            <div className="sessions_slider_place_holder" ref={sessionHolder}></div>
        </>
    )
}