"use client";
import "./dashboard.css";
import { Check_login } from "@/(components)/custom_hooks/UseJwtToken";
import { useState, useRef, useEffect} from "react";
import { Topdash } from "@/(components)/dashboard/dashboardTop/top";
import DashboardOptions from "@/(components)/dashboard/dashboardOptions/dashboardOptions";
import { SessionStats } from "@/(components)/dashboard/sessionStats/sessionsStats";
import { useJwtToken } from "@/(components)/custom_hooks/UseJwtToken";
function Dashboard() {
  let token = useRef("");
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


  return (
    <>
      <div className="masterdiv">
        <div className="look_settings">
          <div className="" onClick={()=>{toggle_theme()}}>
            change_theme
          </div>
        </div>
        <Topdash theme={theme} setTheme={setTheme}/>
        <DashboardOptions currentPage={contentPage} setCurrentPage={setContentPage}/>
        <div className="dashboard_content" id="CONTDIV">
          {contentPage==1&& <SessionStats token={token} selectedSessionId={selectedSessionId} setSelectedSessionId={setSelectedSessionId} />}
          {contentPage==2&& <h1>page2 with a selected {selectedSessionId}</h1>}
          {contentPage==3&& <h1>page3</h1>}
          {contentPage==4&& <h1>page4</h1>}

        </div>
      </div>
    </>
  );
}
export default Dashboard;
