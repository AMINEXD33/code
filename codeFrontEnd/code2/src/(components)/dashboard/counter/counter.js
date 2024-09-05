import { useEffect, useMemo, useRef, useState } from "react";
import "./counter.css";
import { splite_date } from "../../../app/login/api_funcs";
import { Label } from "recharts";



function startCounter(sessionEndingtimeString, hour, setHours, setMinutes, setSeconds, setMakevisible, keepInrevalMemo) {
    let date = splite_date(sessionEndingtimeString)
    const st = setInterval(() => {
        let curr = new Date();
        let timeLeft = date - curr;
        let distance = new Date(timeLeft);

        let hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        let seconds = Math.floor((distance % (1000 * 60)) / 1000);

        setHours(hours);
        setMinutes(minutes);
        setSeconds(seconds);
        setMakevisible(true);
        if (hour == 0) {
            clearInterval(st);
        }
    }, 1000)
    keepInrevalMemo.current = st;
}

export default function Counter({ token, selectedSessionId, sessionsTasks }) {
    let [hour, setHours] = useState(-1);
    let [minutes, setMinutes] = useState(-1);
    let [seconds, setSeconds] = useState(-1);
    let [makevisible, setMakevisible] = useState(false);
    let keepInrevalMemo = useRef(null);
    useEffect(() => {
        console.log("heeere");
        // clear previouse intervals
        if (selectedSessionId != null && sessionsTasks.current != null) {
            try {
                let sessionEndingtimeString = sessionsTasks.current[selectedSessionId]["session_end_time"];
                startCounter(sessionEndingtimeString, hour, setHours, setMinutes, setSeconds, setMakevisible, keepInrevalMemo);
            } catch (err) {
                console.error("can't initiate counter");
                console.log("selectedSessionId   ", selectedSessionId);
                console.log("sessionsTasks", sessionsTasks);
            }
        }
        else {
            setMakevisible(false);
        }
        return () => {
            clearInterval(keepInrevalMemo.current);
        }
    }, [selectedSessionId])


    return (
        <>
            {makevisible == true &&
                <>
                    <label>time left:</label>
                    <div className="counter">
                        <div className="hours">{hour}h:</div>
                        <div className="minutes">{minutes}min:</div>
                        <div className="seconds">{seconds}sec</div>
                    </div>
                </>
            }
            {makevisible == false &&
                <div className="counter">
                    <div className="hours">00h:</div>
                    <div className="minutes">00min:</div>
                    <div className="seconds">00sec</div>
                </div>

            }
        </>
    )
}