"use client";
import "./dashboard.css";
import { Check_login } from "@/(components)/custom_hooks/UseJwtToken";
import { useState, useRef, useEffect} from "react";
import { Topdash } from "@/(components)/dashboard/dashboardTop/top";
import DashboardOptions from "@/(components)/dashboard/dashboardOptions/dashboardOptions";
import { SessionStats } from "@/(components)/dashboard/sessionStats/sessionsStats";
import { useJwtToken } from "@/(components)/custom_hooks/UseJwtToken";
import Logger  from "../../../(components)/message_display/meassage_display_manager";
import { Socks } from "../../../socket_logic/customSockets";
import { callGetSessionStats } from "../../../(components)/api_caller/sockets_caller";
import {SessionSettings} from "../../../(components)/dashboard/SessionSettings/SessionSettings";
import { StudentsStats } from "../../../(components)/dashboard/studentsStats/studentsstats";
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
      sockConnReff.current = new Socks(callGetSessionStats(), token.current, 4, sockOnCloseCallback);
      clearInterval(st);
    }
  }, 1000);
}

function trimData(array=[], delete_count=0)
{
  return (array.splice(0, delete_count))
}
function statsLoad(data, sessionTrackedData, setSessionTrackedData)
{
  try{
    let loadeddta = JSON.parse(data["message"]);
    if (!loadeddta){
      return;
    }
    let prv = sessionTrackedData;
    prv.avgWords = loadeddta.avg_words;
    prv.avgLines = loadeddta.avg_lines;
    prv.avgComplexity = loadeddta.avg_complexity;
    prv.avgErrors = loadeddta.avg_errors;
    prv.totalStudentsBlocked = loadeddta.total_students_blocked;
    prv.avgDeltaWords = loadeddta.avg_words_delta
    prv.avgDeltaLines = loadeddta.avg_lines_delta;
    prv.requestLenght += 1;
    console.warn("setting new data");
    setSessionTrackedData(
      {...prv}
    )
  }catch(error)
  {
    console.warn("couldn't load data");
    console.error(error);
    return;
  }

}
function Dashboard() {
  let InjectableForLoggin = useRef(null);
  let token = useRef("");
  let sockConnReff = useRef(null);
  let [sessionTrackedData, setSessionTrackedData] = useState(
    {
      avgWords: [],
      avgLines: [],
      avgErrors: 0,
      avgComplexity:[],
      totalStudentsBlocked:0,
      avgDeltaWords: 0,
      avgDeltaLines: 0,
      requestLenght:0
    }
  )
  // try and get the access token
  useJwtToken(token)
  let [contentPage, setContentPage] = useState(1);
  let [selectedSessionId, setSelectedSessionId] = useState(null);
  const [theme, setTheme] = useState("light");
  function toggle_theme() {
    if (theme === "light") {
      setTheme("dark");
    } else {
      setTheme("light");
    }
    console.log("toggle theme")
  }
  useEffect(() => {
    injectable_ = InjectableForLoggin;
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
  const start_sending = {
    msgType: "notifme",
    msg: {"sessionId":selectedSessionId},
    successCallback: (data) => { statsLoad(data, sessionTrackedData, setSessionTrackedData) },
    failedCallback: (error) => { console.log(error) },
    expectedAfter: 0,
    permanent: false
  }

  useEffect(()=>{
    initiateSocksWhenTokenIsAvailable(token, sockConnReff, selectedSessionId, sockOnCloseCallback);
    return () => {
      if (sockConnReff.current) {
        sockConnReff.current.sock.close();
      }
    }
  }, [])

  useEffect(()=>{
    if (selectedSessionId)
    {
      queueSockMessageWhenReady(sockConnReff, [start_sending]);
    }
    else{
      logger.recommendation(injectable_, "please select a session id !");
    }
  }, [selectedSessionId])
  return (
    <>
      <div className="masterdiv" ref={InjectableForLoggin}>
        <div className="look_settings">
          <div className="" onClick={()=>{toggle_theme()}}>
            change_theme
          </div>
        </div>
        <Topdash 
          theme={theme} 
          setTheme={setTheme} 
          InjectableForLoggin={InjectableForLoggin}
        />
        <DashboardOptions 
          currentPage={contentPage} 
          setCurrentPage={setContentPage} 
          InjectableForLoggin={InjectableForLoggin}
        />
        <div className="dashboard_content" id="CONTDIV">
          {contentPage==1&& 
          <SessionStats 
            InjectableForLoggin={InjectableForLoggin} 
            token={token} 
            selectedSessionId={selectedSessionId} 
            setSelectedSessionId={setSelectedSessionId}
            sessionTrackedData={sessionTrackedData}
          />}
          {contentPage==2&& 
            <SessionSettings
              token={token}
              InjectableForLoggin={InjectableForLoggin}
              logger = {logger}
              selectedSessionId = {selectedSessionId}
            />}
          {contentPage==3&& 
            <StudentsStats
            token={token}
            InjectableForLoggin={InjectableForLoggin}
            logger = {logger}
            selectedSessionId = {selectedSessionId}
            />}
          {contentPage==4&& <h1>page4</h1>}

        </div>
      </div>
    </>
  );
}
export default Dashboard;
