"use client";
import { useEffect, useRef } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";
/**
 * this function handles of the request is successful
 * @param {*} response the response object comming from an axios request
 * @param {*} token a reference to a useRef
 */
function handleSuccess(response, token, router, useRefRefrence) {
  console.log("in then");
  token.current = response.data["JWT"];
  useRefRefrence.current = response.data["JWT"];
  console.log("got token>>>", token.current);
  if (router.pathname == "/login") {
    router.push(`/private/dashboard/?msg=you're already loged in !`);
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
    Cookies.remove("rf");
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
  let token = useRef("");
  let endpoint = "http://127.0.0.1:8000/api/refresh/";
  let rout = useRouter();
  let ran_blocker = useRef(false);
  useEffect(() => {
    console.log("here");
    const refresh_token = async () => {
      let JWT = await axios
        .post(endpoint, {}, { withCredentials: true })
        .then((response) =>
          handleSuccess(response, token, rout, useRefRefrence),
        )
        .catch((error) => handleError(error, rout));
    };
    // refresh token when loaded
    refresh_token();

    // refresh the token every 15 minutes
    const interval = setInterval(() => {
      refresh_token();
    }, 10000);
    //15 * 40 * 1000

    return () => clearInterval(interval);
  }, []);
  return token.current;
}
