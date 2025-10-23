// Simple auth: call /admin/login to get token and store in localStorage
document.getElementById('loginForm')?.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const form = e.target;
  const username = form.username.value;
  const password = form.password.value;

  try{
    const res = await fetch('/admin/login',{
      method:'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({username,password})
    });
    if(!res.ok) throw new Error('Login failed');
    const data = await res.json();
    localStorage.setItem('ovees_admin_token', data.access_token);
    window.location.href = '/admin/dashboard';
  }catch(err){
    alert('Login failed: '+err.message);
  }
});

// If already logged in, redirect away from login
if(location.pathname.startsWith('/admin') && location.pathname !== '/admin' && location.pathname !== '/admin/login'){
  // noop
}

