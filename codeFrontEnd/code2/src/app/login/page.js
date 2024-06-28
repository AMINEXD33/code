"use client";
import Navbar from "@/(components)/navbar/navbar";
import "./login.css";
import dynamic from "next/dynamic";
import { Suspense, useRef, useState } from "react";
import Input from "@/(components)/linux_inputs/input";
import BtnLoad from "@/(components)/button_loading/btnload";
import { resolve } from "styled-jsx/css";
import Link from "next/link";
function Login() {
    let logCallStatus = useRef(false);

    function handleLogin()
    {
        return new Promise((resolve, reject)=>{
            fetch("www.google.com")
            .then(data=> resolve(data))
            .catch(error=> reject(error))
        })
    }

    function handleResponse(response, error)
    {
        console.log("got response")
        console.log("rs", response);
        console.log("err", error);
        if (response != undefined){
            console.log("rs", response);
        }
        else if (error != undefined){
            console.log("err", error);
        }
    }



    const  Logo  = dynamic(()=>import("@/(components)/logo/logo", {suspense:false}))
    return (
        <>
            <Navbar activeLink={2}/>
            <div className="container">
                <div className="container_md">
                    <div className="login_panel">
                        <div className="logo_section">
                            <Logo glowing={true}/>
                        </div>
                        <div className="logininputs">
                            <Input 
                                name={"username"} 
                                type={"text"} 
                                placeholder={"username"}
                                id={"login_user"}
                            />
                            <Input 
                                name={"password"} 
                                type={"password"} 
                                placeholder={"password"}
                                id={"login_pass"}
                            />
                            <BtnLoad
                            height={50}
                            width={200}
                            radius={10}
                            content={"login"}
                            useStateVar={logCallStatus}
                            callBack = {handleLogin}
                            handleResponse = {handleResponse}
                            args={["amine","aminemeftah"]}
                            />
                        </div>
                        <div className="no_account">
                            <p>don't have an account , create one <Link href={"/"}prefetch={true}>here</Link></p>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}
export default Login;