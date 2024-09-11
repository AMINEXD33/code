import axios from "axios";
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";
import { callLoginApi } from "@/(components)/api_caller/api_caller";

/**
 * notnull:
 * this function retrun false if the arg passed is null
 * or undefined, if not it returns true
 * @param {*} any any value
 * @returns bool
 */
function notnull(any) {
  if (any === null || any === undefined) {
    return false;
  } else {
    return true;
  }
}
/**
 * splite_date
 * this function takes a valid date string, then it will parse
 * it into a new Date object
 * @param {*} dateString a valid date format string
 * @returns a Date object or null
 */
export function splite_date(dateString) {
  const rgx = /^([0-9]{4}.[0-9]{2}.[0-9]{2}).([0-9]{2}:[0-9]{2}:[0-9]{2})/;
  let matches = dateString.match(rgx);
  console.log(matches);
  if (matches == null || undefined) {
    return null;
  }
  if (matches.length === 0) {
    return null;
  }
  let ymd = matches[1].split("-");
  let hms = matches[2].split(":");
  let date_obj = Date.UTC(ymd[0], ymd[1] - 1, ymd[2], hms[0], hms[1], hms[2]);
  return date_obj;

}
/**
 * log_user_in:
 * this function takes a token after it's already
 * verified and make the user loged in , by saving
 * the JWT into memory and set the refresh token
 * as a cookie
 * @param {*} token :
 */
function log_user_in(
  jwtToken,
  jwtExpirationDate,
  refreshToken,
  refreshExpiration,
) {
  // check if every arg is valid
  let tmp_validate = [
    jwtToken,
    jwtExpirationDate,
    refreshToken,
    refreshExpiration,
  ];
  try {
    for (let index = 0; index < tmp_validate.length; index++) {
      if (!notnull(tmp_validate[index])) {
        return false;
      }
    }
    let parsedJwtExpirationDate = splite_date(jwtExpirationDate);
    let parsedRefreshExpirationDate = splite_date(refreshExpiration);
    // set the cookie
    try {
      Cookies.set("rf", refreshToken, {
        expires: parsedRefreshExpirationDate,
        sameSite: "None",
        secure: true,
      });
    } catch (Exception) {
      console.error("cookie set error = > ", Exception);
    }
    return true;
  } catch {
    return false;
  }
}
/**
 * this function takes a username and password and tries to log a user
 * in , if it failes it returns false, otherwise it returns true
 * @param {*} username the username -_-
 * @param {*} password the password -_-
 * @returns bool
 */
export async function login(username, password) {
  try {
    const response = await axios.post(
      callLoginApi(),
      {
        username: username,
        password: password,
      },
      {
        headers: {
          "Content-Type": "application/json",
        },
        withCredentials: true, // Send cookies with the request
      },
    );

    if (!response.data) {
      console.error("Login failed!");
      return false;
    }
    const {
      JWT,
      expiration_date,
      refresh_token,
      refresh_token_expiration_date,
    } = response.data;

    // Handle login
    let login_try = log_user_in(
      JWT,
      expiration_date,
      refresh_token,
      refresh_token_expiration_date,
    );

    if (!login_try) {
      rt.push("/login?err=login failed");
      return false;
    };

    return true;
  } catch {
    return false;
  }
}
