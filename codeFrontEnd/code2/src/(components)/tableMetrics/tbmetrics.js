import { useEffect, useRef } from "react"
import "./tbmetrics.css"


function setTableVisible(rbmet_holder, tbmet)
{
    rbmet_holder.current.style.display = "none";
    tbmet.current.style.display = "flex";
}
function routine(rbmet_holder, tbmet)
{
    // on wait
}

export default function Tbmetrics({InjectableForLoggin})
{
    let rbmet_holder = useRef(null);
    let tbmet = useRef(null);

    useEffect(()=>{
        routine(rbmet_holder, tbmet);
    }, [])


    return (
        <>
            <div className="tbmetrics" ref={tbmet}>
                <table id="tbmet">
                    <tbody>
                        <tr>
                            <th>total students</th>
                            <td>124</td>
                        </tr>
                        <tr>
                            <th>total lines</th>
                            <td>124</td>
                        </tr>
                        <tr>
                            <th>total errors</th>
                            <td>2</td>
                        </tr>
                        <tr>
                            <th>active students</th>
                            <td>1</td>
                        </tr>
                        <tr>
                            <th>blocked students</th>
                            <td>0</td>
                        </tr>
                        <tr>
                            <th>average code complexity</th>
                            <td>O(log(n))</td>
                        </tr>
                        <tr>
                            <th>total words writen</th>
                            <td>1293</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div className="tbmet_placehoder" ref={rbmet_holder}>
                
            </div>
        </>
    )
}