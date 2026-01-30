import { NextRequest, NextResponse } from 'next/server';

// Middleware to protect routes
export function middleware(request: NextRequest) {
  // Get the token from cookies (primary) or Authorization header (fallback)
  let token = request.cookies.get('authToken')?.value || null;

  // If not in cookies, check Authorization header as fallback
  if (!token) {
    const authHeader = request.headers.get('authorization');
    if (authHeader && authHeader.startsWith('Bearer ')) {
      token = authHeader.substring(7);
    }
  }

  // Define protected routes
  const protectedPaths = ['/dashboard', '/tasks', '/chat']; // Added /chat to protected paths
  const isProtectedPath = protectedPaths.some(path =>
    request.nextUrl.pathname.startsWith(path)
  );

  // If user is trying to access a protected route without a token
  if (isProtectedPath && !token) {
    // Redirect to login page
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // If user is logged in and trying to access auth pages, redirect to dashboard
  const authPaths = ['/login', '/register'];
  const isAuthPath = authPaths.some(path =>
    request.nextUrl.pathname.startsWith(path)
  );

  if (token && isAuthPath) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

// Define which paths the middleware should run on
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};