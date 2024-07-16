import { NextResponse } from "next/server";
import axios from "axios";
import { useRef } from "react";

function check_login(request) {
  const cookies_ = request.cookie;
  console.log(request);
  console.log("cookies = ", cookies_);
}

// This function can be marked `async` if using `await` inside
export function middleware(request) {
  const { url, method, headers, cookies } = request;
  const { pathname } = request.nextUrl;
  let cookie = cookies.get("rf");
  if (cookie === undefined && pathname != "/login") {
    return NextResponse.redirect(new URL("/login", request.url));
  } else if (cookie !== undefined && pathname != "/private/dashboard") {
    return NextResponse.redirect(new URL("/private/dashboard", request.url));
  }
  console.info("you're logged in");
  return NextResponse.next();
}

// See "Matching Paths" below to learn more
export const config = {
  matcher: ["/private/:path*", "/login", "/register"],
};
