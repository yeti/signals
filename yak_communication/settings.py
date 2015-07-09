from yak_communication.logging import SignalsError
import os.path
import glob

def load_settings(settings_path):
    if not os.path.isdir(settings_path):
        raise SignalsError("Invalid path.  Please specify project path.")

    settings_filename = settings_path + os.path.sep + ".signalsconfig"
    settings_filename = os.path.normpath(settings_filename)
    if not os.path.isfile(settings_filename):
        raise SignalsError("Settings file \"{}\" not found.".format(settings_filename))

    myvars = {}
    with open(settings_filename) as settings_file:
        for line in settings_file:
            name, var = line.partition("=")[::2]
            myvars[name.strip()] = str(var).rstrip('\n')

    return myvars["schema"], myvars["generator"], myvars["data_models"], myvars["core_data"], myvars["project_name"]


def save_settings(paths, schema, generator_name, data_models, core_data, project_name):
    project_root = find_project_root(paths)
    if project_root is not None and len(project_root) > 0:
        output_settings(project_root, schema, generator_name, data_models, core_data, project_name)
    else:
        raise SignalsError("Failed to locate project root")


def find_project_root(paths):
    for curpath in paths:
        if curpath is None or len(curpath) == 0:
            continue

        # Convert to absolute path, in case we received relative path from user
        curpath = os.path.abspath(curpath)
        while curpath != os.sep:
            # Check if this path has the .xcodeproj or .xcworkspace files
            if len(glob.glob(curpath + os.sep + "*.xcodeproj")) > 0:
                return curpath
            if len(glob.glob(curpath + os.sep + "*.xcworkspace")) > 0:
                return curpath

            curpath = os.path.normpath(os.path.join(curpath, ".."))
    return


def output_settings(project_root, schema, generator_name, data_models, core_data, project_name):
    settings_filename = project_root + os.sep + ".signalsconfig"
    print "Writing settings to " + settings_filename
    with open(settings_filename, "w") as settings_file:
        settings_file.write("schema=" + (os.path.abspath(schema.schema_path) if not (schema.schema_path is str) else "") + "\n")
        settings_file.write("generator=" + (generator_name if not (generator_name is str) else "") + "\n")
        settings_file.write("data_models=" + (os.path.abspath(data_models) if not (data_models is str) else "") + "\n")
        settings_file.write("core_data=" + (os.path.abspath(core_data) if not (core_data is None) else "") + "\n")
        settings_file.write("project_name=" + (project_name if not (project_name is None) else "") + "\n")
