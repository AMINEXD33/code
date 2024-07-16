"use client";
import { Suspense, useEffect } from "react";
import { Check_login } from "@/(components)/custom_hooks/UseJwtToken";
import { useState, useRef } from "react";
import { useJwtToken } from "@/(components)/custom_hooks/UseJwtToken";
import Navbar from "@/(components)/navbar/navbar";
function Dashboard() {
  let token = useRef("");
  // try and get the access token
  token.current = useJwtToken(token);
 


  return (
    <>
      <Navbar mode={1} />
      <h1>PROTECTED</h1>
    </>
  );
}
export default Dashboard;
