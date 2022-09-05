# Just Hungry



## Installation

The packages below are required in order to run the program.

```bash
pip3 install Pyro4
pip3 install requests
```

## Usage
All of my code has been written in Python 3.7.5 and run on linux.
To run first create a name server by running:
```bash
python3 -m Pyro4.naming
```
in a terminal window. Next for each replica you would like to create run:
```bash 
python3 just_hungry_back.py
```
whilst in gltc66_Just_Hungry/Back_End in a separate terminal window i.e for 3 replicas run it in 3 terminal windows. The next stages require opening terminal windows in gltc66_Just_Hungry/Front_End. 

In one window run:
```bash
python3 just_hungry_front.py
```
In another run:
```bash
python3 just_hungry_client.py
```

To use the program then simply follow the on screen instructions that can be seen in the last window. For multiple concurrent client programs simply run just_hungry_client.py in multiple windows.

To terminate the replicas and test the system simply enter ctrl+c in the window of the replica you would like to terminate.


## Functionality and Structure

### Client Program
Simply takes command line input, makes requests to the front end and then provides relevant output to the user. It stores a client ID in a variable to support the retrieval of data. This ID is lost when the program is exited.


### Front End Program
The front end simply takes requests made by the client and forwards them to the current primary server. When starting if a primary cannot be found, the front end creates a view by identifying all back ups on the name server. It then sends this view to each replica in the view itself, the replicas are then capable of choosing a new primary that the front end will be able to access. 

In later instances if the primary can not be found or is thought to have crashed the same process takes place except the view used is that provided by the primary in its last response, before it crashed. This ensures that all back ups in the view will be up to date with the correct data. 

For this same reason if all replicas are destroyed then the front end will not broadcast to any new replicas created as they will not contain the necessary data. Therefore to carry on using the front end it must be restarted, along with the client program.

### Back End Program
The back end consists of all the replicas and each's respective data store. The replicas are responsible for assigning a new primary if one is not present, communicating with the web api's, managing all data, maintaining a consist view among all replicas and facilitate new replicas being added at any point during their life cycle. 

## License
[MIT](https://choosealicense.com/licenses/mit/)
