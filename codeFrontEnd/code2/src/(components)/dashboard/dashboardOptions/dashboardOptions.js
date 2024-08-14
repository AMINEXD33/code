"use client";
import { useEffect, useRef, useState } from "react";
import axios from "axios";
import "./dashboardOptions.css";
import { callSessiondata } from "@/(components)/api_caller/api_caller";
import Cookies from "js-cookie";
import Image from "next/image";


function dataRequestExecuter(JwtTokenRef) {
  if (!JwtTokenRef) {
    console.log("no access token");
  }
  let call = axios.post(
    callSessiondata(),
    {},
    { headers: { access_token: JwtTokenRef } },
  );
}
/**
 * this function removes the active property from all elements
 * @param {Array[object]} optionsList : all options list
 * @returns 
 */
function removeActiveOptions(optionsList) {
  if (!optionsList) {
    console.log("no optionlist was passef");
    return;
  }
  for (let x = 0; x < optionsList.length; x++)
  {
    optionsList[x].current.classList.remove("option_current_page");
  }
}
/**
 * this function switches between pages when the user clicks some option
 * @param {*} currPage : a useState read var that represent the current page the user is in
 * @param {object} setCurrPage : a useState setter to set the current page
 * @param {Number} clickedpage : an int that represent what page the user clicked
 * @param {useRef.current} me : a refrence to the clicked element
 * @param {Array[object]} optionsList : all options list
 * @returns 
 */
function figurePage(currPage, setCurrPage, clickedpage, me, optionsList) {
  if (!me || !currPage || !setCurrPage || !clickedpage) {
    console.log("one arg is not set");
    return;
  }
  if (currPage != clickedpage) {
    removeActiveOptions(optionsList);
    setCurrPage(clickedpage);
    me.classList.add("option_current_page");
  } else {
    console.log("no need to switch");
  }
}
export default function DashboardOptions({ currentPage, setCurrentPage }) {
  let optionsList = [useRef(null), useRef(null), useRef(null), useRef(null)];
  
  // just set the first option as active on first mount
  useEffect(()=>{
    optionsList[0].current.classList.add("option_current_page");
  },[])
  return (
    <>
      <div className="sidebar_container sidebar_container_active" id="SIDEBAR">
        <div className="sidebar">

          <div className="option" ref={optionsList[0]} onClick={() => { figurePage(currentPage, setCurrentPage, 1, optionsList[0].current, optionsList) }}>
            <div className="img_config" id="session_stats"></div>
            <p>session stats</p>
          </div>

          <div className="option" ref={optionsList[1]} onClick={() => { figurePage(currentPage, setCurrentPage, 2, optionsList[1].current, optionsList) }}>
            <div className="img_config" id="session_settings"></div>
            <p>session settings</p>
          </div>

          <div className="option" ref={optionsList[2]} onClick={() => { figurePage(currentPage, setCurrentPage, 3, optionsList[2].current, optionsList) }}>
            <div className="img_config" id="students"></div>
            <p>students stats</p>
          </div>

          <div className="option" ref={optionsList[3]} onClick={() => { figurePage(currentPage, setCurrentPage, 4, optionsList[3].current, optionsList) }}>
            <div className="img_config" id="students_settings"></div>
            <p>session controle</p>
          </div>
        </div>
      </div>
    </>
  );
}
