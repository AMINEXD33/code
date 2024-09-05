import { useEffect, useRef } from "react"
import "./tbmetrics.css"



export default function Tbmetrics({
    InjectableForLoggin, 
    sessionTrackedData,
    selectedSessionId
})
{
    let rbmet_holder = useRef(null);
    let tbmet = useRef(null);

    useEffect(()=>{
        console.warn("[1231]> ", sessionTrackedData);
    }, [sessionTrackedData])
    return (
        <>
        {selectedSessionId &&
            <div className="tbmetrics">
                <table id="tbmet">
                    <tbody>
                        <tr>
                            <th>average lines</th>
                            <td>{sessionTrackedData.avgLines}</td>
                        </tr>
                        <tr>
                            <th>average words</th>
                            <td>{sessionTrackedData.avgWords}</td>
                        </tr>
                        <tr>
                            <th>blocked students</th>
                            <td>{sessionTrackedData.totalStudentsBlocked}</td>
                        </tr>
                        <tr>
                            <th>average errors</th>
                            <td>{sessionTrackedData.avgErrors}</td>
                        </tr>
                        <tr>
                            <th>average code complexity</th>
                            <td>{sessionTrackedData.avgComplexity}</td>
                        </tr>
                    </tbody>
                </table>
            </div>}
            {!selectedSessionId &&
                <div className="tbmet_placehoder" ref={rbmet_holder}>
                </div>
            }
        </>
    )
}