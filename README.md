# PSA_CodeSprint_2025_AK_square

## Attili Kireeti Aditya Kumar 
## Alankritha Thiagarajan


## Project Overview
In the PSA CodeSprint 2025, our project focuses on optimizing horizontal transport (HT) operations in a port terminal using an AI-driven scheduling algorithm. By leveraging dynamic job tracking, route optimization, and emissions monitoring, we create a smarter, more efficient operational environment that significantly reduces congestion and operational costs.

## Key Features
- Dynamic Job Scheduling: Efficiently assign jobs to horizontal transports based on real-time metrics.
- Route Optimization: Analyze and select the most efficient paths for transports to minimize travel time and emissions.
- Real-Time Analytics Dashboard: Visualize operational metrics, emissions data, and traffic patterns in real-time.
- CLI and GUI Support: Users can interact with the simulation through both command-line and graphical interfaces for flexibility.

## Implementation Details
Our primary focus was on enhancing the job scheduling logic in src/plan/job_planner.py. We introduced a priority-based algorithm that considers both job urgency and distance, allowing horizontal transports to manage workloads more effectively. Random variables were also integrated to simulate various operational scenarios.

# Installation Instructions
To run our project, please follow these steps:

Set-up Simulation GUI as it was instructed to us and ensure all packages are downloaded. 
    ## One small change is that, replace the requirements.txt file in Simulation GUI and use the one that is provided in our project submission.
    ## Check that you can run cli.py and gui.py for the base case scenario

Next, import the analytics folder in my submission into the src folder in Simulation GUI 
    ## This folder includes the scripts that holds the analytics engine for all the data live-casted onto the dashboard and the dashboard script.  

Next, replace the job_planner.py in the current project's Simulation GUI/src/plan directory with the one we provided in the zip folder
    ## Also add the planning_engine.py file into the plan folder (helper script)

Save all changes. 

## To run and test out program: 
- First open 2 terminals and activate the python environment with all the dependencies downloaded
- On the first terminal run "python dashboard.py"
- On the second terminal run "python cli.py" (For Performance Testing) or "python gui.py" (Recommended for visual assessment)

## And wait for the magic to happen! 
- A folder called analytics_logs will be created under the data folder where all relevant logs can be viewed. IT is safe to delete this folder after each run as each run will append the results in this folder and extract new runtime data for the live dashboard to run. 


### Running the Dashboard
Important: Make sure to run the dashboard in a separate terminal while the simulation is running.


## Metrics for Evaluation
Makespan difference = 1167610 - 1117280 = 50300 (4.31% improvement)
Emission Levels: Minimize CO2 emissions tracked in kg.

## Conclusion
Our project demonstrates the power of combining real-time data analytics with AI-driven optimization algorithms in port operations. We believe our solution can significantly enhance operational efficiency and sustainability in port management systems.

## Acknowledgments
We would like to thank the PSA CodeSprint organizers for this opportunity and the Open Source community for providing resources that made our project possible.


For any questions or comments, please feel free to reach out!

Contact: [KIREETI001@e.ntu.edu.sg] [al0003an@e.ntu.edu.sg]
GitHub: [https://github.com/KIREETI001/PSA_CodeSprint_2025_AK_square]
Demo Link: [(https://youtu.be/lpfCQBCMPIw)]
