import React, { useEffect, useRef, useState } from 'react';
import { PieChart, Pie, Sector, Cell, ResponsiveContainer } from 'recharts';
const labels = ["finished", "unfinished"]
import "./updatabaleDonut.css";
const COLORS = ['#0088FE', '#00C49F'];
const RADIAN = Math.PI / 180;

/**
 * 
 * @param {*} param0 params to calculate the position of labels
 * @returns 
 */
function renderCustomizedLabel({ cx, cy, midAngle, innerRadius, outerRadius, percent, index }) {
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);
    let color = null;
    if (document.querySelector("body").classList.contains("darkmode"))
    {
        color = "white";
    }
    else{
        color = "black";
    }

    return (
        <text className="cusomtLabel" x={x} y={y} fill={color} textAnchor={x > cx ? 'start' : 'end'} dominantBaseline="central">
            {`${labels[index]} ${(percent * 100).toFixed(0)}%`}
        </text>
    );
};

// sumulate a progress 
var finished = 0;
var unfinished = 25;
function getRandomData() {
    let data = [
        { name: 'finished', value: finished },
        { name: 'inprogress', value: unfinished },
    ];
    if (finished != 25) {
        finished++;
        unfinished--;
    }
    return (
        data
    )
}
export function UpdatableDonut({InjectableForLoggin}) {
    let [data, setData] = useState(getRandomData());
    let [renderGraph, setrenderGraph] = useState(false);
    let thisChart = useRef(null);
    // Initialize the chart

    useEffect(() => {
        let intervalHolder = setInterval(() => { setData(getRandomData()) }, 4000);
        return () => {
            clearInterval(intervalHolder)
        }
    })
    return (
        <ResponsiveContainer className={"responsiveCont"} width="100%" height="100%">
            {renderGraph==true && <PieChart width={400} height={400}>
                <Pie
                    data={data}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={renderCustomizedLabel}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                >
                    {data.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                </Pie>
            </PieChart>}
            {renderGraph==false && 
                <div className='placeholder_for_piechart'>
                        
                </div>
            }
        </ResponsiveContainer>
    )
}