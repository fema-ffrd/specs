package main.java.ffrd.hmscontainer.runner;

import hms.model.Project;

public class RunHMS {
    public static void main(String[] args) {
        if (args.length < 2) {
            System.err.println("Error: You must provide both `hmsFilePath` and `simulationName` as command-line arguments.");
            System.exit(1);
        }

        System.out.println("Starting hms-runner");

        String hmsFilePath = args[0];
        String simulationName = args[1];

        System.out.println("Opening project " + hmsFilePath);
        Project project = Project.open(hmsFilePath);

        System.out.println("Preparing to run simulation " + simulationName);
        project.computeRun(simulationName);

        System.out.println("Simulation run completed for " + hmsFilePath);
        project.close();

        System.out.println("Exiting hms-runner");
        System.exit(0);
    }

}