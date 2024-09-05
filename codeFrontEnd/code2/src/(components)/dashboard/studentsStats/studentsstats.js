import { useEffect, useRef, useState } from "react";
import "./studentsstats.css";
import { getSessionUsers } from "../../api_caller/api_caller";
import axios from "axios";
import Image from "next/image";

async function getUsers(selectedSessionId, token, users, logger, InjectableForLoggin) {
    return axios.post(getSessionUsers(), { "JWT": token.current, "sessionid": selectedSessionId })
        .then(data => data.data)
        .catch(err => {
            logger.error(InjectableForLoggin, "can't get session users!");
            logger.error(InjectableForLoggin, err);
            return [];
        })
}
function seeStats(userid) {

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
                <div className="subdiv2_0">
                    {!selectedSessionId &&
                        <div class="disclaimer">you didn't select any session yet !</div>
                    }
                    <div className="studstatscontainer">
                        {selectedSessionId && rerender == true && users.current.length > 0 && users.current.map((student, index) => {
                            return (
                                <div className="studstatscontainer" key={index}>
                                    <div className="student" key={index}>
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
                                                onClick={student["user_id"]}
                                            >See stats</div>
                                            <div className="seeCode">See code</div>
                                            <div className="blockstudent">blockuser</div>
                                        </div>
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