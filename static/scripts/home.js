window.addEventListener('DOMContentLoaded', (event) => {
  window.userServerIds = [];
  window.serverUpdateInterval = null;

  const userServersDiv = document.getElementById('users_servers');
  
  if(userServersDiv !== null) {
    for(const input of userServersDiv.children) {
      window.userServerIds.push({
        id: input.getAttribute('data-server-id'), 
        dockerId: input.getAttribute('data-docker-id')
      });
    }
  
    window.serverUpdateInterval = setInterval(function () {
      // TODO: Multithread
      for(const serverData of window.userServerIds) {
        // console.log(serverData);
        const serverCurrPlayersElem = document.getElementById(`${serverData.id}_current_players`)
        // TODO: Get dockerid? probably can't
        fetch(`/mc_command/?docker-id=${serverData.dockerId}&command=list`).then(async (resp) => {
          re = /^There are (\d)+/;
          const respJson = await resp.json();
          const text = respJson['message'];
          const matches = text.match(re);
          // TODO: If server not up, show 0
          serverCurrPlayersElem.innerText=matches[1];
        });

      }
    }, 10000)
  }
  // TODO: Live update

});