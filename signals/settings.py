from signals.logging import SignalsError, progress
import os.path
import glob


def load_settings(settings_path):
    if not os.path.isdir(settings_path):
        raise SignalsError("Invalid path. Please specify project path.")

    settings_filename = settings_path + os.path.sep + ".signalsconfig"
    settings_filename = os.path.normpath(settings_filename)
    if not os.path.isfile(settings_filename):
        raise SignalsError("Settings file \"{}\" not found.".format(settings_filename))

    setting_dict = {}
    with open(settings_filename) as settings_file:
        for line in settings_file:
            name, var = line.partition("=")[::2]
            setting_dict[name.strip()] = str(var).rstrip('\n')

    return setting_dict


def save_settings(paths, schema, generator_name, data_models, core_data, project_name, api_url):
    project_root = find_project_root(paths)
    if project_root is not None and len(project_root) > 0:
        output_settings(project_root,
                        os.path.abspath(schema.schema_path),
                        generator_name,
                        os.path.abspath(data_models),
                        os.path.abspath(core_data) if core_data else "",
                        project_name,
                        api_url)
    else:
        raise SignalsError("Failed to locate project root")


def find_project_root(paths):
    for current_path in paths:
        if current_path is None or len(current_path) == 0:
            continue

        # Convert to absolute path, in case we received relative path from user
        current_path = os.path.abspath(current_path)
        while current_path != os.sep:
            # Check if this path has the .xcodeproj or .xcworkspace files
            if len(glob.glob(current_path + os.sep + "*.xcodeproj")) > 0:
                return current_path
            if len(glob.glob(current_path + os.sep + "*.xcworkspace")) > 0:
                return current_path

            current_path = os.path.normpath(os.path.join(current_path, ".."))
    return


def output_settings(project_root, schema, generator_name, data_models, core_data, project_name, api_url):
    settings_filename = project_root + os.sep + ".signalsconfig"
    progress("Writing settings to {}".format(settings_filename))
    keys = ["schema", "generator", "data_models", "core_data", "project_name", "api_url"]
    values = [schema, generator_name, data_models, core_data, project_name, api_url]

    with open(settings_filename, "w") as settings_file:
        for (key, val) in zip(keys, values):
            settings_file.write("{}={}\n".format(key, val))
