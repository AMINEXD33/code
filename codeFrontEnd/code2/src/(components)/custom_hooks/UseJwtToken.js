import { useEffect, useRef } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";
import { callRefreshApi } from "../api_caller/api_caller";
/**
 * this function handles of the request is successful
 * @param {*} response the response object comming from an axios request
 * @param {*} token a reference to a useRef
 */
function handleSuccess(response, router, useRefRefrence) {
  try{
    console.log("in then");
    useRefRefrence.current = response.data["JWT"];
    console.log("got token>>>", useRefRefrence.current);
    if (router.pathname == "/login") {
      // router.push(`/private/dashboardstudents/?msg=you're already loged in !`);
    }
  }
  catch(Exception){
    console.log(Exception)
  }
}
/**
 *
 * @param {*} err error object from a failed axios request
 * @param {*} router a reference to a use router
 */
function handleError(err, router) {
  try {
    console.log("DAMN");
    console.log(err);
    console.log("try rerouting");
    console.log(err);
    // Cookies.remove("rf");
    router.push(
      `../login/?msg=you're loged out either the token was expired or deleted`,
    );
    console.log("whaaaat");
  } catch (Exception) {
    console.log(Exception);
  }
}
/**
 * useJwtToken
 * a costum hook that makes sure to keep refreshing
 * the token every 15 minutes, if the token couldn't refresh
 * the hook will redirect the user to login
 * @param {useRef}a reference to some useref to keep updated with the latest token
 */
export function useJwtToken(useRefRefrence) {
  let endpoint = callRefreshApi();
  let rout = useRouter();
  useEffect(() => {
    
    let rfcookie = Cookies.get("rf");
    const refresh_token = async () => {
      let JWT = await axios
        .post(endpoint, {

        }, 
        { withCredentials: true , headers:{"refresh":rfcookie}})
        .then((response) =>
          handleSuccess(response, rout, useRefRefrence),
        )
        .catch((error) => handleError(error, rout));
    };
    // refresh token when loaded
    refresh_token();

    // refresh the token every 15 minutes
    const interval = setInterval(() => {
      refresh_token();
    }, 10 * 40 * 1000);
    //15 * 40 * 1000

    return () => clearInterval(interval);
  }, []);
}
