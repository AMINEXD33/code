import React, { useRef, useEffect, useState } from "react";
import "./sessionsStats.css";
import { UpdatableDonut } from "@/(components)/donutChart/updatabaleDonut";
import { LineChartCustom } from "@/(components)/lineChart/lineChart";
import { SessionSlider } from "@/(components)/session_slider/sessionsSlider";
import { Socks } from "@/socket_logic/customSockets";
import { useJwtToken } from "@/(components)/custom_hooks/UseJwtToken";
import axios from "axios";
import { callTestReq } from "@/(components)/api_caller/api_caller";
import Tbmetrics from "@/(components)/tableMetrics/tbmetrics";
export function SessionStats({token, selectedSessionId, setSelectedSessionId}) {
  
  let chart1REf = useRef(null);
  let dataLoadedFlag = useRef(false);
  



  return (
    <div className="sessionstats">
      <div className="division0">
        <SessionSlider dataLoadedFlag={dataLoadedFlag} data={{ "data": 1 }} token={token} selectedSessionId={selectedSessionId} setSelectedSessionId={setSelectedSessionId}/>
      </div>

      <div className="division1">
        <div className="subdiv1_0">
          <div className="subdivTitle">Students Progress</div>
          <UpdatableDonut dataLoadedFlag={dataLoadedFlag} data={{ "data": 1 }} />
        </div>
        <div className="subdiv1_1">
          <div className="subdivTitle">Students Activity</div>
          <LineChartCustom dataLoadedFlag={dataLoadedFlag} data={{ "data": 1 }} />
        </div>
      </div>
      <div className="division2">
        <div className="subdiv2_0">
            <div className="subdivTitle">Students Progress</div>
            <Tbmetrics/>
        </div>
      </div>

    </div>
  );
}


