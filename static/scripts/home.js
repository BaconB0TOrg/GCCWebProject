window.addEventListener('DOMContentLoaded', (event) => {
  window.userServers = {};
  const userServersDiv = document.getElementById('users_servers');
  if(userServersDiv !== null) {
    for(const input of userServersDiv.children) {
      console.log(input);
      // const serverIds = input.value
    }
  }
});