"use client";
import Navbar from "@/(components)/navbar/navbar";
import "./login.css";
import dynamic from "next/dynamic";
import { Suspense, useRef, useState } from "react";
import Input from "@/(components)/linux_inputs/input";
import BtnLoad from "@/(components)/button_loading/btnload";
import { resolve } from "styled-jsx/css";
import Link from "next/link";
import { login } from "./api_funcs";
function Login() {
    let logCallStatus = useRef(false);
    let username= useRef("");
    let password = useRef("");
    function setUsername(text)
    {
        username.current = text;
    }
    // two functions to set the passwords from the value stream of the inputs
    function setPassword(text)
    {
        password.current = text
    }
    function handleResponse()
    {
        return (login(username.current, password.current));
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
                                onChange={setUsername}
                            />
                            <Input 
                                name={"password"} 
                                type={"password"} 
                                placeholder={"password"}
                                id={"login_pass"}
                                onChange={setPassword}
                            />
                            <BtnLoad
                            height={50}
                            width={200}
                            radius={10}
                            content={"login"}
                            useStateVar={logCallStatus}
                            callBack = {handleResponse}
                            args={[username.current,password.current]}
                            />
                        </div>
                        <div className="no_account">
                            <p>{"don't have an account create one"}</p>
                            <Link href={"/"}prefetch={true}>here</Link>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}
export default Login;