import click
from signals.parser.schema import Schema
from signals.generators.ios.ios_generator import iOSGenerator
from signals.logging import SignalsError, progress
from signals.settings import save_settings, load_settings, os

generators = {
    'ios': iOSGenerator
}


# Create a separate function so that we can unit test.
# Issues unit testing `main` due to click decorators.
def run_main(schema, generator_name, data_models, core_data, project_name, api_url, save):

    schema = Schema(schema)

    generator = generators[generator_name](schema, data_models, core_data, project_name, api_url)
    try:
        generator.process()
        if save:
            save_settings([data_models, core_data], schema, generator_name, data_models, core_data, project_name,
                          api_url)
    except SignalsError as e:
        print(str(e))
    else:
        progress('Finished generating your files!')


def project_specified(ctx, param, value):
    if not value or (ctx is not None and ctx.resilient_parsing):
        return

    try:
        setting_dict = load_settings(value)
    except SignalsError as e:
        print(str(e))
    else:
        run_main(setting_dict["schema"],
                 setting_dict["generator"],
                 setting_dict["data_models"],
                 setting_dict["core_data"],
                 setting_dict["project_name"],
                 setting_dict["api_url"],
                 False)

    if ctx is not None:
        ctx.exit()


def add_trailing_slash_to_api(ctx, param, value):
    if not value.endswith('/'):
        value += '/'

    return value


def validate_schema_path(ctx, param, value):
    if value.startswith('~'):
        value = os.path.expanduser(value)
    elif value.startswith('.'):
        value = os.path.abspath(value)

    if not os.path.isfile(value):
        raise click.BadParameter("File doesn't exist.", ctx, param)
    else:
        return value


@click.command()
@click.option('settings_path', '--settingspath',
              help='The project path where Signals should look for a .signalsconfig file.  If specified, the contents'
                   ' of the file are used instead of any other specified options',
              type=click.Path(),
              callback=project_specified,
              is_eager=True)
@click.option('--schema',
              prompt='path to api schema file',
              help='The server\'s API schema file.',
              type=click.Path(file_okay=True),
              callback=validate_schema_path)
@click.option('--generator',
              prompt='name of generator to use',
              help='The name of the generator you\'d like to use.',
              type=click.Choice(generators.keys()))
@click.option('data_models', '--datamodels',
              prompt='path to iOS data models',
              help='The location where you\'d like your iOS data model files stored.',
              type=click.Path())
@click.option('core_data', '--coredata',
              help='The location of your core data configuration xcdatamodel file.',
              type=click.Path(exists=True))
@click.option('project_name', '--projectname',
              prompt="name of your iOS project and main target",
              help='The name of your iOS project and main target.',
              type=click.STRING)
@click.option('api_url', '--apiurl',
              prompt='the string url of your api or a method call that returns it',
              help='The fully qualified url of your API for making calls or a method that will return the API, '
                   'ex. Constants.getAPIURL()',
              type=click.STRING,
              callback=add_trailing_slash_to_api)
@click.option('--save', is_flag=True)
# TODO: These are iOS specific settings and we'll need to figure out a way to handle generator specific arguments
# when we add more generators in the future.
def main(settings_path, schema, generator, data_models, core_data, project_name, api_url, save):
    run_main(schema, generator, data_models, core_data, project_name, api_url, save)
