import { NextResponse } from 'next/server'

// This function can be marked `async` if using `await` inside
export function middleware(request) {
  let tok = request.cookies.get("JWT");
  console.log("sss")
  if (tok)
  {
    console.log("you're loged in");
  }
  else{
    return NextResponse.redirect(new URL('/login', request.url))
  }
  return NextResponse.next();
}
 
// See "Matching Paths" below to learn more
export const config = {
  matcher: ['/private/:path*', ]

}