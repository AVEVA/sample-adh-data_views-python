# Using the Cds Data View Service in Python

**Version:** 1.5.6

[![Build Status](https://dev.azure.com/AVEVA-VSTS/Cloud%20Platform/_apis/build/status%2Fproduct-readiness%2FADH%2FAVEVA.sample-adh-data_views-python?repoName=AVEVA%2Fsample-adh-data_views-python&branchName=main)](https://dev.azure.com/AVEVA-VSTS/Cloud%20Platform/_build/latest?definitionId=16140&repoName=AVEVA%2Fsample-adh-data_views-python&branchName=main)

The sample code in this demonstrates how to invoke the Data View REST API via the sample Python client [library](https://github.com/AVEVA/sample-adh-sample_libraries-python). The sample demonstrates how to establish a connection to SDS, obtain an authorization token, create an SdsType and SdsStream with data (if needed), create a Data View, update it, retrieve it, and retrieve data from it in different ways. At the end of the sample, everything that was created is deleted.

This example uses the adh_sample_library_preview library which is also included in this github repo. It is downloadable via pip.

Developed against Python 3.9.5.

## Running the Sample

1. Clone the GitHub repository
1. Install required modules: `pip install -r requirements.txt`
1. Open the folder with your favorite IDE
1. The sample is configured using the file [appsettings.placeholder.json](appsettings.placeholder.json). Before editing, rename this file to `appsettings.json`. This repository's `.gitignore` rules should prevent the file from ever being checked in to any fork or branch, to ensure credentials are not compromised.
1. Update `appsettings.json` with the credentials provided by AVEVA
1. Run `program.py`

To test the sample after running it:

1. Run `python test.py`

or

1. Install pytest `pip install pytest`
1. Run `pytest program.py`

---

Automated test uses Python 3.9.5 x64

For the main Cds data views samples page [ReadMe](https://github.com/AVEVA/AVEVA-Samples-CloudOperations/blob/main/docs/DATA_VIEWS.md)  
For the main Cds samples page [ReadMe](https://github.com/AVEVA/AVEVA-Samples-CloudOperations)  
For the main AVEVA samples page [ReadMe](https://github.com/AVEVA/AVEVA-Samples)
