import { useEffect, useRef } from "react";
import "./taskathand.css";



/**
 * this function load the topics as ships to the dom
 * @param {*} topicsString the topics string
 * @param {*} topics a ref to the topics element
 */
function parseTopics(topicsString, topics) {
    let splitedTopicsString = topicsString.trim().split(" ");
    let frag = document.createDocumentFragment();
    for (let topic = 0; topic < splitedTopicsString.length; topic++)
    {
        let topicDiv = document.createElement('div');
        topicDiv.classList.add("topic");
        topicDiv.innerText = splitedTopicsString[topic];
        frag.append(topicDiv);      
    }
    topics.current.appendChild(frag);
}
/**
 * a function that will load and show the user the task when a session
 * is selected
 * @param {*} selectedSessionId the id of the session selected
 * @param {*} sessionsTasks a dict containing the data about the session
 * @param {*} title a ref to the title element
 * @param {*} topics  a ref to the topics element
 * @param {*} task  a ref to the task element
 */
function loadTaskData(selectedSessionId, sessionsTasks, title, topics, task) {
    let targetData = null;
    try { targetData = sessionsTasks.current[selectedSessionId]; } catch { console.error("damn!") };
    console.log("target data =======> ", targetData);
    if (targetData == null) {
        console.error("targetData can't be null");
        return;
    }
    parseTopics(targetData["session_topics"], topics);
    title.current.innerText = targetData["session_title"]; 
    task.current.innerText = targetData["session_task"];
}


export default function Taskathand({ token, selectedSessionId, sessionsTasks }) {
    let title = useRef(null);
    let topics = useRef(null);
    let task = useRef(null);

    useEffect(() => {
        if (selectedSessionId !== null)
        {
            title.current.innerText = "";
            topics.current.innerText = "";
            task.current.innerText = "";
            loadTaskData(selectedSessionId, sessionsTasks, title, topics, task);
        }
    }, [selectedSessionId])
    return (
        <>
            {selectedSessionId == null && <div className="taskathandplaceholder">
                <div className="disclaimer">{"you didn't select any session yet !"}</div>
            </div>}
            {selectedSessionId != null &&
                <div className="taskathand">
                    <div className="title">
                        <h4 ref={title} >Codding a quick sort algorithm</h4>
                    </div>
                    <div className="topics" ref={topics}>
                    </div>
                    <div className="task_definition">
                        <pre className="task_def_start" ref={ task }>
                            
                        </pre>
                    </div>
                </div>}

        </>
    )
}