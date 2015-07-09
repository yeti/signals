import os.path
import glob

def load_settings(settings_path):
    if not os.path.isdir(settings_path):
        print("Invalid path.  Please specify project path.")
        # TODO: throw exception

    settings_filename = settings_path + os.path.sep + ".signalsconfig"
    settings_filename = os.path.normpath(settings_filename)
    if not os.path.isfile(settings_filename):
        print("Settings file \"{}\" not found.".format(settings_filename))
        # TODO: throw exception

    myvars = {}
    with open(settings_filename) as settings_file:
        for line in settings_file:
            name, var = line.partition("=")[::2]
            myvars[name.strip()] = str(var).rstrip('\n')

    return myvars["schema"], myvars["generator"], myvars["data_models"], myvars["core_data"], myvars["project_name"]


def save_settings(paths, schema, generator_name, data_models, core_data, project_name):
    project_root = find_project_root(paths)
    if len(project_root) > 0:
        output_settings(project_root, schema, generator_name, data_models, core_data, project_name)
    else:
        print("Failed to locate project root")


def find_project_root(paths):
    for curpath in paths:
        #print curpath
        while curpath != os.sep:
            # Check if this path has the .xcodeproj or .xcworkspace files
            if len(glob.glob(curpath + os.sep + "*.xcodeproj")) > 0:
                return curpath
            if len(glob.glob(curpath + os.sep + "*.xcworkspace")) > 0:
                return curpath

            curpath = os.path.normpath(os.path.join(curpath, ".."))
            # print curpath
    return


def output_settings(project_root, schema, generator_name, data_models, core_data, project_name):
    settings_filename = project_root + os.sep + ".signalsconfig"
    print "writing settings to: " + settings_filename
    with open(settings_filename, "w") as settings_file:
        settings_file.write("schema=" + schema.schema_path + "\n")
        settings_file.write("generator=" + generator_name + "\n")
        settings_file.write("data_models=" + data_models + "\n")
        settings_file.write("core_data=" + core_data + "\n")
        settings_file.write("project_name=" + project_name + "\n")

