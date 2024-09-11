import { useEffect, useRef, useState } from "react";
import "./studentsstats.css";
import { getSessionUsers } from "../../api_caller/api_caller";
import axios from "axios";
import Image from "next/image";
import { Codewindow } from "./codewindow";
import { StatsWindow } from "./states_";

async function getUsers(selectedSessionId, token, users, logger, InjectableForLoggin) {
    return axios.post(getSessionUsers(), { "JWT": token.current, "sessionid": selectedSessionId })
        .then(data => data.data)
        .catch(err => {
            logger.error(InjectableForLoggin, "can't get session users!");
            logger.error(InjectableForLoggin, err);
            return [];
        })
}

function searchForStudent(term) {
    let searchterm = term.trim();
    let rgx = RegExp(searchterm);
    let students = document.getElementsByClassName("student");
    if (searchterm !== "") {
        for (let indx = 0; indx < students.length; indx++) {
            if (!rgx.test(students[indx].id)) {
                students[indx].style.display = "none";
            }
            else {
                students[indx].style.display = "flex";
            }
        }
    }
    else {
        for (let indx = 0; indx < students.length; indx++) {
            students[indx].style.display = "flex";
        }
    }

}

export function StudentsStats({
    token,
    InjectableForLoggin,
    logger,
    selectedSessionId
}) {
    let users = useRef([]);
    let usersElements = null;
    let [rerender, setRerender] = useState(false);
    let [showcode, setShowcode] = useState(false);
    let [showstats, setShowstats] = useState(true);

    useEffect(() => {
        async function fetchusers() {
            const data = await getUsers(selectedSessionId, token, users, logger, InjectableForLoggin);
            users.current = data;
            setRerender(true);
            console.warn("req = ", users.current);
        }
        if (selectedSessionId) {
            fetchusers();
        }

        return () => {

        }
    }, [selectedSessionId])

    return (
        <>
            <div className="division2">
                <div className="subdiv2_0 this12">
                    {showcode &&
                        <Codewindow
                            setShowcode={setShowcode}
                        />
                    }
                    {showstats &&
                        <StatsWindow
                            setShowstats={setShowstats}
                        />

                    }
                    {!selectedSessionId &&
                        <div class="disclaimer">you did not select any session yet !</div>
                    }
                    {selectedSessionId &&
                        <div className="search_students">
                            <label htmlFor="search_stu">search:</label>
                            <input
                                onChange={(event) => {
                                    searchForStudent(event.target.value);
                                }}
                                id="search_stu"
                                type="search"
                                placeholder="search for a student" />
                        </div>
                    }
                    <div className="studstatscontainer">
                        {selectedSessionId && rerender == true && users.current.length > 0 && users.current.map((student, index) => {
                            return (
                                <div className="student" key={index} id={"student" + student["user_username"]}>
                                    <div className="student_profile">
                                        <Image
                                            src={""}
                                            width={50}
                                            height={50}
                                        />
                                    </div>
                                    <div className="student_name">{student["user_username"]}</div>
                                    <div className="student_actions">
                                        <div
                                            className="seeStats"
                                            onClick={() => { setShowstats(true) }}
                                        >See stats</div>
                                        <div
                                            onClick={() => { setShowcode(true) }}
                                            className="seeCode">See code</div>
                                        <div className="blockstudent">blockuser</div>
                                    </div>
                                </div>)

                        })
                        }
                    </div>
                </div>
            </div>
        </>
    )
}