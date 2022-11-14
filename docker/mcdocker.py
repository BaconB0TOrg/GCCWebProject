import docker


def make_server(return_container=False, port=25565):
    client = docker.from_env() 
    mc_server_container = client.containers.run(image="itzg/minecraft-server", detach=True, ports={f"{port}":f"{port}"}, name="mc", environment=["EULA=True"])
    if return_container:
        return mc_server_container
    else:
        return mc_server_container.id

def run_docker_mc_command(container_id=None, message=""):
    if container_id is None:
        return
    client = docker.from_env()

    container = client.containers.get(container_id)
    output = container.exec_run(f"rcon-cli {message}")
    if output[0] != 0:
        print(f"Failed to run RCON command, exit code {output[0]}")
        return
    print(f"{output[1].decode()}")

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
    make_server()
    #run_docker_mc_command("mc", "/banlist players")
    #stop_docker("mc")  
    #start_docker("mc")  
