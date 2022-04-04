import time
import os


def dirCreator():
    now = time.localtime(time.time())
    createTime = str(now.tm_mday) + "." + str(now.tm_mon) + "." + str(now.tm_year)
    # Creating directories for excercises
    parent_dir = os.path.abspath(os.getcwd())

    if not os.path.exists(os.path.join(parent_dir, "Bicep")):
        os.mkdir(os.path.join(parent_dir, "Bicep"))

    if not os.path.exists(os.path.join(parent_dir, "Bicep/" + createTime)):
        os.mkdir(os.path.join(parent_dir, "Bicep/" + createTime))

    if not os.path.exists(os.path.join(parent_dir, "Knee")):
        os.mkdir(os.path.join(parent_dir, "Knee"))

    if not os.path.exists(os.path.join(parent_dir, "Knee/" + createTime)):
        os.mkdir(os.path.join(parent_dir, "Knee/" + createTime))

    if not os.path.exists(os.path.join(parent_dir, "Bow")):
        os.mkdir(os.path.join(parent_dir, "Bow"))

    if not os.path.exists(os.path.join(parent_dir, "Bow/" + createTime)):
        os.mkdir(os.path.join(parent_dir, "Bow/" + createTime))


def main():
    print("welcome to the creator. But you shouldn't be here XD")


if __name__ == "__main__":
    main()
