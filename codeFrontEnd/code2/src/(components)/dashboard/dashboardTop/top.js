import "./top.css";
import Image from "next/image";
import menue from "@/../../public/menue.svg";
import menue_dark from "@/../../public/menue.svg";
import noti_active from "@/../../public/notification_active.svg";
import noti_active_dark from "@/../../public/notification_active_dark.svg";
import noti_default from "@/../../public/notification_default.svg";
import noti_default_dark from "@/../../public/notification_default_black.svg";
import person from "@/../../public/persone.jpeg";
import { useEffect, useRef } from "react";


/**
 * this function adjust the following when the menue icon is clicked
 * -> it set's the side bar to active/inactive using their propper classes
 * -> animate the menue button using their propper classes classes
 * -> animate and adjust the padding when the side bar is active and inactive
 * @param {*} menue: a useRef reference ot the menue icon 
 */
function toggleMenue(menue) {
  let sidebar = document.getElementById("SIDEBAR");
  let contentDiv = document.getElementById("CONTDIV");

  // inactive sidebar -> active sidebar
  if (sidebar.classList.contains("sidebar_container_inactive")) {
    // side bar active animation
    sidebar.classList.remove("sidebar_container_inactive");
    sidebar.classList.add("sidebar_container_active");
    // menue icon animation
    menue.current.classList.add("menue_rotate");
    menue.current.classList.remove("menue_rotate_back");
    // adjust padding in the content div 
    contentDiv.classList.remove("inactiveSidebar");
    contentDiv.classList.add("activeSidebar");
  }
  // active sidebar -> inactive sidebar
  else if (sidebar.classList.contains("sidebar_container_active")) {
    // side bar inactive animation
    sidebar.classList.remove("sidebar_container_active");
    sidebar.classList.add("sidebar_container_inactive");
    // menue icon animation
    menue.current.classList.add("menue_rotate_back");
    menue.current.classList.remove("menue_rotate");
    // adjust padding in the content div 
    contentDiv.classList.remove("activeSidebar");
    contentDiv.classList.add("inactiveSidebar");
  }

  
}
export function Topdash({InjectableForLoggin}) {
  let menue = useRef(null);
  let icons = [menue, noti_active, noti_default];



  return (
    <div className="topdash">
      <div className="leftparttop">
        <div className="menue img_config">
          <div id="menue" className="img_config" ref={menue} onClick={() => { toggleMenue(menue) }}></div>
        </div>
        <div className="logo">code</div>
      </div>
      <div className="rightparttop img_config">
        <div className="notifications">
          <div id="nificon" className="img_config"></div>
        </div>
        <div className="profile img_config">
          <div id="profile" className="img_config"></div>
        </div>
      </div>
    </div>
  );
}
