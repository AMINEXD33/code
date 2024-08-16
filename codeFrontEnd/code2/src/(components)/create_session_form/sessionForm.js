import axios from "axios";
import "./sessionForm.css";
import { useEffect, useRef, useState } from "react";
import { callCreateSession } from "../api_caller/api_caller";
import { callGetGroupsGetLangues } from "../api_caller/api_caller";
import Logger from "../message_display/meassage_display_manager";
var loggerInjectable;
var logger;
/**
 * this function parses the topics the user is typing and shows it nicely
 * @param {*} event the event
 * @param {*} setTopicShipsValues function that sets the value of each ships in an array
 * @param {*} setTopics function that sets the value of the input topics
 * @param {*} setControlledInp fucntion to controll the input value of the input 
 * @returns 
 */
function parseTopics(event, setTopicShipsValues, setTopics, setControlledInp) {
    let splitedTopics = event.target.value.split(" ");

    for (let index = 0; index < splitedTopics.length; index++) {
        splitedTopics[index].trim();
    }
    let tmp = [];
    if (splitedTopics[splitedTopics.length - 1].length >= 30) { return };
    for (let index = 0; index < splitedTopics.length; index++) {
        if (tmp.length > 4) { break; }
        let shortened = "";
        if (splitedTopics[index].length >= 30) {
            for (let x = 0; x <= 30; x++) {
                shortened += splitedTopics[index][x];
            }
            if (shortened.length > 0) {
                tmp.push(<div className="topic_ship">{shortened}</div>);
            }

        }
        else {
            if (splitedTopics[index].length > 0) {
                tmp.push(<div className="topic_ship">{splitedTopics[index]}</div>);
            }
        }
    }
    if (tmp.length > 4) { return; }
    setTopicShipsValues(tmp);
    setTopics(event.target.value);
    setControlledInp(event.target.value);
}

/**
 * 
 * @param {*} value 
 * @param {*} title 
 * @param {*} indexOftheOption 
 * @param {*} setGroup 
 * @returns 
 */
function options(value, title, indexOftheOption, setGroup) {
    let option = document.createElement("option");
    option.value = value;
    option.innerText = title;
    if (indexOftheOption === 0) {
        setGroup(value);
    }
    return option;
}

/**
 * this function loads the data comming from loadInitialData() request
 * and populates the group select dropdown input.
 * note that this function loads an event listiner that has a callback
 * that has the correct value, so the logic is not reliying on the front by
 * any means
 * @param {*} data the data comming from the API
 * @param {*} setGroup function that sets the  value of a group 
 * @param {*} selectOptions the reference to the the <select/> element
 */
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

/**
 * this function loads the data comming from loadInitialData() request
 * and populates the languages select dropdown input.
 * note that this function loads an event listiner that has a callback
 * that has the correct value, so the logic is not reliying on the front by
 * @param {*} data the data comming from the API
 * @param {*} setLangue function that sets the value of a language
 * @param {*} selectLange the reference to the <select/> element
 */
function loadIntoLangs(data, setLangue, selectLange) {
    let domFrag = document.createDocumentFragment();
    for (let index = 0; index < data.length; index++) {
        let option = options(
            data[index]["languages_id"],
            data[index]["languages_name"],
            index,
            setLangue
        )
        option.addEventListener("click", () => {
            setLangue(data[index]["languages_id"]);
        })
        console.log(option);
        domFrag.appendChild(option);
    }
    console.log(domFrag);
    selectLange.current.appendChild(domFrag);
}

/**
 * this function is responsible for loading groups, and languages available 
 * via the API, and passes each chunk of data ["groups"] and ["languages"] to
 * two function to handle the display and functionality  loadIntoOptions() and loadIntoLangs()
 * note1: the function will try to re-execute it self if no token is available (just a reliablity code)
 * note2: this is the function that controlls if the element is still in load mode or not
 * @param {*} token 
 * @param {*} setLangue 
 * @param {*} selectLange 
 * @param {*} setGroup 
 * @param {*} selectOptions 
 * @param {*} sessionForm 
 * @param {*} sessionFormHolder 
 */
