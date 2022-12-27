import docker 
import os
import tarfile
from configparser import ConfigParser
import threading

def make_server(return_container=False, name="mc-default", port=25565, max_players=20, gamemode="survival", threaded=True):
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
    # TODO: fail if the name is already taken and return something appropriate.
    try:    
        client = docker.from_env() 
        mc_server_container = client.containers.run(image="itzg/minecraft-server", detach=True, ports={"25565":f"{port}"}, name=f"{name}", environment=["EULA=True"])

        if not mc_server_container:
            raise Exception("Docker is not running!")

        if threaded:
            # Start a threaded process to go ahead and read the mc_server_loggin info
            thread_x = threading.Thread(target=server_create, args=(mc_server_container, max_players, gamemode,), name="thread")
            thread_x.start()
        else:
            # A non threaded run useful for testing purposes
            server_create(mc_server_container, max_players, gamemode)

        if return_container:
            return mc_server_container
        else:
            return mc_server_container.id
    except Exception as e:
        print(e)
        return None


def server_create(mc_server_container, max_players, gamemode):
    attached = mc_server_container.attach(stream=True, stdout=True, stderr=False, logs=False)

    # Looking for a certain string to signal that the mc_server has started
    for console_output in attached:
        if "RCON running on" in console_output.decode():
            attached.close()
            break

    update_server_properties(container_id=mc_server_container.id, updated_properties={"difficulty": "hard", "max-players": str(max_players), "motd":"ITS ALIVE", "gamemode": str(gamemode)}, init_properties=True)


def update_server_properties(container_id="mc-default", updated_properties={}, init_properties=False):
    """
    Function to update an existing minecraft server.
    Parameters
    ----------
    container_id : String
        Default to 'mc-default', name of the docker container
    updated_properties: Dict
        Key value pairs of all the settings wished to be updated
    init_properties: False
        DO NOT USED THIS, ONLY NEEDS TO BE USED FROM THE MAKE SERVER CALL
        Makes server.properties the first time into a file type similar to .ini
    Returns
    -------
    String
        Id of the docker container that was created using this function
    """
    if container_id == None:
        return False
    client = docker.from_env()
    container = client.containers.get(container_id)

    # Get the server properties from the container
    tar_archive_server_properties = container.get_archive("/data/server.properties", encode_stream=False)
    
    tar_file = f"server_properties_{container_id}.tar"

    with open(tar_file, "wb") as f: # Used for testing purposes
       for x in tar_archive_server_properties[0]:
           f.write(x)
    f.close()

    if tarfile.is_tarfile(f.name):
        print("[INFO] Succesfully recieved server tar archive")
    else:
        print("Failed to find server properties tar archive")
        return False
    
    # Un tar it
    server_tar_file = tarfile.TarFile(name=tar_file)
    buffer = server_tar_file.extractfile('server.properties')
    
    # Editing the server.properties file
    server_properties_content = buffer.read().decode()
    server_tar_file.close() # We have the buffer now and now we can close the tarfile connection
    os.remove(tar_file)

    # This is needed for the configparser, it converts it to a more .ini type config system
    string_content = ""    
    if not init_properties:
        string_content = server_properties_content
    else:
        string_content = "[root]\r\n" + server_properties_content


    configparser = ConfigParser()
    configparser.read_string(string_content)

    for key in updated_properties:
        if configparser["root"].get(key) == None:
            return False

    for key in updated_properties:
        configparser["root"][key] = updated_properties[key]
    
    with open("server.properties", "w") as config_file:
        configparser.write(config_file)
    
    
    # write the new server.properties tar archieve that is going to be sent to the docker container
    tar_file_new = tarfile.open(f"server_properties_{container_id}.tar", "w")
    tar_file_new.add(config_file.name)
    tar_file_new.close()

    os.remove("server.properties")

    # get the archive byte info
    archive_file_to_send = open(tar_file, "rb")
    data = archive_file_to_send.read()
    archive_file_to_send.close()
    
    container.put_archive("/data", data)
    
    os.remove(tar_file)
    
    container.restart()
    
    print("[INFO] Succesfully updated the server properties\n")
    # Close the socket

    return True

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
        return True
    except Exception as e:
        print(e)
        return False

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
        return True
    except Exception as e:
        print(e)
        return False

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
        return True
    except Exception as e:
        print(e)
        return False

# TODO: Finish getting the world folder
def get_server_world(container_id = None):
    """
    Function to collect the mc servers world files

    Parameters
    ----------
    container_id: String
    Default to None, used to specify the which containers world to grab
    """

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


if __name__ == "__main__":
    #cdmake_server()
    #make_server()
    #run_docker_mc_command("mc", "/banlist players")
    #stop_docker("mc")  
    #start_docker("mc")  
    #remove_docker("mc") 
    #update_server_properties(key="max-players", value="50") 
    #update_server_properties(key="motd", value="Test MOTD")
    #update_server_properties(key="pvp", value="False")
    pass

