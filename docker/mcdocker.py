import docker

"""
Function to start a docker minecraft server.

Parameters
----------
return_container : bool
    Default to false, if true returns a container object. Documentaion on the container object is found here -> https://docker-py.readthedocs.io/en/stable/containers.html
name : String
    Default to 'mc-default', name of the docker container
port : int
    Default to 25565, outward facing port set on the minecraft server

Returns
-------
String
    Id of the docker container that was created using this function
"""
def make_server(return_container=False, name="mc-default", port=25565):
    client = docker.from_env() 
    mc_server_container = client.containers.run(image="itzg/minecraft-server", detach=True, ports={"25565":f"{port}"}, name=f"{name}", environment=["EULA=True"])
    if return_container:
        return mc_server_container
    else:
        return mc_server_container.id

"""
Function to run a RCON command.

Parameters
----------
container_id : String
  Default to None, this can either be the container id or the container name. Does the same thing either way.
message : String
    Default to '', this is the minecraft command you wish to run on 'x' docker container

Returns
-------
String
    Returns the output of the minecraft command entered
None
    Returns nothing if the link to the docker container is invalid
"""
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

"""
Function to stop the docker container specified.

Parameters
----------
container_id : String
  Default to None, this can either be the container id or the container name. Does the same thing either way.

Returns
-------
None
"""
def stop_docker(container_id=None):
    if container_id is None:
        return
    client = docker.from_env()

    container = client.containers.get(container_id)
    container.stop()

"""
Function to start the docker container specified.

Parameters
----------
container_id : String
  Default to None, this can either be the container id or the container name. Does the same thing either way.

Returns
-------
None
"""
def start_docker(container_id=None):
    if container_id is None:
        return
    client = docker.from_env()
    
    container = client.containers.get(container_id)
    container.start()



if __name__ == "__main__":
    make_server()
    make_server(name="mc-default-2", port=25567)
    #run_docker_mc_command("mc", "/banlist players")
    #stop_docker("mc")  
    #start_docker("mc")  
