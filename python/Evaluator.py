import os
import shutil

from Evaluation import main as evaluation

amount_counter = 3


def main():
    results_path = os.path.join(os.getcwd(), "..", "documents", "results")
    # create the test folder inside the results folder
    os.makedirs(os.path.join(results_path, "runs"), exist_ok=True)

    runs_path = os.path.join(results_path, "runs")
    for folder in os.listdir(runs_path):
        shutil.rmtree(os.path.join(runs_path, folder))
    for runs in range(amount_counter):
        grafics, precision, recall, f1_score = evaluation()
        print(f"Run {runs + 1} of {amount_counter}")
        print(f"Precision: {precision}")
        print(f"Recall: {recall}")
        print(f"F1-Score: {f1_score}")
        # create a directory one level above in the directory documents in the directory results with the name runs
        # if the directory already exists, the program will not create a new one
        # set the path to the results folder
        os.makedirs(os.path.join(runs_path, str(runs + 1)), exist_ok=True)
        print(f"made directory")
        working_dir = os.path.join(runs_path, str(runs + 1))
        # inside that runs directory make a new directory with the current runs number as the name
        # inside that number directory save the grafics as a svg file

        # I want to save the precision, recall and f1_score as a txt file
        with open(os.path.join(working_dir, "results.txt"), "w") as file:
            file.write(f"Precision: {precision}\nRecall: {recall}\nF1-Score: {f1_score}")
        print(f"saved results")

        # inside the working_dir folder I want to save the grafics as a svg file
        grafics.savefig(os.path.join(working_dir, "grafics.svg"))
        print(f"saved grafics")


if __name__ == '__main__':
    main()
