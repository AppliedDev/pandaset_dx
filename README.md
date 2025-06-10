# Data Explorer skeleton interface

## Prerequesites

1. Install docker on a development machine that is [supported by ADP](https://home.applied.co/manual/latest/docs/adp/getting_started/linux).
2. Download a desktop ship of ADP from the [downloads page](https://home.applied.co/downloads/).
3. Have a log file ready that you would like to ingest on your computer.

## Running an initial conversion locally

1. Run your ADP desktop ship. See [ADP docs](https://home.applied.co/manual/adp/v1.40/#/adp_tutorials/01-getting_started/getting_started) for more details.
2. Navigate into this repository and run `docker/build.sh`. This will take several minutes.
3. Run `docker/start.sh --logs ~/path/to/log/directory`, passing in a local directory with your log files that you want to ingest.
4. Obtain your CLI token by following [here](https://home.applied.co/manual/adp/latest/#/apis/rest_api/rest_api?id=authentication-for-desktop-adp).
5. Run `python3 scripts/convert_log_rest.py --rest_api_token {INSERT TOKEN FROM STEP 3}` to run an initial conversion in Data Explorer.
6. Go to <http://localhost:{PORT}/data_explorer/library> to view your converted result.

## Skeleton layout

- `docker`:
  - `docker/build.sh`: A script to build a docker container that your code will run in both locally and in the cloud.
  - `docker/Dockerfile`: Dockerfile that you can customize to install more 3rd party libraries into your image.
  - `docker/start.sh`: A script to start the docker container that was built so it will run locally, allowing you to iterate on your converter locally.
    Running this script with the `--logs` flag like `docker/start.sh --logs ~/path/to/log/directory` mounts the contents of that directory into the `/logs/` directory in the docker container.
    This allows you to iterate without needing to implement downloading logic for your initial implementation.
  - `docker/remove.sh`: A script to remove the docker container.
  - `docker/variables.sh`: This holds the default container name of your interface.
- `interface`:
  - `interface/plugins`:
    - `interface/plugins/export.py`: Class that holds implementations for your exporting logic.
    - `interface/plugins/plugin_service.py`: Script to run the plugin service.
  - `interface/constants.py`: A file to contain shared constants, such as the name of the channels you send to ADP.
  - `interface/data_sender.py`: A class that allows you to send data to ADP. This should be initialized in `log_converter.py` and passed into the log readers/channel handlers that send drawings or data points.
  - `interface/log_converter.py`: The main python class that implements the main conversion. Running this file runs the GRPC server that ADP communicates with to get your data.
  - `interface/log_readers/`: Placeholder log readers that send arbitrary data to ADP.
  - `interface/channel_handlers/`: Placeholder channel handlers that convert data to ADP format.
  - `interface/mailbox.py`: Class to hold shared state.
- `scripts`:
  - `scripts/convert_drive_rest.py`: This is a sample script that will allow you to run a conversion in your running ADP instance programmatically.
    Run this script with `python3 scripts/convert_log_rest.py --rest_api_token <>` where your REST API token can be obtained [here](https://home.applied.co/manual/adp/latest/#/apis/rest_api/rest_api?id=authentication-for-desktop-adp).
- `run_tests.sh`: Run tests for the interface.
- `run_typing.sh`: Run mypy to check that python type annotations are consistent.

## Writing your initial integration

This skeleton is structured to guide you towards separating out logic for reading your logs and transforming your logs into separate modules.

- A `LogReader` should be implemented for each data source you want to read from. It's responsible for iterating through the data and yielding the relevant data you are interested in.
- A `ChannelHandler` should be implemented for each channel you want to send to ADP. This is the module that is responsible for performing conversion to ADP.
  If data from multiple logs are used in one ADP channel, the channel handler can use the mailbox to access that shared state.

### Interface development tips

Here are some tips to minimize your iteration cycles.

1. Write a log reader for each log source.
   You should test that your log sources parses data out properly by writing a test that just runs that log reader and ensures that the data is correct.
2. Write a channel handler for each channel that converts your data into the ADP format.
3. Register your log readers and channel handlers in `log_converter.py`
4. Edit `log_converter_test.py` to read your test log and edit the number of messages you expect to receive.
5. Test that your whole interface is working properly by running `./run_tests.sh`.
6. Run your conversion in ADP locally.
7. Run your conversion in the cloud.

## Extending your initial integration

In order to get your conversion running in the cloud, you'll need to implement the `open` method in the log readers to download from your cloud storage.
