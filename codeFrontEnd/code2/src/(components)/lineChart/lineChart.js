import React, { PureComponent, useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

let time = 0;

function simulate_incoming_data() {
    return {
        name: `minute${time}`,
        activity: Math.random() * 1841,
        amt: Math.random() * 1841,
    };
}

export function LineChartCustom() {
    const [data, setData] = useState([]);

    useEffect(() => {
        const intervalHolder = setInterval(() => {
            const new_data = simulate_incoming_data();
            time += 5;
            setData(prevData => [...prevData, new_data]);
        }, 5000);

        return () => clearInterval(intervalHolder);
    }, []); // Empty dependency array to run only once on mount
    return (
        <ResponsiveContainer className={"responsiveCont"} width="100%" height="100%">
        <LineChart
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
        </LineChart>
      </ResponsiveContainer>
    )
}