function loadInitialData(token, setLangue, selectLange, setGroup, selectOptions, sessionForm, sessionFormHolder) {
    if (token.current.length > 0) {
        axios.post(callGetGroupsGetLangues(), { data: { "JWT": token.current } })
            .then(response => {
                loadIntoOptions(response.data["data"]["groups"], setGroup, selectOptions);
                loadIntoLangs(response.data["data"]["languages"], setLangue, selectLange)
                sessionFormHolder.current.style.display = "none"
                sessionForm.current.style.display = "flex";
            })
            .catch(error => {
                if (error.response) {
                    logger.error(loggerInjectable, error.response.data);
                }
                else{
                    logger.error(loggerInjectable, "error fetching the groups and languages");
                }
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

/**
 * this function switches from one state to state,
 * the first state is when the user clicks add, 
 * the second is when two buttons get displayed , yes and cancel
 * @param {*} setCOnfirm function that sets the new state
 */
function addBtn(setCOnfirm) { setCOnfirm(true); }

/**
 * this function resets the stat, to displaying teh add button
 * @param {*} setCOnfirm function that sets the new state
 */
function promptCancel(setCOnfirm) { setCOnfirm(false); }

/**
 * this function is the function that posts the data to api to attempt to 
 * create the new session, and it disables the two buttns until the request is
 * done
 * @param {*} options an object containing all the inputs the user provided
 * @param {*} token the access token
 * @param {*} confirmaddBtn the reference to the ok button  
 * @param {*} cancelBtn the refrence to the cancel
 */
function performAction(options, token, confirmaddBtn, cancelBtn) {
    confirmaddBtn.current.setAttribute("disabled", "");
    cancelBtn.current.setAttribute("disabled", "");
    // do some validation here
    axios.post(callCreateSession(), {
        data: {
            "JWT": token.current,
            "title": options.title,
            "topics": options.topics,
            "task": options.task,
            "allowru": options.allowedrun,
            "duration": options.sessionrange,
            "group": options.group,
            "langue": options.langue

        }
    })
        // show some error to the user
        .then(data => { 
            logger.success(loggerInjectable, "session created successfully !");
        })
        .catch(error => {
            if (error.response) {
                logger.error(loggerInjectable, error.response.data);
            }
            else{
                logger.error(loggerInjectable, "error posting data for a new session to API");
            }
        
        })
        .finally(() => {
            confirmaddBtn.current.removeAttribute("disabled", "");
            cancelBtn.current.removeAttribute("disabled", "");
        }
        )
};

export default function Sessionform({ token, InjectableForLoggin}) {
    // pass the refremces to some global vars for easy access
    loggerInjectable = InjectableForLoggin;
    logger = new Logger();

    const MAX = 10;
    let topicspreview = useRef(null);
    let [confirm, setCOnfirm] = useState(false);
    let [title, setTitle] = useState("");
    let [topics, setTopics] = useState("");
    let [task, setTask] = useState("");
    let [allowedrun, setAlowedrun] = useState(false);
    let [group, setGroup] = useState("1");
    let [sessionrange, setSessionrange] = useState(1);
    let sessionForm = useRef(null);
    let sessionFormHolder = useRef(null);
    let selectOptions = useRef(null);
    let selectLange = useRef(null);
    let [langue, setLangue] = useState("");
    let topicShips = useRef(null);
    let [TopicShipsValues, setTopicShipsValues] = useState([]);
    let [controlledInp, setControlledInp] = useState("");
    let confirmaddBtn = useRef(null);
    let cancelBtn = useRef(null);
    let options = { title, topics, task, allowedrun, group, sessionrange, langue };
    
    // load data
    useEffect(() => {
        loadInitialData(token, setLangue, selectLange, setGroup, selectOptions, sessionForm, sessionFormHolder);
    }, [])
    return (
        <>

            <div className="sessionform_placeholder" ref={sessionFormHolder}></div>
            <div className="sessionform" ref={sessionForm}>
                <label htmlFor="title">session title</label>
                <input type="text" id="title" onChange={(event) => { setTitle(event.target.value) }}></input>

                <div className="topicspreview" ref={topicspreview}></div>
                <label htmlFor="topics">topics of this session</label>
                <div className="topic_ships" ref={topicShips}>
                    {TopicShipsValues.map((topic, index) => (
                        <div key={index} className="topic_ship">
                            {topic}
                        </div>
                    ))}
                </div>
                <input value={controlledInp} id="topics" type="text" onChange={(event) => { parseTopics(event, setTopicShipsValues, setTopics, setControlledInp); }}></input>

                <label className="task" htmlFor="task">the task of this session</label>
                <textarea id="task" onChange={(event) => { setTask(event.target.value) }}></textarea>

                <label htmlFor="allowed_to_run_code">allow to run the code</label>
                <input defaultValue={false} type="checkbox" onChange={(event) => { setAlowedrun(event.target.checked) }} id="allowed_to_run_code"></input>

                <label htmlFor="groupPicker">target group</label>
                <select value={group} ref={selectOptions} className="groups" id="groupPicker" onChange={(event) => { setGroup(event.target.value) }}>
                </select>

                <label htmlFor="languePicker">target group</label>
                <select value={langue} ref={selectLange} className="groups" id="languePicker" onChange={(event) => { setLangue(event.target.value) }}>
                </select>

                <label>Session duration {sessionrange} Hours</label>
                <input id="sessionrannge" value={sessionrange} type="number" min={1} max={MAX} onChange={(event) => { setSessionrange(parseFloat(event.target.value)) }}></input>
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
                            <button id="confirmadd_yes" ref={confirmaddBtn} onClick={() => { performAction(options, token, confirmaddBtn, cancelBtn) }}>yes</button>
                            <button id="confirmadd_cancel" ref={cancelBtn} onClick={() => { promptCancel(setCOnfirm) }}>cancel</button>
                        </div>
                    </>
                }
            </div>
        </>
    )
}