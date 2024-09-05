"use client";
import "./dashboard.css";
import { Check_login } from "@/(components)/custom_hooks/UseJwtToken";
import { useState, useRef, useEffect } from "react";
import { Topdash } from "@/(components)/dashboard/dashboardTop/top";
import DashboardOptionsStudents from "@/(components)/dashboard/dashboardOptions/dashboardOptionsStudents";
import { SessionStats } from "@/(components)/dashboard/sessionStats/sessionsStats";
import { Socks } from "../../../socket_logic/customSockets";
import { useJwtToken } from "@/(components)/custom_hooks/UseJwtToken";
import { callTrackSession } from "../../../(components)/api_caller/sockets_caller";
import Stpicker from "@/(components)/studentsessionpicker/stpicker";
import Logger from "../../../(components)/message_display/meassage_display_manager";
import CryptoJS from 'crypto-js';
var injectable_ = null;
var logger = new Logger();
function sockOnCloseCallback() {
  logger.error(injectable_, "socket disconnected, please reload the page!");
}
/**
 * this function pushes a list of socks jobs to the queue to be executed
 * @param {*} sockConnection the Socks object
 * @param {*} sockRequests the Socks jobs array
 */
function queueSockMessageWhenReady(sockConnectionRef, sockRequests) {
  console.warn("trying to queue");
  const intervalId = setInterval(() => {
    if (sockConnectionRef.current) {
      clearInterval(intervalId);

      for (let sockRequest = 0; sockRequest < sockRequests.length; sockRequest++) {
        console.warn("msg queeed !!");
        sockConnectionRef.current.queueAmessage(
          sockRequests[sockRequest].msgType,
          sockRequests[sockRequest].msg,
          sockRequests[sockRequest].successCallback,
          sockRequests[sockRequest].failedCallback,
          sockRequests[sockRequest].expectedAfter,
          sockRequests[sockRequest].permanent
        );
      }
    }
  }, 300);

}

/**
* this function will only initiate the Sock object when the token
* to make the request is available, then it's passing the jobs 
* to the queue to be executed
* @param {*} token  the token
* @param {*} sockRequests  the Socks jobs array 
*/
function initiateSocksWhenTokenIsAvailable(token, sockConnReff, sockOnCloseCallback_ref) {

  const st = setInterval(() => {
    if (token && token.current) {
      sockConnReff.current = new Socks(callTrackSession(), token.current, 4, sockOnCloseCallback);
      clearInterval(st);
    }
  }, 1000);
}

/**
 * this function tracks if the user is leaving the page
 * and it queues a message to the server when the event is triggered
 * @param {*} metrics the metrics array containing the useRefs
 * @param {*} susActivity the predifined request
 * @param {*} sockConnReff the reference to the sock object
 */
function TrackIfUserMouse(metrics, susActivity, sockConnReff) {
  let mainWindow = document.body;

  let timeyouleft = null;
  // record the time when the user left
  mainWindow.addEventListener("mouseleave", (event) => {
    console.log(event.relatedTarget);
    console.log(event.target);
    // ignore an element that causes conflict
    if (event.relatedTarget || event.relatedTarget == '.monaco-highlighted-label') {
      return;
    }
    timeyouleft = new Date();
  })
  // when user comes back
  mainWindow.addEventListener("mouseenter", (event) => {
    // ignore an element that causes conflict
    console.log(event.relatedTarget);
    console.log(event.target);
    if (event.relatedTarget || event.relatedTarget == '.monaco-highlighted-label') {
      return;
    }
    let curr = new Date();// current time
    let diffrent = (curr - timeyouleft) / 1000;// the diffrence
    if (diffrent < 1.3) { return; }// don't send anything that is concidered spam
    let suslist = metrics.sus.length;// lenght if the sus array
    if (suslist < 10) {
      metrics.sus.push({
        lefttiming: new Date(timeyouleft),
        diffrence: diffrent
      })
    }
    else if (suslist >= 10) {// keep removing from first and add to last
      metrics.sus.splice(0, 1);
      metrics.sus.push({
        lefttiming: new Date(timeyouleft),
        diffrence: diffrent
      })
    }
    queueSockMessageWhenReady(sockConnReff, [susActivity]);
    timeyouleft = null;
  })

}

