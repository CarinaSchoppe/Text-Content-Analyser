import os
import re
import shutil

from Evaluation import evaluate as evaluation

amount_counter = 1

single_evaluation = True


def file_saver(runs, grafics, precision, recall, f1_score):
    print("############################################################################################################")
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
    print("############################################################################################################")


results_path = os.path.join(os.getcwd(), "..", "documents", "results")
# create the test folder inside the results folder
os.makedirs(os.path.join(results_path, "runs"), exist_ok=True)
runs_path = os.path.join(results_path, "runs")


def file_evaluator():
    result_files = []
    # go through all results.txt files in the runs folder
    for folder in os.listdir(runs_path):
        folder_path = os.path.join(runs_path, folder)
        for file in os.listdir(folder_path):
            if file == "results.txt":
                # read in the contents of the results.txt file
                with open(os.path.join(folder_path, file), "r") as f:
                    content = f.read()
                # extract the F1-Score as an integer using regular expressions
                f1_score = re.search(r"F1-Score:\s+(\d+)", content).group(1)
                # add the folder name and F1-Score to the result_files list
                result_files.append((folder, int(f1_score)))
    # Print the list of result files and their corresponding folder numbers
    print(result_files)
    best_score = 0
    best_folder = ""

    for folder, score in result_files:
        if score > best_score:
            best_score = score
            best_folder = folder

    print(f"The best F1 score ({best_score}) was found in folder {best_folder}")
    best_folder_path = os.path.join(runs_path, best_folder)
    best_path = os.path.join(runs_path, "best")

    os.makedirs(best_path, exist_ok=True)

    for item in os.listdir(best_folder_path):
        item_path = os.path.join(best_folder_path, item)
        if os.path.isfile(item_path):
            shutil.copy2(item_path, best_path)
        elif os.path.isdir(item_path):
            shutil.copytree(item_path, os.path.join(best_path, item))

    print("Contents of the best run have been copied to the 'best' folder")


def evaluator():
    for folder in os.listdir(runs_path):
        shutil.rmtree(os.path.join(runs_path, folder))
    print("file deletion completed")
    for runs in range(amount_counter):
        grafics, precision, recall, f1_score = evaluation(single_evaluation)
        file_saver(runs, grafics, precision, recall, f1_score)

    file_evaluator()


if __name__ == '__main__':
    evaluator()
