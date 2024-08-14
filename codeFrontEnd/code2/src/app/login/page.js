"use client";
import Navbar from "@/(components)/navbar/navbar";
import "./login.css";
import dynamic from "next/dynamic";
import { Suspense, useEffect, useRef, useState } from "react";
import Input from "@/(components)/linux_inputs/input";
import BtnLoad from "@/(components)/button_loading/btnload";
import Link from "next/link";
import { login } from "./api_funcs";
import useJwtToken from "@/(components)/custom_hooks/UseJwtToken";
import { useRouter } from "next/navigation";
function Login() {
  let logCallStatus = useRef(false);
  let username = useRef("");
  let password = useRef("");
  let flag = useRef(false);
  let router = useRouter();
  function setUsername(text) {
    username.current = text;
  }
  // two functions to set the passwords from the value stream of the inputs
  function setPassword(text) {
    password.current = text;
  }
  async function handleResponse() {
    let loginState = await login(username.current, password.current);
    if (loginState == true) {
      console.log("state of login is , ", flag.current);
      router.push("/private/dashboard?msg=you're loged in haha");
    }

    return loginState;
  }

  const Logo = dynamic(
    () => import("@/(components)/logo/logo", { suspense: false }),
  );
  return (
    <>
      {/*this is for making sure that the user is loged in*/}
      <Navbar activeLink={2} />
      <div className="container">
        <div className="container_md centerize">
          <div className="login_panel">
            <div className="logo_section">
              <Logo glowing={true} />
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
                id={"logbtn"}
                height={50}
                width={200}
                radius={10}
                content={"login"}
                useStateVar={logCallStatus}
                callBack={handleResponse}
                args={[username.current, password.current]}
              />
            </div>
            <div className="no_account">
              <p>{"don't have an account create one "}</p>
              <Link href={"/"} prefetch={true} id="llk1">
                {" "}
                here
              </Link>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
export default Login;