function periodicCodeSubmition(metrics, lastCodeSubmissionHash, sockConnReff, updateCodeRequest, sig)
{
  const interval = setInterval(()=>{
      if (sig.current)
      {
        console.info("sig recieved clearing interval");
        clearInterval(interval);
      }
      // recalculating hash
      let hash = CryptoJS.SHA224(metrics.code).toString();
      // compair
      if (hash === lastCodeSubmissionHash.current)
      {
        return; // don't do anything the code is the same
      }
      // update hash
      lastCodeSubmissionHash.current = hash;
      queueSockMessageWhenReady(sockConnReff, [updateCodeRequest]);
  }, 15000);
}


function Dashboard() {
  let token = useRef(null);
  // try and get the access token
  useJwtToken(token);
  // this is the session id selected by the user
  let [selectedSessionId, setSelectedSessionId] = useState(null);
  // when the sessions are loaded, the data will be stored here
  // for future references
  let sessionsTasks = useRef({});
  // keep track of the current page the user clicked
  let [contentPage, setContentPage] = useState(1);
  // keep track of the thems
  const [theme, setTheme] = useState("light");
  // an injectable element for displaying errors
  let InjectableForLoggin = useRef(null);
  // a reference that will hold the socks object after waiting for the token
  let sockConnReff = useRef(null);
  // a hash that makes it possible to know if the user code that is going to be submited the same
  // or changed 
  let lastCodeSubmissionHash = useRef(null);
  // counter interval memorization to keep cleaning stuff
  let sig = useRef(false);
  let metrics = useRef([
    {
      sessionid: selectedSessionId,
      code: ""
    },
    {
      sessionid: selectedSessionId,
      sus: []
    },
    {
      sessionid: selectedSessionId,
      activityStartedAt: "null",
      activityEndedAt: "null",
    }
  ]);
  // socks request
  const susActivity = {
    msgType: "susActivity",
    msg: metrics.current[1],
    successCallback: (data) => { console.warn(data) },
    failedCallback: (error) => { console.log(error) },
    expectedAfter: 0,
    permanent: false
  }
  const updateCodeRequest = {
    msgType: "codingActivity",
    msg: metrics.current[0],
    successCallback: (data) => { console.warn(data) },
    failedCallback: (error) => { console.log(error) },
    expectedAfter: 0,
    permanent: false
  }

  function toggle_theme() {
    if (theme === "light") {
      setTheme("dark");
    } else {
      setTheme("light");
    }
    console.log("toggle theme")
  }
  useEffect(() => {
    let body = document.getElementById("bod");
    if (theme === "light") {
      body.classList.remove("darkmode");
      localStorage.setItem("theme", "light");
    } else {
      body.classList.add("darkmode");
      localStorage.setItem("theme", "dark");
    }
    console.log("set body")
  }, [theme]);
  useEffect(() => {
    injectable_ = InjectableForLoggin;
    initiateSocksWhenTokenIsAvailable(token, sockConnReff, selectedSessionId, sockOnCloseCallback);
    return () => {
      if (sockConnReff.current) {
        sockConnReff.current.sock.close();
      }
    }
  }, []);

  useEffect(() => {
    // only if the session id is not null
    if (selectedSessionId != null) {
      // update the session id for the metrics
      for (let index = 0; index < metrics.current.length; index++) {
        metrics.current[index].sessionid = selectedSessionId;
      }
      metrics.current[0].code = "";
      // start tracking events
      TrackIfUserMouse(metrics.current[1], susActivity, sockConnReff);
      periodicCodeSubmition(metrics.current[0], lastCodeSubmissionHash, sockConnReff, updateCodeRequest, sig);
    }
  }, [selectedSessionId])
  return (
    <>
      <div className="masterdiv" ref={InjectableForLoggin}>
        <div className="look_settings">
          <div className="" onClick={() => { toggle_theme() }}>
            change_theme
          </div>
        </div>
        <Topdash
          theme={theme}
          setTheme={setTheme}
        />
        <DashboardOptionsStudents
          currentPage={contentPage}
          setCurrentPage={setContentPage}
        />
        <div className="dashboard_content" id="CONTDIV">
          {contentPage == 1 &&
            <Stpicker
              sockConnReff={sockConnReff}
              sessionsTasks={sessionsTasks}
              InjectableForLoggin={InjectableForLoggin}
              token={token}
              selectedSessionId={selectedSessionId}
              setSelectedSessionId={setSelectedSessionId}
              metrics={metrics}
            />
          }
          {contentPage == 2 && <h1>page2</h1>}
          {contentPage == 3 && <h1>page3</h1>}
          {contentPage == 4 && <h1>page4</h1>}
        </div>
      </div>
    </>
  );
}
export default Dashboard;
