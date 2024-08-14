"use client";
import "./dashboard.css";
import { Check_login } from "@/(components)/custom_hooks/UseJwtToken";
import { useState, useRef, useEffect} from "react";
import { Topdash } from "@/(components)/dashboard/dashboardTop/top";
import DashboardOptionsStudents from "@/(components)/dashboard/dashboardOptions/dashboardOptionsStudents";
import { SessionStats } from "@/(components)/dashboard/sessionStats/sessionsStats";
import { Socks } from "@/socket_logic/customSockets";
import { useJwtToken } from "@/(components)/custom_hooks/UseJwtToken";
import Stpicker from "@/(components)/studentsessionpicker/stpicker";

function Dashboard() {
  let jwt = useRef(null); 
  // try and get the access token
  useJwtToken(jwt);
  let sockINstalce = null;

  let [contentPage, setContentPage] = useState(1);
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

  useEffect(()=>{
    sockINstalce = new Socks("ws://127.0.0.1:8000/ws/chat/", "your_valid_token", 2);
    sockINstalce.queueAmessage("request", "adasdas", (d)=>{console.log(d)}, (r)=>{console.log(r)}, 10, true)
  }, [])
  return (
    <>
      <div className="masterdiv">
        <div className="look_settings">
          <div className="" onClick={()=>{toggle_theme()}}>
            change_theme
          </div>
        </div>
        <Topdash theme={theme} setTheme={setTheme}/>
        <DashboardOptionsStudents currentPage={contentPage} setCurrentPage={setContentPage}/>
        <div className="dashboard_content" id="CONTDIV">
          {contentPage==1&& <Stpicker/>}
          {contentPage==2&& <h1>page2</h1>}
          {contentPage==3&& <h1>page3</h1>}
          {contentPage==4&& <h1>page4</h1>}

        </div>
      </div>
    </>
  );
}
export default Dashboard;
