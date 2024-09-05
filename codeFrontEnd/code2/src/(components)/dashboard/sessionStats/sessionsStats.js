import React, { useRef, useEffect, useState } from "react";
import "./sessionsStats.css";
import { UpdatableDonut } from "@/(components)/donutChart/updatabaleDonut";
import { LineChartCustom } from "@/(components)/lineChart/lineChart";
import { SessionSlider } from "@/(components)/session_slider/sessionsSlider";
import { useJwtToken } from "@/(components)/custom_hooks/UseJwtToken";
import axios from "axios";
import { callTestReq } from "@/(components)/api_caller/api_caller";
import Tbmetrics from "@/(components)/tableMetrics/tbmetrics";
import { callTrackSession } from "../../api_caller/sockets_caller";

import Socks from "../../../socket_logic/customSockets";
import  initiateSocksWhenTokenIsAvailable  from "../../../app/private/waitingUtils";


export function SessionStats({ 
  token, 
  selectedSessionId, 
  setSelectedSessionId, 
  InjectableForLoggin,
  sessionTrackedData,
}) {

  let chart1REf = useRef(null);
  let dataLoadedFlag = useRef(false);

  useEffect(() => {
    console.log("here!!????")
    

  })

  return (
    <div className="sessionstats">
      <div className="division0">
        <SessionSlider
          InjectableForLoggin={InjectableForLoggin}
          dataLoadedFlag={dataLoadedFlag}
          data={{ "data": 1 }}
          token={token}
          selectedSessionId={selectedSessionId}
          setSelectedSessionId={setSelectedSessionId}
        />
      </div>

      <div className="division1">
        <div className="subdiv1_0">
          <div className="subdivTitle">Students Progress</div>
          <UpdatableDonut
            InjectableForLoggin={InjectableForLoggin}
            dataLoadedFlag={dataLoadedFlag}
            data={{ "data": 1 }}
            selectedSessionId={selectedSessionId}
            sessionTrackedData={sessionTrackedData}
          />
        </div>
        <div className="subdiv1_1">
          <div className="subdivTitle">Students Activity</div>
          <LineChartCustom
            InjectableForLoggin={InjectableForLoggin}
            dataLoadedFlag={dataLoadedFlag}
            data={{ "data": 1 }}
            sessionTrackedData={sessionTrackedData}
            selectedSessionId={selectedSessionId}
          />
        </div>
      </div>
      <div className="division2">
        <div className="subdiv2_0">
          <div className="subdivTitle">Students Progress</div>
          <Tbmetrics
            InjectableForLoggin={InjectableForLoggin}
            sessionTrackedData={sessionTrackedData}
            selectedSessionId={selectedSessionId}
          />
        </div>
      </div>

    </div>
  );
}


