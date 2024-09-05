import React, { PureComponent, useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import "./lineChart.css";
var time = 0;

function incoming_data(sessionTrackedData) {
    console.warn("incoming data = ", sessionTrackedData);
    let calc = sessionTrackedData.avgDeltaLines + sessionTrackedData.avgDeltaWords;
    console.warn("----> ", calc)
    return {

        name: `minutes ${time}`,
        activity: calc,
        amt: time,
    };
}

export function LineChartCustom({InjectableForLoggin, sessionTrackedData, selectedSessionId}) {
    const [data, setData] = useState([]);

    useEffect(() => {
      console.warn("CHANGED++++++++")
      let pack_data =  incoming_data(sessionTrackedData)
      setData(prevData => [...prevData, pack_data]);
      time += 5
    }, [sessionTrackedData]);
    
    return (
      
          <ResponsiveContainer className={"responsiveCont"} width="100%" height="100%">
          {selectedSessionId && <LineChart
              width={500}
              height={300}
              data={data}
              margin={{
                top: 5,
                right: 30,
                left: 20,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis/>
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="activity" stroke="#8884d8" activeDot={{ r: 10 }} />
            </LineChart>}
            {!selectedSessionId &&
          <div className='linesgraphPlaceholder'></div>
        }
        </ResponsiveContainer>

    )
}