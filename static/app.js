// GolfGives — utility functions

function logout() {
  localStorage.removeItem('token');
  window.location.href = '/';
}

// Redirect logged-in users away from login/signup
if ((window.location.pathname === '/login' || window.location.pathname === '/signup') && localStorage.getItem('token')) {
  window.location.href = '/dashboard';
}
