import docker


def make_server(return_container=False):
    client = docker.from_env() 
    mc_server_container = client.containers.run(image="itzg/minecraft-server", detach=True, ports={'25565':'25565'}, name="mc", environment=["EULA=True"])
    if return_container:
        return mc_server_container
    else:
        return mc_server_container.id

def run_docker_mc_command(container_id=None, message=""):
    if container_id is None:
        return
    client = docker.from_env()

    container = client.containers.get(container_id)
    container.exec_run(f"rcon-cli {message}")

def stop_docker(container_id=None):
    if container_id is None:
        return
    client = docker.from_env()

    container = client.containers.get(container_id)
    container.stop()

    
def start_docker(container_id=None):
    if container_id is None:
        return
    client = docker.from_env()
    
    container = client.containers.get(container_id)
    container.start()



if __name__ == "__main__":
    #make_server()
    #run_docker_mc_command("mc", "/say hi")
    #stop_docker("mc")  
    start_docker("mc")  
