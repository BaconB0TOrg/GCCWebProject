import docker 
import configparser
import os

# File configuration
dirname = os.path.dirname(__file__)
dir = os.path.join(dirname, f'..\\..\\')

def make_server(return_container=False, name="mc-default", port=25565):
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
    try:
        client = docker.from_env() 
        folder = os.path.join(dir, f'{name}')
        mc_server_container = client.containers.run(image="itzg/minecraft-server", detach=True, ports={"25565":f"{port}"}, name=f"{name}", environment=["EULA=True"], mounts=[docker.types.Mount(target="/data", source=f"{folder}", type="bind")])
    except Exception as e:
        print(e)

    if return_container:
        return mc_server_container
    else:
        return mc_server_container.id_attribute


def run_docker_mc_command(container_id=None, message=""):
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
    if container_id is None:
        return
    client = docker.from_env()

    try:
        container = client.containers.get(container_id)
        output = container.exec_run(f"rcon-cli {message}")
        if output[0] != 0:
            # connection made but rcon not ready
            print(f"Failed to run RCON command, exit code {output[0]}")
            print(f"error: {output[1]}")
            return "Something went wrong, please try again shortly"
        # if everything is good
        return output[1].decode()
    except Exception as e:
        print(e)
    # exception is thrown. Docker fails to connect.
    return "Something went wrong, please make sure your server is running."

def stop_docker(container_id=None):
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
    if container_id is None:
        return
    
    try:
        client = docker.from_env()

        container = client.containers.get(container_id)
        container.stop()
    except Exception as e:
        print(e)

def start_docker(container_id=None):
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
    if container_id is None:
        return
    try:
        client = docker.from_env()
    
        container = client.containers.get(container_id)
        container.start()
    except Exception as e:
        print(e)

def remove_docker(container_id=None):
    """
    Function to delete a docker, used if the user decides to delete a button
    
    Keyword arguments:
    container_id : String, optional
    Defaults to None, this can be the dockers id or container name.
    Return: None
    """
    if container_id is None:
        return
    client = docker.from_env()

    try:
        container = client.containers.get(container_id)
        container.stop()
        container.remove(v=True, link=False, force=True)
    except Exception as e:
        print(e)

def get_server_world(container_id = None):

    if container_id is None:
        return
    client = docker.from_env()

    try:
        container = client.containers.get(container_id)
        # Get the requested containers_id tar file
        tar_archive_world = container.get_archive("/data/world")
        # Delete the old server
        #with open("test.tar", "wb") as f: # Used for testing purposes
        #   for x in tar_archive_world[0]:
        #       f.write(x)
        
        #f.close()

    except Exception as e:
        print(e)

def update_server_properties(container_id=None):
    if container_id is None:
        return
    client = docker.from_env()


    try:
        container = client.get_container(container_id)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    make_server()
    #make_server(name="mc-default-2", port=25567)
    #run_docker_mc_command("mc", "/banlist players")
    #stop_docker("mc")  
    #start_docker("mc")  
    #remove_docker("mc")
    #update_server_properties(container_id="mc-default", server_name="lul", max_players=10)
    pass
