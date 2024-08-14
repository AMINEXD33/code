import axios from "axios";
import "./sessionForm.css";
import { useEffect, useRef, useState } from "react";
import { callCreateSession } from "../api_caller/api_caller";
import { callGetGroups } from "../api_caller/api_caller";
function parseTopics() {
    //hold
}

function options(value, title, indexOftheOption, setGroup) {
    let option = document.createElement("option");
    option.value = value;
    option.innerText = title;
    if (indexOftheOption === 0) {
        setGroup(value);
    }
    console.log("OPTION+", option);
    return option;
}

function loadIntoOptions(data, setGroup, selectOptions) {
    let domFrag = document.createDocumentFragment();
    for (let index = 0; index < data.length; index++) {
        let option = options(
            data[index]["session_users_groupe"],
            data[index]["session_users_groupe_name"],
            index,
            setGroup
        )
        option.addEventListener("click", () => {
            setGroup(data[index]["session_users_groupe"]);
        })
        console.log(option);
        domFrag.appendChild(option);
    }
    console.log(domFrag);
    selectOptions.current.appendChild(domFrag);
}


function loadGroups(token, setGroup, selectOptions, sessionForm, sessionFormHolder) {
    if (token.current.length > 0) {
        axios.post(callGetGroups(), { data: { "JWT": token.current } })
            .then(response => {
                console.log(response.data);
                loadIntoOptions(response.data["data"], setGroup, selectOptions);
                sessionFormHolder.current.style.display = "none"
                sessionForm.current.style.display = "flex";
            })
            .catch(error => {
                console.error(error);
            })
            .finally(() => {

            }
            )
    }
    else {
        setTimeout(() => {
            console.log("no token was passsed")
            loadGroups(token, setGroup, selectOptions, sessionForm, sessionFormHolder)
        }, 1000)
    }
}
function addBtn(setCOnfirm) { setCOnfirm(true); }

function promptCancel(setCOnfirm) { setCOnfirm(false); }

function performAction(options) {

    // do some validation here
    axios.post(callCreateSession(), {
        data: {
            "options": options.title,
            "topics": options.topics,
            "task": options.task,
            "allowru": options.allowedrun,
            "group": options.group
        }
    })
};
export default function Sessionform({ token }) {
    let topicspreview = useRef(null);
    let [confirm, setCOnfirm] = useState(false);
    let [title, setTitle] = useState("");
    let [topics, setTopics] = useState("");
    let [task, setTask] = useState("");
    let [allowedrun, setAlowedrun] = useState(false);
    let [group, setGroup] = useState("1");
    let options = { title, topics, task, allowedrun, group }
    let sessionForm = useRef(null);
    let sessionFormHolder = useRef(null);
    let selectOptions = useRef(null);
    useEffect(() => {
        console.log("heeeeeeeheeeeee ", selectOptions.current);
        setTimeout(() => { loadGroups(token, setGroup, selectOptions, sessionForm, sessionFormHolder) }, 5000);

    }, [])
    return (
        <>

            <div className="sessionform_placeholder" ref={sessionFormHolder}></div>
            <div className="sessionform" ref={sessionForm}>
                <label htmlFor="title">session title</label>
                <input type="text" id="title" onChange={(event) => { setTitle(event.target.value) }}></input>

                <div className="topicspreview" ref={topicspreview}></div>
                <label htmlFor="topics">topics of this session</label>
                <input id="topics" type="text" onChange={(event) => { setTopics(event.target.value); parseTopics(event, topicspreview); }}></input>

                <label className="task" htmlFor="task">the task of this session</label>
                <textarea id="task" onChange={(event) => { setTask(event.target.value) }}></textarea>

                <label htmlFor="allowed_to_run_code">allow to run the code</label>
                <input defaultValue={false} type="checkbox" onChange={(event) => { setAlowedrun(event.target.checked) }} id="allowed_to_run_code"></input>

                <label htmlFor="groupPicker">target group</label>
                <select value={group} ref={selectOptions} className="groups" id="groupPicker" onChange={(event) => { setGroup(event.target.value) }}>
                </select>

                {confirm == false &&
                    <>
                        <div className="promp">
                            <button id="addbtn" onClick={() => { addBtn(setCOnfirm) }}>add</button>
                        </div>
                    </>
                }
                {confirm == true &&
                    <>
                        <div className="promp">
                            <label id="confirmation">are you sure you want to add this session?</label>
                            <button id="confirmadd_yes" onClick={() => { performAction(options) }}>yes</button>
                            <button id="confirmadd_cancel" onClick={() => { promptCancel(setCOnfirm) }}>cancel</button>
                        </div>
                    </>
                }
            </div>
        </>
    )
}